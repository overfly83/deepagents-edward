import { useState, useEffect, useRef } from 'react';
import './index.css';
import { useDecoupledTypingEffect } from './hooks/useDecoupledTypingEffect';
import { MessageManager } from './components/MessageManager';

// Define a simple logging utility
const logger = {
  info: (message: string, ...args: any[]) => console.info('[AppDecoupled]', message, ...args),
  debug: (message: string, ...args: any[]) => console.debug('[AppDecoupled]', message, ...args),
  warn: (message: string, ...args: any[]) => console.warn('[AppDecoupled]', message, ...args),
  error: (message: string, ...args: any[]) => console.error('[AppDecoupled]', message, ...args)
};

// Define the message data structure for all types
interface Message {
  type: string;
  content: string;
}

type MessageData = Message[];

function AppDecoupled() {
  // State for all message types - now using an array to preserve order
  const [messages, setMessages] = useState<MessageData>([]);
  
  const [inputValue, setInputValue] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected');
  const messageContainerRef = useRef<HTMLDivElement>(null);
  const [hasSentMessage, setHasSentMessage] = useState(false);

  // State for streaming
  const [useStreaming, setUseStreaming] = useState(true);

  // Initialize WebSocket connection
  useEffect(() => {
    logger.info('Component mounted, initializing WebSocket connection');
    
    // Generate a unique session ID for this user
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    logger.debug('Generated session ID:', newSessionId);

    // Create WebSocket connection (hardcoded URL for testing)
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsHost = window.location.host;
    const wsUrl = `${wsScheme}://${wsHost}/ws/${newSessionId}`;
    logger.info('Attempting to connect WebSocket:', wsUrl);
    
    try {
      const websocket = new WebSocket(wsUrl);
      setWs(websocket);
      
      websocket.onopen = () => {
        setConnectionStatus('connected');
        logger.info('WebSocket connected');
        // Add welcome message
        setMessages(prev => [...prev, {
          type: 'default',
          content: 'Hello! I\'m DeepAgents, your AI assistant. How can I help you today?'
        }]);
      };
      
      websocket.onmessage = (event) => {
        logger.debug('WebSocket message received:', event.data);
        try {
          const data = JSON.parse(event.data);
          logger.debug('Parsed message:', data);
          
          // Handle different message types with appropriate formatting and typing effect
          if (data.type === 'chunk' || data.type === 'thought' || data.type === 'tool_call' || 
              data.type === 'tool_response' || data.type === 'result' || data.type === 'error' ||
              data.type === 'process' || data.type === 'default' || data.type === 'plan' || 
              data.type === 'todo') {
            logger.debug(`Received ${data.type}:`, data.content);
            
            // Route message to appropriate container based on type
            const messageType = data.type === 'chunk' ? 'default' : data.type;
            addChunk(data.content, messageType);
          } else if (data.type === 'complete') {
            logger.debug('Received complete message:', data.content);
            completeStreaming(data.message_type || 'default');
          } else if (data.type === 'debug') {
            logger.debug('Received debug message:', data);
            // Display debug messages in the process container
            addChunk(`Debug: ${JSON.stringify(data)}`, 'process');
          } else if (data.type === 'status') {
            logger.info('Status message received:', data.message);
            addChunk(data.message, 'process');
          } else {
            logger.warn('Unknown message type received:', data.type);
            // Default to the default container for unknown types
            setMessages(prev => [...prev, {
              type: 'default',
              content: `Unknown message type: ${JSON.stringify(data)}`
            }]);
          }
        } catch (error) {
          logger.error('Error processing WebSocket message:', error);
          setMessages(prev => [...prev, {
            type: 'error',
            content: `Error processing message: ${error}`
          }]);
        }
      };
      
      websocket.onclose = (event) => {
        setConnectionStatus('disconnected');
        logger.info('WebSocket disconnected:', event.code, event.reason);
        setMessages(prev => [...prev, {
          type: 'error',
          content: 'Connection to server lost. Please refresh the page to try again.'
        }]);
      };
      
      websocket.onerror = (error) => {
        setConnectionStatus('error');
        logger.error('WebSocket error:', error);
        setMessages(prev => [...prev, {
          type: 'error',
          content: `Connection error: ${JSON.stringify(error)}`
        }]);
      };

      // Cleanup on unmount
      return () => {
        if (websocket) {
          logger.info('Component unmounted, closing WebSocket connection');
          websocket.close();
        }
      };
    } catch (error) {
      logger.error('Error creating WebSocket:', error);
      setConnectionStatus('error');
      setMessages(prev => [...prev, {
        type: 'error',
        content: `Failed to create WebSocket connection: ${error}`
      }]);
    }
  }, []);

  // Use the decoupled typing effect hook
  const { 
    addChunk, 
    completeStreaming, 
    resetStreaming, 
    startStreamingSession,
    activeType,
    isWaitingForNextType,
    waitingType
  } = useDecoupledTypingEffect({
    onMessagesUpdate: setMessages
  });

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messageContainerRef.current) {
      messageContainerRef.current.scrollTop = messageContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || !ws || connectionStatus !== 'connected') return;
    
    // Reset streaming state before new request
    resetStreaming();
    startStreamingSession();
    setHasSentMessage(true);
    
    // Add user message
    setMessages(prev => [...prev, {
      type: 'user',
      content: inputValue
    }]);
    
    // Send message to server
    ws.send(JSON.stringify({ message: inputValue, use_streaming: useStreaming }));
    
    // Clear input and show typing indicator
    setInputValue('');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center">
            <i className="fas fa-robot text-indigo-500 text-2xl mr-3"></i>
            <h1 className="text-xl font-semibold text-gray-800">DeepAgents AI - Decoupled Messages</h1>
          </div>
          <div className="flex items-center">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              connectionStatus === 'connected' 
              ? 'bg-green-100 text-green-800' 
              : connectionStatus === 'error'
              ? 'bg-red-100 text-red-800'
              : 'bg-gray-100 text-gray-800'
            }`}>
              <span className={`w-2 h-2 mr-1 rounded-full ${
                connectionStatus === 'connected' 
                ? 'bg-green-400' 
                : connectionStatus === 'error'
                ? 'bg-red-400'
                : 'bg-gray-400'
              }`}></span>
              {connectionStatus === 'connected' ? 'Connected' : 
               connectionStatus === 'error' ? 'Connection Error' : 'Disconnected'}
            </span>
          </div>
        </div>
      </header>

      {/* Chat container */}
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 py-6 chat-container">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col">
          {/* Messages */}
          <div className="flex-1 p-4 message-container" ref={messageContainerRef}>
            <MessageManager 
              messages={messages}
              activeType={activeType}
              isWaiting={hasSentMessage && isWaitingForNextType}
              waitingType={waitingType}
            />
          </div>

          {/* Input form */}
          <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4">
            <div className="flex items-center mb-3">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={useStreaming}
                  onChange={(e) => setUseStreaming(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                <span className="ml-3 text-sm font-medium text-gray-700">Use streaming</span>
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter your question..."
                className="flex-1 border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                disabled={connectionStatus !== 'connected'}
              />
              <button
                type="submit"
                disabled={!inputValue.trim() || connectionStatus !== 'connected'}
                className="bg-indigo-500 text-white px-4 py-2 rounded-r-lg hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                <i className="fas fa-paper-plane"></i>
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

export default AppDecoupled;
