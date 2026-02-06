import os
import sys
import asyncio
import json
import argparse
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from utils.logger import get_logger
import uvicorn

logger = get_logger(__name__, source="server")

# Add project root to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(os.path.dirname(current_dir))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from agents.agent_manager import AgentManager

# Create FastAPI app
app = FastAPI(title='DeepAgents Demo API', description='API for weather agent demo', version='1.0.0')

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Allow all origins for demo purposes
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Pydantic models
class WeatherRequest(BaseModel):
    location: str
    date: Optional[str] = None
    additional_info: Optional[str] = None

class ChatMessage(BaseModel):
    role: str
    content: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Server is running"
    }

# Route inspection endpoint to debug endpoint registration
@app.get("/routes")
async def list_routes():
    """List all registered routes for debugging purposes"""
    routes = []
    for route in app.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": list(route.methods) if hasattr(route, "methods") else None,
            "type": type(route).__name__
        })
    return {
        "routes": routes,
        "count": len(routes)
    }

class DebugInfo(BaseModel):
    intent: Optional[str] = None
    message: Optional[str] = None
    agent: Optional[str] = None
    workflow_step: Optional[str] = None
    task_plan: Optional[Any] = None
    step_number: Optional[int] = None
    step_name: Optional[str] = None
    step_description: Optional[str] = None

class WebSocketConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

# Initialize connection manager
manager = WebSocketConnectionManager()

# Initialize agent manager at module level for API endpoints
agent_manager = AgentManager()

@app.websocket('/ws/{session_id}')
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    logger.info(f"WebSocket connection attempt received from {websocket.client} for session: {session_id}")
    
    try:
        await manager.connect(websocket)
        logger.info(f"WebSocket connection accepted for session: {session_id}")
        
        # Send welcome message
        welcome_msg = {"type":"status","message":"Connected with session ID: " + session_id}
        await websocket.send_json(welcome_msg)
        logger.info(f"Sent welcome message for session: {session_id}")
        
        while True:
            # Receive raw text data
            try:
                data = await websocket.receive_text()
                logger.info(f"Received message from session {session_id}: {data[:200]}...")
            except WebSocketDisconnect:
                manager.disconnect(websocket)
                logger.info(f"WebSocket connection disconnected for session: {session_id}")
                break
            
            try:
                # Parse JSON message
                message_data = json.loads(data)
                user_message = message_data.get('message', '')
                use_streaming = message_data.get('use_streaming', False)
                
                if not user_message:
                    error_msg = {"type":"error","message":"Message is required"}
                    await websocket.send_json(error_msg)
                    logger.warning(f"Empty message received from session {session_id}")
                    continue
                
                # Send processing status
                processing_msg = {"type":"status","message":"Processing your request..."}
                await websocket.send_json(processing_msg)
                logger.info(f"Sent processing status to session {session_id}")
                
                if use_streaming:
                    # Use streaming mode
                    try:
                        # Initialize response buffer
                        full_response = ""
                        await websocket.send_json({"type":"debug","message":"weather agent streaming started..."})
                        # Process message with agent manager in streaming mode
                        for chunk in agent_manager.stream_handle_message(user_message):
                            logger.debug(f"Received chunk: {chunk}")
                            
                            # Handle different message types
                            if "type" in chunk and "content" in chunk:
                                msg_type = chunk["type"]
                                content = chunk["content"]
                                
                                # Send the chunk with its type to frontend
                                await websocket.send_json(chunk)
                                logger.info(f"Sent {msg_type} to session {session_id}: {content[:100]}...")
                                
                                # Update full_response only for actual content chunks
                                if msg_type == "chunk":
                                    if full_response == "":
                                        full_response = content
                                    elif content.startswith(full_response):
                                        full_response = content
                                    else:
                                        full_response += content
                        
                        # Send complete response after streaming
                        await websocket.send_json({"type": "complete", "content": "query complete."})
                    except Exception as stream_error:
                        # Fall back to non-streaming mode if streaming fails
                        logger.error(f"Streaming error: {stream_error}")
                        # Process message with agent manager with step-by-step updates in fallback mode
                        final_result = None
                        
                        # Use the generator version to get step-by-step updates
                        for step_data in agent_manager.handle_message(user_message, return_steps=True):
                            if step_data.get("type") == "complete":
                                # This is the final result
                                final_result = step_data["result"]
                            else:
                                # This is a workflow step, send as debug message with step info
                                if "debug" in step_data:
                                    debug_info = step_data["debug"]
                                    # Create DebugInfo model instance with step details
                                    debug_model = DebugInfo(
                                        step_number=step_data["step_number"],
                                        step_name=step_data["step_name"],
                                        step_description=step_data["step_description"],
                                        **debug_info
                                    )
                                    # Convert to dict, excluding None values
                                    debug_dict = debug_model.dict(exclude_none=True)
                                    # Add type field
                                    debug_msg = {
                                        "type": "debug",
                                        **debug_dict
                                    }
                                    await websocket.send_json(debug_msg)
                                    logger.debug(f"Sent step message (fallback): {json.dumps(debug_msg)}")
                        
                        # Send complete response
                        if final_result:
                            await websocket.send_json({"type":"complete","content": final_result["response"]})
                else:
                    # Use non-streaming mode
                    result = agent_manager.handle_message(user_message)
                    if isinstance(result, dict):
                        if "debug" in result:
                            debug_info = result["debug"]
                            # Create DebugInfo model instance
                            debug_model = DebugInfo(**debug_info)
                            # Convert to dict, excluding None values
                            debug_dict = debug_model.dict(exclude_none=True)
                            # Add type field
                            debug_msg = {
                                "type": "debug",
                                **debug_dict
                            }
                            await websocket.send_json(debug_msg)
                        
                        # Send plan if it exists
                        if "plan" in result:
                            await websocket.send_json({"type": "plan", "content": result["plan"]})
                            logger.info(f"Sent plan to session {session_id}")
                        
                        # Send complete response
                        await websocket.send_json({"type":"complete","content": result["response"]})
                    else:
                        # Handle string response
                        await websocket.send_json({"type":"complete","content": result})
                    
            except json.JSONDecodeError as e:
                error_msg = {"type":"error","message":"Invalid JSON format"}
                await websocket.send_json(error_msg)
                logger.error(f"JSON decode error from session {session_id}: {e}")
            except Exception as e:
                error_msg = {"type":"error","message":"Unexpected error: " + str(e)}
                await websocket.send_json(error_msg)
                logger.error(f"Unexpected error processing message from session {session_id}: {e}")
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        logger.error(f"Unexpected WebSocket error for session {session_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    finally:
        logger.info(f"WebSocket connection closed for session: {session_id}")

@app.post('/api/weather')
async def get_weather(request: WeatherRequest):
    """Get weather forecast for a specific location"""
    try:
        result = await agent_manager.run_agent(
            "weather",
            location=request.location,
            date=request.date,
            additional_info=request.additional_info
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/')
async def root():
    """Root endpoint - serve frontend"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {'message': 'Static files not found. Please build the frontend first.'}

if __name__ == '__main__':
    # Initialize agent manager with debug mode
    
    agent_manager = AgentManager()
    
    # Parse command line arguments only when running directly
    parser = argparse.ArgumentParser(description='Weather Assistant Backend Server')
    # Use a different approach that allows us to check if the argument was explicitly provided
    parser.add_argument('--debug', action='store_true', default=None, help='Enable debug mode')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run on')
    parser.add_argument('--port', default=8000, type=int, help='Port to run on')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    parser.add_argument('--log-level', default='debug', help='Log level')
    args = parser.parse_args()
    
    # Check if --debug flag was explicitly provided
    debug_flag_provided = any('--debug' in arg for arg in sys.argv)
    
    # Set debug mode - prioritize command line args, then environment variable
    if debug_flag_provided:
        agent_manager.debug_mode = args.debug
    
    logger.info(f"Starting server, debug mode: {agent_manager.debug_mode}, log level: {args.log_level}")
    
    uvicorn.run(
        'agents.server:app',
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )