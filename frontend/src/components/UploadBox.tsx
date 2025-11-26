/**
 * UploadBox Component
 *
 * A UI component that allows selecting a PDF file using:
 * - Drag & Drop
 * - Click to open file picker
 *
 * Props:    none
 * Returns:  JSX.Element
 */
import React, { useRef, useState } from "react";

export const UploadBox = () => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please upload a PDF file.");
      return;
    }

    console.log("PDF selected (drag):", file);
  };

  const handleFilePickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please upload a PDF file.");
      return;
    }

    console.log("PDF selected (picker):", file);
  };

  return (
    <div className="flex flex-col items-center">
      {/* Hidden File Input */}
      <input
        type="file"
        accept="application/pdf"
        ref={fileInputRef}
        className="hidden"
        onChange={handleFilePickerChange}
      />

      {/* Upload Box */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          w-[400px] h-[250px] rounded-xl border-2 border-dashed flex flex-col 
          items-center justify-center text-center cursor-pointer transition 
          ${isDragging ? "bg-blue-100 border-blue-500" : "bg-white border-gray-400"}
        `}
      >
        <p className="text-lg font-medium">
          גרור PDF לכאן  
          <br />
          או לחץ כדי לבחור
        </p>
      </div>
    </div>
  );
};
