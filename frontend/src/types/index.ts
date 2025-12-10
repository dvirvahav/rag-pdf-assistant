// Message types for chat interface
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  file?: File;
}

// Upload job status
export interface UploadJob {
  id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string;
  filename?: string;
  error?: string;
}

// App state
export interface AppState {
  messages: Message[];
  currentJob: UploadJob | null;
  isUploading: boolean;
  isAsking: boolean;
}
