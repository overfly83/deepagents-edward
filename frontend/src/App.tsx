import { useState, useEffect, useRef } from 'react';
import './index.css';

// Define a simple logging utility
const logger = {
  info: (message: string, ...args: any[]) => console.info('[App]', message, ...args),
  debug: (message: string, ...args: any[]) => console.debug('[App]', message, ...args),
  warn: (message: string, ...args: any[]) => console.warn('[App]', message, ...args),
  error: (message: string, ...args: any[]) => console.error('[App]', message, ...args)
};

interface Message {
  text: string;
  isUser: boolean;
  isDebug?: boolean;
  isProcess?: boolean;
}

const MessageItem = ({ message, isUser, isDebug, isProcess }: { message: string; isUser: boolean; isDebug?: boolean; isProcess?: boolean }) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-fade-in`}>
      <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${isDebug 
        ? 'bg-blue-100 text-blue-800 border-l-4 border-blue-500' 
        : isProcess
        ? 'bg-gray-100 text-gray-500' 
        : isUser 
        ? 'bg-indigo-500 text-white' 
        : 'bg-gray-200 text-gray-800'}`}>
        {message}
      </div>
    </div>
  );
};

const TypingIndicator = () => {
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected');
  const messageContainerRef = useRef<HTMLDivElement>(null);

  // State for streaming
  const [useStreaming, setUseStreaming] = useState(true);
  const [, setIsReceivingChunks] = useState(false);

  // Initialize WebSocket connection
  useEffect(() => {
    logger.info('Component mounted, initializing WebSocket connection');
    
    // Generate a unique session ID for this user
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    logger.debug('Generated session ID:', newSessionId);

    // Create WebSocket connection (hardcoded URL for testing)
    const wsUrl = `ws://localhost:8000/ws/${newSessionId}`;
    logger.info('Attempting to connect WebSocket:', wsUrl);
    
    try {
        const websocket = new WebSocket(wsUrl);
        setWs(websocket);
        
        websocket.onopen = () => {
        setConnectionStatus('connected');
        logger.info('WebSocket connected');
        // Add welcome message
        setMessages(prev => [...prev, { text: 'Hello! I\'m a weather assistant. How can I help you today?', isUser: false }]);
      };
      
      websocket.onmessage = (event) => {
        logger.debug('WebSocket message received:', event.data);
        try {
          const data = JSON.parse(event.data);
          logger.debug('Parsed message:', data);
          
          if (data.type === 'chunk') {
            logger.debug('Received chunk:', data.content);
            setIsReceivingChunks(true);
            // Append chunk to the last message only if we're already receiving chunks
            setMessages(prev => {
              const newMessages = [...prev];
              if (newMessages.length > 0 && !newMessages[newMessages.length - 1].isUser && !newMessages[newMessages.length - 1].isProcess) {
                newMessages[newMessages.length - 1].text += data.content;
              } else {
                newMessages.push({ text: data.content, isUser: false });
              }
              return newMessages;
            });
          } else if (data.type === 'complete') {
            logger.debug('Received complete message:', data.content);
            // setMessages(prev => {
            //   // Only update the last message if we're receiving chunks
            //   if (isReceivingChunks && prev.length > 0 && !prev[prev.length - 1].isUser && !prev[prev.length - 1].isProcess) {
            //     const newMessages = [...prev];
            //     newMessages[newMessages.length - 1].text = data.content;
            //     return newMessages;
            //   }
            //   // Otherwise append as new message
            //   return [...prev, { text: data.content, isUser: false }];
            // });
            setIsReceivingChunks(false);
            setIsTyping(false);
          } else if (data.type === 'debug') {
            logger.debug('Received debug message:', data);
            // Always append debug messages as new messages, never merge with chunks
            setIsReceivingChunks(false);
            // Display process information line by line in gray font
            if (data.intent) {
              setMessages(prev => [...prev, { text: `Detected intent: ${data.intent}`, isUser: false, isProcess: true }]);
            }
            if (data.message) {
              setMessages(prev => [...prev, { text: `Processing message: ${data.message}`, isUser: false, isProcess: true }]);
            }
            if (data.agent) {
              setMessages(prev => [...prev, { text: `Selected agent: ${data.agent}`, isUser: false, isProcess: true }]);
            }
            if (data.workflow_step) {
              setMessages(prev => [...prev, { text: `Workflow step: ${data.workflow_step}`, isUser: false, isProcess: true }]);
            }
            if (data.step_name) {
              setMessages(prev => [...prev, { text: `Current step: ${data.step_name}`, isUser: false, isProcess: true }]);
            }
            if (data.step_description) {
              setMessages(prev => [...prev, { text: `Step description: ${data.step_description}`, isUser: false, isProcess: true }]);
            }
            if (data.task_plan) {
              setMessages(prev => [...prev, { text: `Task plan: ${JSON.stringify(data.task_plan)}`, isUser: false, isProcess: true }]);
            }
          } else if (data.type === 'status') {
            logger.info('Status message received:', data.message);
          } else if (data.type === 'error') {
            logger.error('Error message received:', data.message);
            setMessages(prev => [...prev, { text: `Error: ${data.message}`, isUser: false }]);
            setIsTyping(false);
          } else {
            logger.warn('Unknown message type received:', data.type);
          }
        } catch (error) {
          logger.error('Error processing WebSocket message:', error);
          setMessages(prev => [...prev, { text: `Error processing message: ${error}`, isUser: false }]);
          setIsTyping(false);
        }
      };
      
      websocket.onclose = (event) => {
        setConnectionStatus('disconnected');
        logger.info('WebSocket disconnected:', event.code, event.reason);
        setMessages(prev => [...prev, { text: 'Connection to server lost. Please refresh the page to try again.', isUser: false }]);
      };
      
      websocket.onerror = (error) => {
        setConnectionStatus('error');
        logger.error('WebSocket error:', error);
        setMessages(prev => [...prev, { text: `Connection error: ${JSON.stringify(error)}`, isUser: false }]);
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
      setMessages(prev => [...prev, { text: `Failed to create WebSocket connection: ${error}`, isUser: false }]);
    }
  }, []);

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
    
    // Add user message
    setMessages(prev => [...prev, { text: inputValue, isUser: true }]);
    
    // Send message to server
    ws.send(JSON.stringify({ message: inputValue, use_streaming: useStreaming }));
    
    // Clear input and show typing indicator
    setInputValue('');
    setIsTyping(true);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center">
            <i className="fas fa-cloud-sun text-indigo-500 text-2xl mr-3"></i>
            <h1 className="text-xl font-semibold text-gray-800">Weather Assistant</h1>
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
            {messages.length === 0 && (
              <div className="text-center text-gray-500 mt-8">
                <i className="fas fa-comments text-4xl mb-4"></i>
                <p>Hello! I'm a weather assistant that can help you check weather information.</p>
                <p className="mt-2">Try asking: "What's the weather like in Shanghai today?"</p>
              </div>
            )}
            {messages.map((message, index) => (
              <MessageItem 
                key={index} 
                message={message.text} 
                isUser={message.isUser} 
                isDebug={message.isDebug} 
                isProcess={message.isProcess} 
              />
            ))}
            {isTyping && <TypingIndicator />}
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

export default App;