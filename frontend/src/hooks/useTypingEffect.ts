import { useEffect, useRef, useState } from 'react';
import { Message } from '../App';

// Define typing speed settings (characters per second)
const MIN_TYPING_SPEED = 50;
const MAX_TYPING_SPEED = 120;

interface TypingEffectConfig {
  onMessagesUpdate: (updater: (prevMessages: Message[]) => Message[]) => void;
}

interface TypingEffectReturn {
  addChunk: (chunk: string) => void;
  completeStreaming: () => void;
  resetStreaming: () => void;
  isReceivingChunks: boolean;
}

export const useTypingEffect = ({ onMessagesUpdate }: TypingEffectConfig): TypingEffectReturn => {
  const [isReceivingChunks, setIsReceivingChunks] = useState(false);
  
  // Buffer for streaming chunks and current display text
  const streamBufferRef = useRef<string>('');
  const streamDisplayRef = useRef<string>('');
  const animationFrameRef = useRef<number>();
  const lastCharTimeRef = useRef<number>(0);
  const streamingMessageIndexRef = useRef<number>(-1);

  // Typing animation effect for streaming chunks
  useEffect(() => {
    const typeNextChar = (timestamp: number) => {
      // Calculate time since last character
      const timeSinceLastChar = timestamp - lastCharTimeRef.current;
      
      // Determine typing speed (random between min and max for natural effect)
      const typingSpeed = MIN_TYPING_SPEED + Math.random() * (MAX_TYPING_SPEED - MIN_TYPING_SPEED);
      const charInterval = 1000 / typingSpeed; // milliseconds per character
      
      // Check if enough time has passed to type the next character
      if (timeSinceLastChar >= charInterval && streamBufferRef.current.length > 0) {
        // Take the next character from the buffer
        const nextChar = streamBufferRef.current.charAt(0);
        streamBufferRef.current = streamBufferRef.current.slice(1);
        streamDisplayRef.current += nextChar;
        
        // Update the message with the new character
        onMessagesUpdate((prevMessages) => {
          const newMessages = [...prevMessages];
          if (streamingMessageIndexRef.current !== -1 && streamingMessageIndexRef.current < newMessages.length) {
            newMessages[streamingMessageIndexRef.current] = {
              ...newMessages[streamingMessageIndexRef.current],
              text: streamDisplayRef.current
            };
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
        onMessagesUpdate((prevMessages) => {
          const newMessages = [...prevMessages];
          if (streamingMessageIndexRef.current !== -1 && streamingMessageIndexRef.current < newMessages.length) {
            newMessages[streamingMessageIndexRef.current] = {
              ...newMessages[streamingMessageIndexRef.current],
            };
          }
          return newMessages;
        });
        
        // Reset streaming state
        streamingMessageIndexRef.current = -1;
        streamDisplayRef.current = '';
      }
    };
    
    // Start the animation if not already running
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
   * Adds a chunk of text to the streaming buffer
   */
  const addChunk = (chunk: string) => {
    setIsReceivingChunks(true);
    
    // Buffer the chunk instead of immediately appending
    streamBufferRef.current += chunk;

    // If this is the first chunk, create a new message
    if (streamingMessageIndexRef.current === -1) {
      onMessagesUpdate((prevMessages) => {
        const newMessages = [...prevMessages];
        newMessages.push({ text: '', isUser: false});
        streamingMessageIndexRef.current = newMessages.length - 1;
        return newMessages;
      });
    }
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
    streamBufferRef.current = '';
    streamDisplayRef.current = '';
    streamingMessageIndexRef.current = -1;
    
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = undefined;
    }
  };

  return {
    addChunk,
    completeStreaming,
    resetStreaming,
    isReceivingChunks
  };
};