import { useRef, useState } from 'react';

// Define typing speed settings (characters per second)
const MIN_TYPING_SPEED = 50;
const MAX_TYPING_SPEED = 120;

// Interface for a single message
interface Message {
  type: string;
  content: string;
}

interface DecoupledTypingEffectConfig {
  onMessagesUpdate: (updater: (prevMessages: Message[]) => Message[]) => void;
}

interface DecoupledTypingEffectReturn {
  addChunk: (chunk: string, type: string) => void;
  completeStreaming: (type: string) => void;
  startStreamingSession: () => void;
  resetStreaming: () => void;
  isReceivingChunks: boolean;
  activeType: string | null;
  isWaitingForNextType: boolean;
  waitingType: string | null;
}

interface StreamingBuffer {
  content: string;
  type: string;
  messageIndex: number;
}

export const useDecoupledTypingEffect = ({ onMessagesUpdate }: DecoupledTypingEffectConfig): DecoupledTypingEffectReturn => {
  const [isReceivingChunks, setIsReceivingChunks] = useState(false);
  const [activeType, setActiveType] = useState<string | null>(null);
  const [isWaitingForNextType, setIsWaitingForNextType] = useState(false);
  const [waitingType, setWaitingType] = useState<string | null>(null);
  
  // Stream buffer stores chunks that are waiting to be processed
  const streamBufferRef = useRef<StreamingBuffer[]>([]);
  const activeTypeRef = useRef<string | null>(null);
  const lastTypeRef = useRef<string | null>(null);
  const currentOpenTypeRef = useRef<string | null>(null);
  const currentOpenMessageIndexRef = useRef<number | null>(null);
  const sessionActiveRef = useRef(false);
  const isStreamingCompleteRef = useRef(false);
  
  // Track current message being typed for each type
  const currentMessageIndicesRef = useRef<Record<string, number | null>>({
    thought: null,
    tool_call: null,
    tool_response: null,
    plan: null,
    todo: null,
    result: null,
    error: null,
    process: null,
    user: null,
    default: null
  });
  
  const animationFrameRef = useRef<number | null>(null);
  const lastCharTimeRef = useRef<number>(0);

  // Simple logging utility
  const logger = {
    debug: (message: string, ...args: any[]) => console.debug('[useDecoupledTypingEffect]', message, ...args),
    error: (message: string, ...args: any[]) => console.error('[useDecoupledTypingEffect]', message, ...args)
  };

  const updateWaitingState = () => {
    if (!sessionActiveRef.current || isStreamingCompleteRef.current) {
      setIsWaitingForNextType(false);
      setWaitingType(null);
      setActiveType(null);
      activeTypeRef.current = null;
      return;
    }

    if (!lastTypeRef.current) {
      setIsWaitingForNextType(false);
      setWaitingType(null);
      setActiveType(null);
      activeTypeRef.current = null;
      return;
    }

    setIsWaitingForNextType(true);
    setWaitingType(lastTypeRef.current);
    if (activeTypeRef.current !== lastTypeRef.current) {
      activeTypeRef.current = lastTypeRef.current;
      setActiveType(lastTypeRef.current);
    }
  };

  const typeNextChar = (timestamp: number) => {
    const timeSinceLastChar = timestamp - lastCharTimeRef.current;
    const typingSpeed = MIN_TYPING_SPEED + Math.random() * (MAX_TYPING_SPEED - MIN_TYPING_SPEED);
    const charInterval = 1000 / typingSpeed;

    if (timeSinceLastChar >= charInterval && streamBufferRef.current.length > 0) {
      const currentChunk = streamBufferRef.current[0];

      if (activeTypeRef.current !== currentChunk.type) {
        activeTypeRef.current = currentChunk.type;
        setActiveType(currentChunk.type);
      }

      setIsWaitingForNextType(false);
      setWaitingType(null);

      const nextChar = currentChunk.content.charAt(0);

      onMessagesUpdate((prevMessages: Message[]) => {
        const newMessages = [...prevMessages];
        newMessages[currentChunk.messageIndex] = {
          ...newMessages[currentChunk.messageIndex],
          content: newMessages[currentChunk.messageIndex].content + nextChar
        };
        return newMessages;
      });

      currentChunk.content = currentChunk.content.slice(1);

      if (currentChunk.content.length === 0) {
        streamBufferRef.current.shift();
        lastTypeRef.current = currentChunk.type;
      }

      lastCharTimeRef.current = timestamp;
      setIsReceivingChunks(true);
    }

    if (streamBufferRef.current.length > 0) {
      animationFrameRef.current = requestAnimationFrame(typeNextChar);
    } else {
      animationFrameRef.current = null;
      setIsReceivingChunks(false);
      updateWaitingState();
    }
  };

  // Add chunk for specific type
  const addChunk = (chunk: string, type: string) => {
    logger.debug('Adding chunk to buffer for type:', type, 'chunk:', chunk);
    sessionActiveRef.current = true;
    isStreamingCompleteRef.current = false;
    
    // Track message index in a ref to ensure it's available after state update
    const messageIndexRef = { value: -1 };

    const lastBufferItem = streamBufferRef.current[streamBufferRef.current.length - 1];
    const shouldAppendToLast = lastBufferItem && lastBufferItem.type === type;
    const shouldAppendToOpen = !lastBufferItem && currentOpenTypeRef.current === type && currentOpenMessageIndexRef.current !== null;

    if (shouldAppendToLast) {
      lastBufferItem.content += chunk;
    } else if (shouldAppendToOpen) {
      messageIndexRef.value = currentOpenMessageIndexRef.current as number;
      streamBufferRef.current.push({ content: chunk, type, messageIndex: messageIndexRef.value });
    } else {
      onMessagesUpdate((prevMessages: Message[]) => {
        const newMessages = [...prevMessages];
        messageIndexRef.value = newMessages.length;
        newMessages.push({ type, content: '' });
        currentMessageIndicesRef.current[type] = messageIndexRef.value;
        currentOpenTypeRef.current = type;
        currentOpenMessageIndexRef.current = messageIndexRef.value;
        return newMessages;
      });

      if (messageIndexRef.value !== -1) {
        streamBufferRef.current.push({ content: chunk, type, messageIndex: messageIndexRef.value });
      } else {
        logger.error('Failed to determine message index for chunk:', chunk);
      }
    }
    
    // Start the animation if not already running
    if (!animationFrameRef.current) {
      lastCharTimeRef.current = performance.now();
      animationFrameRef.current = requestAnimationFrame(typeNextChar);
    }
    
    setIsReceivingChunks(true);
    setIsWaitingForNextType(false);
    setWaitingType(null);
  };

  // Complete streaming for a specific type
  const completeStreaming = (type: string) => {
    logger.debug('Completing streaming for type:', type);
    isStreamingCompleteRef.current = true;
    sessionActiveRef.current = false;

    currentMessageIndicesRef.current[type] = null;
    if (currentOpenTypeRef.current === type) {
      currentOpenTypeRef.current = null;
      currentOpenMessageIndexRef.current = null;
    }
    
    if (streamBufferRef.current.length === 0 && animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (streamBufferRef.current.length === 0) {
      setIsReceivingChunks(false);
      setIsWaitingForNextType(false);
      setWaitingType(null);
      setActiveType(null);
      activeTypeRef.current = null;
    }
  };

  const startStreamingSession = () => {
    sessionActiveRef.current = true;
    isStreamingCompleteRef.current = false;
    setIsWaitingForNextType(false);
    setWaitingType(null);
  };

  // Reset all streaming state
  const resetStreaming = () => {
    logger.debug('Resetting streaming state');
    
    // Cancel animation frame
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    
    // Clear the buffer
    streamBufferRef.current = [];
    
    // Clear current message indices
    Object.keys(currentMessageIndicesRef.current).forEach(type => {
      currentMessageIndicesRef.current[type] = null;
    });

    currentOpenTypeRef.current = null;
    currentOpenMessageIndexRef.current = null;
    sessionActiveRef.current = false;
    isStreamingCompleteRef.current = false;
    activeTypeRef.current = null;
    lastTypeRef.current = null;
    
    setIsReceivingChunks(false);
    setIsWaitingForNextType(false);
    setWaitingType(null);
    setActiveType(null);
  };

  return {
    addChunk,
    completeStreaming,
    startStreamingSession,
    resetStreaming,
    isReceivingChunks,
    activeType,
    isWaitingForNextType,
    waitingType
  };
};
