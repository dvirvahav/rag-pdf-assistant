import React, { useState, useRef } from "react";

const FILE_API_URL = "http://localhost:8000";
const RAG_API_URL = "http://localhost:8002";
const POLL_INTERVAL = 2000;

interface FileAttachment {
  filename: string;
  status: "uploading" | "processing" | "completed" | "failed";
}

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
  attachment?: FileAttachment;
  isLoading?: boolean;
}

export const ChatBox = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hello! Upload a PDF and ask me questions about it.", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [currentFilename, setCurrentFilename] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const updateAttachmentStatus = (messageId: number, status: FileAttachment["status"]) => {
    setMessages((prev) =>
      prev.map((msg) =>
        msg.id === messageId && msg.attachment
          ? { ...msg, attachment: { ...msg.attachment, status } }
          : msg
      )
    );
  };

  const pollJobStatus = async (jobId: string, messageId: number, filename: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await fetch(`${FILE_API_URL}/files/jobs/${jobId}/status`);
          if (!response.ok) throw new Error("Failed");
          const data = await response.json();

          if (data.status === "completed") {
            updateAttachmentStatus(messageId, "completed");
            setCurrentFilename(filename);
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now(),
                text: `✓ File processed! ${data.details?.chunks_count || 0} chunks created. You can now ask questions about "${filename}".`,
                sender: "bot",
              },
            ]);
            setIsUploading(false);
            resolve();
          } else if (data.status === "failed") {
            updateAttachmentStatus(messageId, "failed");
            setMessages((prev) => [
              ...prev,
              {
                id: Date.now(),
                text: `✗ Processing failed: ${data.details?.error || "Unknown error"}`,
                sender: "bot",
              },
            ]);
            setIsUploading(false);
            reject();
          } else {
            setTimeout(poll, POLL_INTERVAL);
          }
        } catch {
          updateAttachmentStatus(messageId, "failed");
          setIsUploading(false);
          reject();
        }
      };
      poll();
    });
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    const messageId = Date.now();

    setMessages((prev) => [
      ...prev,
      {
        id: messageId,
        text: "",
        sender: "user",
        attachment: { filename: file.name, status: "uploading" },
      },
    ]);
    setTimeout(scrollToBottom, 100);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${FILE_API_URL}/files/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Upload failed");
      const data = await response.json();

      updateAttachmentStatus(messageId, "processing");
      await pollJobStatus(data.job_id, messageId, file.name);
    } catch {
      updateAttachmentStatus(messageId, "failed");
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), text: "✗ Upload failed. Please try again.", sender: "bot" },
      ]);
      setIsUploading(false);
    }
    setTimeout(scrollToBottom, 100);
  };

  const askQuestion = async (question: string) => {
    if (!currentFilename) {
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), text: "Please upload a PDF first before asking questions.", sender: "bot" },
      ]);
      return;
    }

    setIsAsking(true);
    const loadingMsgId = Date.now();

    // Add loading message
    setMessages((prev) => [
      ...prev,
      { id: loadingMsgId, text: "", sender: "bot", isLoading: true },
    ]);
    setTimeout(scrollToBottom, 100);

    try {
      const response = await fetch(`${RAG_API_URL}/rag/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: currentFilename, question }),
      });

      if (!response.ok) throw new Error("RAG request failed");
      const data = await response.json();

      // Replace loading message with actual response
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMsgId
            ? { ...msg, text: data.answer || "No answer found.", isLoading: false }
            : msg
        )
      );
    } catch (error) {
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === loadingMsgId
            ? { ...msg, text: "✗ Failed to get answer. Please try again.", isLoading: false }
            : msg
        )
      );
    }
    setIsAsking(false);
    setTimeout(scrollToBottom, 100);
  };

  const handleSend = () => {
    if (!input.trim() || isAsking) return;
    const question = input.trim();
    setMessages((prev) => [...prev, { id: Date.now(), text: question, sender: "user" }]);
    setInput("");
    setTimeout(scrollToBottom, 100);
    askQuestion(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === "application/pdf" && !isUploading) {
      uploadFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file?.type === "application/pdf") {
      uploadFile(file);
    }
  };

  // File Attachment Card Component
  const FileCard = ({ attachment }: { attachment: FileAttachment }) => {
    const statusConfig = {
      uploading: { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-600", label: "Uploading..." },
      processing: { bg: "bg-yellow-50", border: "border-yellow-200", text: "text-yellow-600", label: "Processing..." },
      completed: { bg: "bg-green-50", border: "border-green-200", text: "text-green-600", label: "Ready" },
      failed: { bg: "bg-red-50", border: "border-red-200", text: "text-red-600", label: "Failed" },
    };
    const config = statusConfig[attachment.status];

    return (
      <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${config.bg} ${config.border}`}>
        <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center flex-shrink-0">
          <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zm-1 2l5 5h-5V4zm-3 9h2v2H9v2H7v-2h2v-2H7v-2h2v2zm4 0h4v2h-4v-2zm0 4h4v2h-4v-2z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-800 truncate">{attachment.filename}</p>
          <div className="flex items-center gap-2">
            {(attachment.status === "uploading" || attachment.status === "processing") && (
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
            )}
            <span className={`text-xs ${config.text}`}>{config.label}</span>
          </div>
        </div>
        {attachment.status === "completed" && (
          <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        )}
        {attachment.status === "failed" && (
          <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        )}
      </div>
    );
  };

  // Loading dots component
  const LoadingDots = () => (
    <div className="flex items-center gap-1">
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
    </div>
  );

  return (
    <div
      className={`w-full max-w-2xl h-[600px] flex flex-col bg-white rounded-xl shadow-lg border relative ${
        isDragging ? "border-blue-500 bg-blue-50" : "border-gray-200"
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
      onDrop={handleDrop}
    >
      {/* Drag Overlay */}
      {isDragging && (
        <div className="absolute inset-0 flex items-center justify-center bg-blue-50/95 rounded-xl z-20 border-2 border-dashed border-blue-400">
          <div className="text-center">
            <svg className="w-12 h-12 mx-auto text-blue-500 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-blue-600 font-medium">Drop PDF here</p>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-xl flex items-center justify-between">
        <h2 className="font-semibold text-gray-700">PDF Assistant</h2>
        {currentFilename && (
          <span className="text-xs text-gray-500 bg-gray-200 px-2 py-1 rounded">
            📄 {currentFilename}
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div className={`max-w-[80%] ${msg.attachment ? "" : "px-4 py-2 rounded-2xl"} ${
              msg.sender === "user" && !msg.attachment
                ? "bg-blue-600 text-white rounded-br-md"
                : !msg.attachment
                ? "bg-gray-100 text-gray-800 rounded-bl-md"
                : ""
            }`}>
              {msg.attachment ? (
                <FileCard attachment={msg.attachment} />
              ) : msg.isLoading ? (
                <LoadingDots />
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
        <div className="flex items-center gap-2">
          <input
            type="file"
            accept="application/pdf"
            ref={fileInputRef}
            className="hidden"
            onChange={handleFileChange}
            disabled={isUploading}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className={`p-2 rounded-lg transition ${
              isUploading ? "text-gray-400 cursor-not-allowed" : "text-gray-500 hover:bg-gray-200"
            }`}
            title="Upload PDF"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </button>

          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={currentFilename ? "Ask a question..." : "Upload a PDF first..."}
            disabled={isAsking}
            className="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-full text-sm focus:outline-none focus:border-blue-400 disabled:bg-gray-100"
          />

          <button
            onClick={handleSend}
            disabled={!input.trim() || isAsking}
            className={`p-2 rounded-lg transition ${
              input.trim() && !isAsking ? "bg-blue-600 text-white hover:bg-blue-700" : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          {currentFilename ? `Chatting about: ${currentFilename}` : "Drag & drop PDF or click 📎 to upload"}
        </p>
      </div>
    </div>
  );
};
