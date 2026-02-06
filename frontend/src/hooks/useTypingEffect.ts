import { useEffect, useRef, useState } from 'react';
import { Message } from '../App';

// Define typing speed settings (characters per second)
const MIN_TYPING_SPEED = 50;
const MAX_TYPING_SPEED = 120;

interface TypingEffectConfig {
  onMessagesUpdate: (updater: (prevMessages: Message[]) => Message[]) => void;
}

interface TypingEffectReturn {
  addChunk: (chunk: string, type?: 'thought' | 'tool_call' | 'tool_response' | 'result' | 'chunk' | 'error' | 'debug' | 'process') => void;
  completeStreaming: () => void;
  resetStreaming: () => void;
  isReceivingChunks: boolean;
}

export const useTypingEffect = ({ onMessagesUpdate }: TypingEffectConfig): TypingEffectReturn => {
  const [isReceivingChunks, setIsReceivingChunks] = useState(false);
  
  // Buffer for streaming chunks with their types
  const streamBufferRef = useRef<{ content: string; type?: string }[]>([]);
  const currentMessageTypeRef = useRef<string | undefined>(undefined);
  const streamingMessageIndexRef = useRef<number>(-1);
  const streamDisplayRef = useRef<string>('');
  const animationFrameRef = useRef<number>();
  const lastCharTimeRef = useRef<number>(0);

  // Simple logging utility
  const logger = {
    debug: (message: string, ...args: any[]) => console.debug('[useTypingEffect]', message, ...args)
  };

  // Typing animation effect for streaming chunks
  useEffect(() => {
    const typeNextChar = (timestamp: number) => {
      // Calculate time since last character
      const timeSinceLastChar = timestamp - lastCharTimeRef.current;
      
      // Determine typing speed (random between min and max for natural effect)
      const typingSpeed = MIN_TYPING_SPEED + Math.random() * (MAX_TYPING_SPEED - MIN_TYPING_SPEED);
      const charInterval = 1000 / typingSpeed; // milliseconds per character
      
      // Check if there are chunks to process
      if (timeSinceLastChar >= charInterval && streamBufferRef.current.length > 0) {
        // Get the first chunk from the buffer
        const currentChunk = streamBufferRef.current[0];
        
        // If the message type changed, create a new message
        if (currentChunk.type !== currentMessageTypeRef.current) {
          logger.debug('Message type changed from', currentMessageTypeRef.current, 'to', currentChunk.type);
          
          // Complete previous message if it exists and it's a streaming message (has type property)
          if (streamingMessageIndexRef.current !== -1) {
            onMessagesUpdate((prevMessages) => {
              const newMessages = [...prevMessages];
              // Only complete messages that were created by the streaming system (have type property)
              // Ensure the message exists at the specified index
              const messageIndex = streamingMessageIndexRef.current;
              if (messageIndex >= 0 && messageIndex < newMessages.length && newMessages[messageIndex].type) {
                newMessages[messageIndex] = {
                  ...newMessages[messageIndex],
                  text: streamDisplayRef.current
                };
              }
              return newMessages;
            });
          }
          
          // Create new message for the new type
          streamDisplayRef.current = '';
          
          // Create new message with appropriate type
          const newMessage: Message = {
            text: '',
            isUser: false,
            type: currentChunk.type as any
          };
          
          onMessagesUpdate((prevMessages) => {
            const newMessages = [...prevMessages];
            newMessages.push(newMessage);
            streamingMessageIndexRef.current = newMessages.length - 1;
            return newMessages;
          });
          
          currentMessageTypeRef.current = currentChunk.type;
        }
        
        // Take the next character from the current chunk
        const nextChar = currentChunk.content.charAt(0);
        streamDisplayRef.current += nextChar;
        
        // Update the current chunk in the buffer
        currentChunk.content = currentChunk.content.slice(1);
        
        // If the current chunk is empty, remove it from the buffer
        if (currentChunk.content.length === 0) {
          streamBufferRef.current.shift();
        }
        
        // Update the message with the new character
        onMessagesUpdate((prevMessages) => {
          const newMessages = [...prevMessages];
          const messageIndex = streamingMessageIndexRef.current;
          if (messageIndex !== -1 && messageIndex < newMessages.length) {
            // Only update messages that were created by the streaming system (have type property)
            if (newMessages[messageIndex].type) {
              newMessages[messageIndex] = {
                ...newMessages[messageIndex],
                text: streamDisplayRef.current
              };
            }
          }
          return newMessages;
        });
        
        // Update last character time
        lastCharTimeRef.current = timestamp;
      }
      
      // Continue the animation if there are more characters to type
      if (streamBufferRef.current.length > 0 || isReceivingChunks) {
        animationFrameRef.current = requestAnimationFrame(typeNextChar);
      } else {
        // Animation complete
        if (streamingMessageIndexRef.current !== -1) {
          onMessagesUpdate((prevMessages) => {
            const newMessages = [...prevMessages];
            // Only complete messages that were created by the streaming system (have type property)
            // Ensure the message exists at the specified index
            const messageIndex = streamingMessageIndexRef.current;
            if (messageIndex >= 0 && messageIndex < newMessages.length && newMessages[messageIndex].type) {
              newMessages[messageIndex] = {
                ...newMessages[messageIndex],
                text: streamDisplayRef.current
              };
            }
            return newMessages;
          });
        }
        
        // Reset streaming state
        streamingMessageIndexRef.current = -1;
        streamDisplayRef.current = '';
        currentMessageTypeRef.current = undefined;
      }
    };
    
    // Start the animation if not already running and there's content to stream
    if (!animationFrameRef.current && (isReceivingChunks || streamBufferRef.current.length > 0)) {
      lastCharTimeRef.current = performance.now();
      animationFrameRef.current = requestAnimationFrame(typeNextChar);
    }
    
    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = undefined;
      }
    };
  }, [isReceivingChunks, onMessagesUpdate]);

  /**
   * Adds a chunk of text to the streaming buffer with its type
   */
  const addChunk = (chunk: string, type?: 'thought' | 'tool_call' | 'tool_response' | 'result' | 'chunk' | 'error' | 'debug' | 'process') => {
    logger.debug('Adding chunk to buffer:', chunk, 'type:', type);
    streamBufferRef.current.push({ content: chunk, type });
    setIsReceivingChunks(true);
  };

  /**
   * Completes the streaming process
   */
  const completeStreaming = () => {
    setIsReceivingChunks(false);
  };

  /**
   * Resets all streaming state
   */
  const resetStreaming = () => {
    streamBufferRef.current = [];
    streamDisplayRef.current = '';
    streamingMessageIndexRef.current = -1;
    currentMessageTypeRef.current = undefined;
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = undefined;
    }
    
    setIsReceivingChunks(false);
  };

  return {
    addChunk,
    completeStreaming,
    resetStreaming,
    isReceivingChunks
  };
};