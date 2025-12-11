import { User, Bot, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import type { MessageProps } from '../types';

export const MessageComponent = ({ message, isUploading = false }: MessageProps) => {
  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';
  const isFile = message.file !== undefined;

  // System messages (processing status)
  if (isSystem) {
    const isProcessing = message.content.includes('Processing');
    const isCompleted = message.content.includes('successfully');
    const isError = message.content.includes('Failed') || message.content.includes('error');

    return (
      <div className="flex w-full justify-center mb-4">
        <div className="flex items-center space-x-2 bg-gray-50 border border-gray-200 rounded-lg px-4 py-2 max-w-md">
          {isProcessing && <Loader className="w-4 h-4 text-blue-500 animate-spin" />}
          {isCompleted && <CheckCircle className="w-4 h-4 text-green-500" />}
          {isError && <AlertCircle className="w-4 h-4 text-red-500" />}
          <span className="text-sm text-gray-700">{message.content}</span>
        </div>
      </div>
    );
  }

  // File messages
  if (isFile) {
    return (
      <div className="flex w-full justify-end mb-4">
        <div className="flex max-w-[80%] bg-blue-50 border border-blue-200 rounded-lg px-3 py-2">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-red-500 flex-shrink-0" />
            <span className="text-sm text-gray-700">Uploaded PDF</span>
            {isUploading && (
              <Loader className="w-3 h-3 text-blue-500 animate-spin flex-shrink-0" />
            )}
          </div>
        </div>
      </div>
    );
  }

  // Regular user/assistant messages
  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
      >
        {/* Avatar */}
        <div
          className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
            isUser
              ? 'bg-blue-500 ml-3'
              : 'bg-gray-500 mr-3'
          }`}
        >
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message bubble */}
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 text-gray-800 border border-gray-200'
          }`}
        >
          <div className="whitespace-pre-wrap break-words">
            {message.content}
          </div>
          <div
            className={`text-xs mt-1 ${
              isUser ? 'text-blue-100' : 'text-gray-500'
            }`}
          >
            {message.timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

