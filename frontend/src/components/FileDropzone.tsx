'use client';

import { useState, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, X } from 'lucide-react';

interface FileDropzoneProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  onRemoveFile: () => void;
  isLoading?: boolean;
}

export default function FileDropzone({ 
  onFileSelect, 
  selectedFile, 
  onRemoveFile, 
  isLoading = false 
}: FileDropzoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf'];
    
    if (!allowedTypes.includes(file.type)) {
      alert('Please select a PDF file.');
      return false;
    }
    
    if (file.size > maxSize) {
      alert('File size must be less than 10MB.');
      return false;
    }
    
    return true;
  };

  const handleFileSelect = useCallback((file: File) => {
    if (validateFile(file)) {
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  if (selectedFile) {
    return (
      <motion.div 
        className="w-full max-w-2xl mx-auto"
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <motion.div 
          className="bg-card border border-border rounded-lg p-6"
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <motion.div 
                className="p-3 bg-primary/10 border border-primary/20 rounded-lg"
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{ 
                  duration: 2, 
                  repeat: Infinity, 
                  ease: "easeInOut" 
                }}
              >
                <FileText className="h-6 w-6 text-primary" />
              </motion.div>
              <div className="flex-1">
                <motion.p 
                  className="text-lg font-semibold text-card-foreground font-mono truncate"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  {selectedFile.name}
                </motion.p>
                <motion.p 
                  className="text-sm text-muted-foreground font-mono"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </motion.p>
              </div>
            </div>
            <motion.button
              onClick={onRemoveFile}
              disabled={isLoading}
              className="
                p-2 bg-card border border-border rounded-lg hover:bg-destructive hover:text-destructive-foreground 
                hover:border-destructive transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
              "
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              initial={{ opacity: 0, rotate: 90 }}
              animate={{ opacity: 1, rotate: 0 }}
              transition={{ delay: 0.4, type: "spring", stiffness: 300 }}
            >
              <X className="h-5 w-5" />
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={handleFileInputChange}
        className="hidden"
      />
      
      <motion.div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-20 text-center cursor-pointer 
          transition-all duration-200 ease-in-out
          ${isDragOver 
            ? 'border-primary bg-primary/5' 
            : 'border-border hover:border-primary/60 hover:bg-primary/5'
          }
        `}
        whileHover={{ scale: 1.02 }}
        animate={{ 
          scale: isDragOver ? 1.05 : 1,
          borderColor: isDragOver ? '#007acc' : undefined
        }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <motion.div className="relative z-10">
          <motion.div 
            className={`
              inline-flex items-center justify-center w-24 h-24 border-2 rounded-lg mb-8
              transition-all duration-200 ease-in-out
              ${isDragOver 
                ? 'border-primary bg-primary text-primary-foreground' 
                : 'border-border bg-card text-muted-foreground hover:border-primary hover:bg-primary hover:text-primary-foreground'
              }
            `}
            animate={{ 
              scale: isDragOver ? 1.2 : 1,
              rotate: isDragOver ? [0, -10, 10, 0] : 0,
              y: isDragOver ? [0, -10, 0] : 0
            }}
            transition={{ 
              type: "spring", 
              stiffness: 300, 
              damping: 20,
              rotate: { duration: 0.5, repeat: isDragOver ? Infinity : 0 }
            }}
          >
            <Upload className={`
              transition-all duration-200 ease-in-out
              ${isDragOver ? 'h-12 w-12' : 'h-10 w-10'}
            `} />
          </motion.div>
          
          <motion.h3 
            className={`
              text-3xl font-bold mb-4 transition-all duration-200 font-mono
              ${isDragOver ? 'text-primary' : 'text-foreground'}
            `}
            animate={{ 
              scale: isDragOver ? 1.1 : 1,
              y: isDragOver ? -5 : 0
            }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
          >
            <AnimatePresence mode="wait">
              <motion.span
                key={isDragOver ? 'drop' : 'upload'}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {isDragOver ? 'DROP PDF HERE' : 'UPLOAD PDF'}
              </motion.span>
            </AnimatePresence>
          </motion.h3>
          
          <motion.p 
            className={`
              text-lg mb-8 transition-all duration-200 font-mono
              ${isDragOver ? 'text-card-foreground' : 'text-muted-foreground'}
            `}
            animate={{ opacity: isDragOver ? 1 : 0.8 }}
          >
            <AnimatePresence mode="wait">
              <motion.span
                key={isDragOver ? 'release' : 'drag'}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                {isDragOver 
                  ? 'Release to upload your file' 
                  : 'Drag and drop your PDF file here, or click to browse'
                }
              </motion.span>
            </AnimatePresence>
          </motion.p>
          
          <motion.div 
            className="text-sm text-muted-foreground space-y-1 font-mono"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <p>SUPPORTED FORMAT: PDF</p>
          </motion.div>
        </motion.div>

        {/* Animated Background Effect */}
        <AnimatePresence>
          {isDragOver && (
            <motion.div
              className="absolute inset-0 bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg"
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.3 }}
            />
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
} 