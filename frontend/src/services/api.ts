import axios, { AxiosError } from 'axios';
import type { UploadResponse, JobStatusResponse, AskResponse } from '../types';

// Get API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling helper
const handleApiError = (error: unknown): void => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail?: string }>;

    if (!axiosError.response) {
      // Network error or backend not running
      throw new Error('Cannot connect to backend server. Please make sure the backend is running on localhost:8000.');
    }

    const status = axiosError.response.status;
    const data = axiosError.response.data;

    if (status === 413) {
      throw new Error('File is too large. Maximum file size is 10MB.');
    } else if (status === 415) {
      throw new Error('Invalid file type. Only PDF files are supported.');
    } else if (status === 500) {
      throw new Error('Backend server error. Please try again later.');
    } else if (status === 503) {
      throw new Error('Backend service is temporarily unavailable. Please try again in a few moments.');
    } else if (data?.detail) {
      throw new Error(data.detail);
    } else {
      throw new Error('An unexpected error occurred. Please try again.');
    }
  } else {
    throw new Error('An unexpected error occurred. Please try again.');
  }
};

// API functions
export const uploadPDF = async (file: File): Promise<UploadResponse> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error; // This line will never be reached, but satisfies TypeScript
  }
};

export const getJobStatus = async (jobId: string): Promise<JobStatusResponse> => {
  try {
    const response = await api.get(`/documents/job/${jobId}`);
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error; // This line will never be reached, but satisfies TypeScript
  }
};

export const askQuestion = async (question: string): Promise<AskResponse> => {
  try {
    const response = await api.post('/query/ask', { question });
    return response.data;
  } catch (error) {
    handleApiError(error);
    throw error; // This line will never be reached, but satisfies TypeScript
  }
};

export default api;
