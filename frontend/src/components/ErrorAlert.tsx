'use client';

import { AlertCircle, X } from 'lucide-react';
import { useState } from 'react';

interface ErrorAlertProps {
  message: string;
  onClose?: () => void;
}

export default function ErrorAlert({ message, onClose }: ErrorAlertProps) {
  const [isVisible, setIsVisible] = useState(true);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  if (!isVisible) return null;

  return (
    <div className="w-full max-w-3xl mx-auto mb-4">
      <div className="bg-black border-2 border-white/30 rounded-lg p-6">
        <div className="flex items-start space-x-4">
          <AlertCircle className="h-6 w-6 text-white flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-base text-white font-mono font-semibold">
              ERROR: {message}
            </p>
          </div>
          {onClose && (
            <button
              onClick={handleClose}
              className="p-1 bg-black border border-white/30 rounded hover:bg-white hover:text-black transition-colors"
            >
              <X className="h-5 w-5 text-white hover:text-black transition-colors" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
} 