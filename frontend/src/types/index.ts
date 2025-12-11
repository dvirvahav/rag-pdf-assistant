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

// API response types
export interface UploadResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface JobStatusResponse {
  id: string;
  type: string;
  status: string;
  progress: number;
  message: string;
  created_at: string;
  updated_at: string;
  result?: {
    filename?: string;
    [key: string]: unknown;
  };
  error?: string;
}

export interface AskRequest {
  question: string;
}

export interface AskResponse {
  question: string;
  answer: string;
  context_used?: string[];
}

// Component props types
export interface UploadStatusProps {
  job: UploadJob | null;
}

export interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onFileSelect?: (file: File) => void;
  disabled?: boolean;
  attachmentDisabled?: boolean;
  placeholder?: string;
}

export interface MessageProps {
  message: Message;
  isUploading?: boolean;
}

export interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
  disabled?: boolean;
}

export interface ChatInterfaceProps {
  messages: Message[];
  isLoading?: boolean;
  onFileDrop?: (file: File) => void;
  isUploading?: boolean;
}
