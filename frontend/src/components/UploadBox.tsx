import React, { useRef, useState } from "react";

const API_BASE_URL = "http://localhost:8000";
const POLL_INTERVAL = 2000;

type UploadStatus = "idle" | "uploading" | "processing" | "completed" | "failed";

export const UploadBox = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const pollJobStatus = async (jobId: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/files/jobs/${jobId}/status`);
          if (!response.ok) throw new Error("Failed");
          const data = await response.json();
          
          if (data.status === "completed") {
            setUploadStatus("completed");
            resolve();
          } else if (data.status === "failed") {
            setUploadStatus("failed");
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
      await pollJobStatus(data.job_id);
    } catch {
      setUploadStatus("failed");
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === "application/pdf") uploadFile(file);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file?.type === "application/pdf") uploadFile(file);
  };

  const isLoading = uploadStatus === "uploading" || uploadStatus === "processing";

  return (
    <div
      onClick={() => !isLoading && fileInputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={(e) => { e.preventDefault(); setIsDragging(false); }}
      onDrop={!isLoading ? handleDrop : undefined}
      className={`
        w-64 h-16 border-2 border-dashed rounded flex items-center justify-center
        text-sm cursor-pointer transition-colors
        ${isDragging ? "bg-blue-50 border-blue-400" : ""}
        ${uploadStatus === "completed" ? "bg-green-50 border-green-400 text-green-600" : ""}
        ${uploadStatus === "failed" ? "bg-red-50 border-red-400 text-red-600" : ""}
        ${uploadStatus === "idle" ? "border-gray-300 text-gray-500 hover:border-gray-400" : ""}
        ${isLoading ? "border-blue-400 text-blue-500" : ""}
      `}
    >
      <input
        type="file"
        accept="application/pdf"
        ref={fileInputRef}
        className="hidden"
        onChange={handleChange}
        disabled={isLoading}
      />
      {uploadStatus === "idle" && "Drop PDF or click"}
      {isLoading && (
        <span className="flex items-center gap-2">
          <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          Processing...
        </span>
      )}
      {uploadStatus === "completed" && "✓ Done"}
      {uploadStatus === "failed" && (
        <span onClick={(e) => { e.stopPropagation(); setUploadStatus("idle"); }}>
          ✗ Failed - Retry
        </span>
      )}
    </div>
  );
};
