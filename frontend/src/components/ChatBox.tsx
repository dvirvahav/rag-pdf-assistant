import React, { useState, useRef } from "react";

const API_BASE_URL = "http://localhost:8000";
const POLL_INTERVAL = 2000;

interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
}

type UploadStatus = "idle" | "uploading" | "processing" | "completed" | "failed";

export const ChatBox = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, text: "Hello! Upload a PDF and ask me questions about it.", sender: "bot" },
  ]);
  const [input, setInput] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const pollJobStatus = async (jobId: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/files/jobs/${jobId}/status`);
          if (!response.ok) throw new Error("Failed");
          const data = await response.json();
          
          if (data.status === "completed") {
            setUploadStatus("completed");
            setMessages((prev) => [
              ...prev,
              { id: Date.now(), text: `✓ File processed! ${data.details?.chunks_count || 0} chunks created. You can now ask questions.`, sender: "bot" },
            ]);
            resolve();
          } else if (data.status === "failed") {
            setUploadStatus("failed");
            setMessages((prev) => [
              ...prev,
              { id: Date.now(), text: `✗ Processing failed: ${data.details?.error || "Unknown error"}`, sender: "bot" },
            ]);
            reject();
          } else {
            setTimeout(poll, POLL_INTERVAL);
          }
        } catch {
          setUploadStatus("failed");
          reject();
        }
      };
      poll();
    });
  };

  const uploadFile = async (file: File) => {
    setUploadStatus("uploading");
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: `Uploading ${file.name}...`, sender: "bot" },
    ]);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(`${API_BASE_URL}/files/upload`, {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Upload failed");
      const data = await response.json();
      
      setUploadStatus("processing");
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { id: Date.now(), text: `Processing ${file.name}...`, sender: "bot" },
      ]);
      
      await pollJobStatus(data.job_id);
    } catch {
      setUploadStatus("failed");
      setMessages((prev) => [
        ...prev,
        { id: Date.now(), text: "✗ Upload failed. Please try again.", sender: "bot" },
      ]);
    }
    setTimeout(scrollToBottom, 100);
  };

  const handleSend = () => {
    if (!input.trim()) return;
    setMessages((prev) => [
      ...prev,
      { id: Date.now(), text: input, sender: "user" },
    ]);
    setInput("");
    setTimeout(scrollToBottom, 100);
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
    if (file?.type === "application/pdf") {
      uploadFile(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file?.type === "application/pdf") {
      uploadFile(file);
    }
  };

  const isUploading = uploadStatus === "uploading" || uploadStatus === "processing";

  return (
    <div
      className={`w-full max-w-2xl h-[600px] flex flex-col bg-white rounded-xl shadow-lg border ${
        isDragging ? "border-blue-500 bg-blue-50" : "border-gray-200"
      }`}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
      onDrop={handleDrop}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-xl">
        <h2 className="font-semibold text-gray-700">PDF Assistant</h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {isDragging && (
          <div className="absolute inset-0 flex items-center justify-center bg-blue-50/90 rounded-xl z-10">
            <p className="text-blue-600 font-medium">Drop PDF here</p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] px-4 py-2 rounded-2xl ${
                msg.sender === "user"
                  ? "bg-blue-600 text-white rounded-br-md"
                  : "bg-gray-100 text-gray-800 rounded-bl-md"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
        <div className="flex items-center gap-2">
          {/* Upload Button */}
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
              isUploading
                ? "text-gray-400 cursor-not-allowed"
                : "text-gray-500 hover:bg-gray-200"
            }`}
            title="Upload PDF"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
            </svg>
          </button>

          {/* Text Input */}
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2 bg-white border border-gray-300 rounded-full text-sm focus:outline-none focus:border-blue-400"
          />

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className={`p-2 rounded-lg transition ${
              input.trim()
                ? "bg-blue-600 text-white hover:bg-blue-700"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          Drag & drop PDF or click 📎 to upload
        </p>
      </div>
    </div>
  );
};
