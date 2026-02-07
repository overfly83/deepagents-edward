import React from 'react';

interface Message {
  type: string;
  content: string;
}

interface MessageContainersProps {
  messages: Message[];
  activeType?: string | null;
  isWaiting?: boolean;
  waitingType?: string | null;
}

const MessageTypeRenderer: React.FC<{ message: Message }> = ({ message }) => {
  const { type, content } = message;
  
  const typeColors: Record<string, string> = {
    thought: 'bg-purple-100 text-purple-800',
    'tool_call': 'bg-orange-100 text-orange-800',
    'tool_response': 'bg-green-100 text-green-800',
    plan: 'bg-yellow-100 text-yellow-800',
    todo: 'bg-indigo-100 text-indigo-800',
    result: 'bg-blue-100 text-blue-800',
    error: 'bg-red-100 text-red-800',
    process: 'bg-gray-100 text-gray-800',
    user: 'bg-indigo-500 text-white ml-auto',
    default: 'bg-gray-200 text-gray-800'
  };

  const typeLabels: Record<string, string> = {
    thought: '💭 Thought',
    'tool_call': '🔧 Tool Call',
    'tool_response': '🔄 Tool Response',
    plan: '🧭 Plan',
    todo: '📝 Todo',
    result: '✅ Result',
    error: '❌ Error',
    process: '🔄 Process',
    user: 'User',
    default: 'Response'
  };

  const bgColor = typeColors[type] || 'bg-gray-200';
  const label = typeLabels[type] || 'Message';
  const isUserMessage = type === 'user';

  return (
    <div className={`flex mb-4 ${isUserMessage ? 'justify-end' : 'justify-start'}`}>
      <div className="flex flex-col max-w-[80%]">
        {!isUserMessage && (
          <div className="text-xs font-semibold mb-1 text-gray-500">{label}</div>
        )}
        <div className={`${bgColor} px-4 py-2 rounded-lg shadow-sm message-bubble`}>
          <p>{content}</p>
        </div>
      </div>
    </div>
  );
};

const TypingIndicator = ({ type }: { type: string }) => {
  const typeColors: Record<string, string> = {
    thought: 'bg-purple-100',
    'tool_call': 'bg-orange-100',
    'tool_response': 'bg-green-100',
    plan: 'bg-yellow-100',
    todo: 'bg-indigo-100',
    result: 'bg-blue-100',
    error: 'bg-red-100',
    process: 'bg-gray-100',
    user: 'bg-indigo-500',
    default: 'bg-gray-200'
  };

  const bgColor = typeColors[type] || 'bg-gray-200';

  return (
    <div className="flex justify-start mb-4">
      <div className={`${bgColor} text-gray-800 px-4 py-2 rounded-lg typing-indicator`}>
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  );
};

export const MessageContainers: React.FC<MessageContainersProps> = ({
  messages = [],
  activeType,
  isWaiting = false,
  waitingType
}) => {
  const indicatorType = activeType || waitingType || 'default';
  const showIndicator = isWaiting;
  const visibleMessages = messages.filter((message) => message.content.trim().length > 0);

  return (
    <div className="message-containers">
      {visibleMessages.map((message, index) => (
        <MessageTypeRenderer key={`${message.type}-${index}`} message={message} />
      ))}
      {showIndicator && <TypingIndicator type={indicatorType} />}
    </div>
  );
};

export default MessageContainers;
