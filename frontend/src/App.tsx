import React, { useState, useEffect, useCallback } from 'react';
import ChatInterface from './components/ChatInterface';
import MessageInput from './components/MessageInput';
import { uploadPDF, getJobStatus, askQuestion } from './services/api';
import type { Message, UploadJob } from './types';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentJob, setCurrentJob] = useState<UploadJob | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  // Poll job status
  useEffect(() => {
    if (!currentJob || currentJob.status === 'completed' || currentJob.status === 'failed') {
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const status = await getJobStatus(currentJob.id);
        setCurrentJob({
          id: status.id,
          status: status.status as UploadJob['status'],
          progress: status.progress,
          message: status.message,
          filename: status.result?.filename,
          error: status.error
        });

        // Add processing status as system message
        if (status.status === 'processing') {
          const processingMessage: Message = {
            id: `processing-${status.id}`,
            role: 'system',
            content: `Processing document... ${status.progress}%`,
            timestamp: new Date()
          };
          setMessages(prev => {
            // Remove previous processing message and add new one
            const filtered = prev.filter(m => !m.id.startsWith('processing-'));
            return [...filtered, processingMessage];
          });
        } else if (status.status === 'completed') {
          const successMessage: Message = {
            id: `completed-${status.id}`,
            role: 'system',
            content: 'Document processed successfully! You can now ask questions about it.',
            timestamp: new Date()
          };
          setMessages(prev => {
            const filtered = prev.filter(m => !m.id.startsWith('processing-'));
            return [...filtered, successMessage];
          });
        } else if (status.status === 'failed') {
          const errorMessage: Message = {
            id: `error-${status.id}`,
            role: 'system',
            content: `Failed to process document: ${status.error || 'Unknown error'}`,
            timestamp: new Date()
          };
          setMessages(prev => {
            const filtered = prev.filter(m => !m.id.startsWith('processing-'));
            return [...filtered, errorMessage];
          });
        }

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Error polling job status:', error);
        clearInterval(pollInterval);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [currentJob]);

  const handleFileUpload = useCallback(async (file: File) => {
    setIsUploading(true);

    // Add file message to chat with loading state
    const fileMessage: Message = {
      id: `file-${Date.now()}`,
      role: 'user',
      content: file.name,
      timestamp: new Date(),
      file: file
    };
    setMessages(prev => [...prev, fileMessage]);

    try {
      const response = await uploadPDF(file);
      setCurrentJob({
        id: response.job_id,
        status: 'queued',
        progress: 0,
        message: 'Upload queued...',
        filename: file.name
      });

      // Add initial processing message
      const processingMessage: Message = {
        id: `processing-${response.job_id}`,
        role: 'system',
        content: 'Processing document...',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, processingMessage]);

    } catch (error) {
      console.error('Upload failed:', error);
      setCurrentJob({
        id: 'error',
        status: 'failed',
        progress: 0,
        message: 'Upload failed. Please try again.',
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      // Add error message
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'system',
        content: 'Failed to upload document. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsUploading(false);
    }
  }, []);

  const handleSendMessage = useCallback(async (question: string) => {
    if (!currentJob || currentJob.status !== 'completed') {
      return;
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsAsking(true);

    try {
      const response = await askQuestion(question);

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Question failed:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your question. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsAsking(false);
    }
  }, [currentJob]);

  const canAskQuestions = currentJob?.status === 'completed';

  return (
    <div className="h-screen flex flex-col bg-white">
      {/* Chat Interface - Full Screen */}
      <div className="flex-1 flex flex-col">
        <ChatInterface
          messages={messages}
          isLoading={isAsking}
          onFileDrop={handleFileUpload}
          isUploading={isUploading}
        />
        <MessageInput
          onSendMessage={handleSendMessage}
          onFileSelect={handleFileUpload}
          disabled={!canAskQuestions || isAsking}
          attachmentDisabled={isUploading}
          placeholder={
            canAskQuestions
              ? "Ask a question about the document..."
              : "Upload a PDF document to get started..."
          }
        />
      </div>
    </div>
  );
}

export default App;
