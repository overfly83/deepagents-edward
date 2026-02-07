import React from 'react';
import { MessageContainers } from './MessageContainers';

interface Message {
  type: string;
  content: string;
}

export interface MessageManagerProps {
  messages: Message[];
  activeType?: string | null;
  isWaiting?: boolean;
  waitingType?: string | null;
}

export const MessageManager: React.FC<MessageManagerProps> = ({ 
  messages = [],
  activeType,
  isWaiting,
  waitingType
}) => {
  return (
    <div className="message-manager">
      <MessageContainers
        messages={messages}
        activeType={activeType}
        isWaiting={isWaiting}
        waitingType={waitingType}
      />
    </div>
  );
};

export default MessageManager;
