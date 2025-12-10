import React from 'react';
import { CheckCircle, XCircle, Clock, Loader } from 'lucide-react';
import type { UploadJob } from '../types';

interface UploadStatusProps {
  job: UploadJob | null;
}

const UploadStatus: React.FC<UploadStatusProps> = ({ job }) => {
  if (!job) return null;

  const getStatusIcon = () => {
    switch (job.status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'processing':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'queued':
      default:
        return <Clock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = () => {
    switch (job.status) {
      case 'completed':
        return 'text-green-700 bg-green-50 border-green-200';
      case 'failed':
        return 'text-red-700 bg-red-50 border-red-200';
      case 'processing':
        return 'text-blue-700 bg-blue-50 border-blue-200';
      case 'queued':
      default:
        return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    }
  };

  return (
    <div className={`border rounded-lg p-4 ${getStatusColor()}`}>
      <div className="flex items-center space-x-3">
        {getStatusIcon()}
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">
              {job.status === 'completed' && 'Upload Complete'}
              {job.status === 'failed' && 'Upload Failed'}
              {job.status === 'processing' && 'Processing Document'}
              {job.status === 'queued' && 'Upload Queued'}
            </h3>
            {job.status === 'processing' && (
              <span className="text-xs font-medium">{job.progress}%</span>
            )}
          </div>
          <p className="text-sm mt-1">{job.message}</p>
          {job.filename && (
            <p className="text-xs mt-1 opacity-75">
              File: {job.filename}
            </p>
          )}
          {job.error && (
            <p className="text-xs mt-1 text-red-600">
              Error: {job.error}
            </p>
          )}
        </div>
      </div>

      {job.status === 'processing' && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadStatus;
