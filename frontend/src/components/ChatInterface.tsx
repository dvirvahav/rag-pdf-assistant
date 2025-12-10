import React, { useEffect, useRef, useCallback, useState } from 'react';
import MessageComponent from './Message';
import { Upload, FileText } from 'lucide-react';
import type { Message } from '../types';

interface ChatInterfaceProps {
  messages: Message[];
  isLoading?: boolean;
  onFileDrop?: (file: File) => void;
  isUploading?: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  isLoading = false,
  onFileDrop,
  isUploading = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (onFileDrop && e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        onFileDrop(file);
      }
    }
  }, [onFileDrop]);

  return (
    <div
      className="flex-1 flex flex-col min-h-0 relative"
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {dragActive && (
        <div className="absolute inset-0 bg-blue-50 bg-opacity-90 flex items-center justify-center z-10 border-2 border-dashed border-blue-300">
          <div className="text-center">
            <Upload className="w-12 h-12 text-blue-500 mx-auto mb-4" />
            <p className="text-lg font-medium text-blue-700">Drop your PDF here</p>
            <p className="text-sm text-blue-600">Upload a document to start chatting</p>
          </div>
        </div>
      )}

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <FileText className="w-16 h-16 mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Drop a PDF to get started
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Drag and drop a PDF document here, or use the attachment button below.
                Once uploaded, you can ask questions about its content.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <MessageComponent
                  key={message.id}
                  message={message}
                  isUploading={isUploading && message.file !== undefined}
                />
              ))}

              {isLoading && (
                <div className="flex justify-start mb-4">
                  <div className="flex max-w-[80%]">
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-500 mr-3 flex items-center justify-center">
                      <svg
                        className="w-4 h-4 text-white animate-spin"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                    </div>
                    <div className="bg-gray-100 border border-gray-200 rounded-lg px-4 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatInterface;
