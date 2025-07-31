'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send } from 'lucide-react';
import FileDropzone from '@/components/FileDropzone';
import EnhancedLoadingExperience from '@/components/EnhancedLoadingExperience';
import JsonViewer from '@/components/JsonViewer';
import ErrorAlert from '@/components/ErrorAlert';

interface ParsedData {
  section?: string;
  name?: string;
  part1?: {
    partItems?: Array<{
      index?: string;
      text?: string;
      children?: unknown;
      tables?: unknown[];
    }>;
  };
  part2?: {
    partItems?: Array<{
      index?: string;
      text?: string;
      children?: unknown;
      tables?: unknown[];
    }>;
  };
  part3?: {
    partItems?: Array<{
      index?: string;
      text?: string;
      children?: unknown;
      tables?: unknown[];
    }>;
  };
}

interface ApiResponse {
  success: boolean;
  data?: ParsedData;
  error?: string;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [jsonData, setJsonData] = useState<ParsedData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setError(null);
    setJsonData(null);
  }, []);

  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
    setError(null);
    setJsonData(null);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);
    setJsonData(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await fetch('http://localhost:8000/parse', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ApiResponse = await response.json();
      
      if (result.success && result.data) {
        setJsonData(result.data);
      } else {
        throw new Error(result.error || 'Failed to parse PDF');
      }
    } catch (err) {
      console.error('Error parsing PDF:', err);
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  }, [selectedFile]);

  const handleErrorClose = useCallback(() => {
    setError(null);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12 lg:py-16">
        {/* Header */}
        <motion.div 
          className="text-center mb-8 sm:mb-12 lg:mb-20"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.h1 
            className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-foreground mb-4 sm:mb-6 lg:mb-8 tracking-tight font-mono"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          >
            MasterFormat PDF Parser
          </motion.h1>
          <motion.p 
            className="text-sm sm:text-base lg:text-xl text-muted-foreground max-w-xs sm:max-w-2xl lg:max-w-4xl mx-auto leading-relaxed font-mono px-2 sm:px-0"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          >
            Upload your MasterFormat specification PDF and convert it to structured JSON format using AI-powered parsing.
          </motion.p>
        </motion.div>

        {/* Main Content */}
        <div className="space-y-8 sm:space-y-12 lg:space-y-16">
          {/* File Upload Section */}
          <motion.div 
            className="bg-card border border-border rounded-lg p-4 sm:p-6 lg:p-12"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6, ease: "easeOut" }}
          >
            <FileDropzone
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile}
              onRemoveFile={handleRemoveFile}
              isLoading={isLoading}
            />

            {/* Submit Button */}
            <AnimatePresence>
              {selectedFile && (
                <motion.div 
                  className="flex justify-center mt-6 sm:mt-8 lg:mt-10"
                  initial={{ opacity: 0, scale: 0.8, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, y: -20 }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                >
                  <motion.button
                    onClick={handleSubmit}
                    disabled={isLoading}
                    className="
                      group flex items-center space-x-2 sm:space-x-3 px-4 py-3 sm:px-6 lg:px-8 sm:py-4 bg-primary text-primary-foreground 
                      border-2 border-primary rounded-lg font-mono font-semibold text-sm sm:text-base hover:bg-primary/90 
                      disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200
                    "
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    transition={{ type: "spring", stiffness: 400, damping: 17 }}
                  >
                    <AnimatePresence mode="wait">
                      {isLoading ? (
                        <motion.div
                          key="loading"
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 10 }}
                          className="flex items-center space-x-3"
                        >
                          <span>PROCESSING...</span>
                        </motion.div>
                      ) : (
                        <motion.div
                          key="ready"
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 10 }}
                          className="flex items-center space-x-3"
                        >
                          <motion.div
                            animate={{ x: [0, 3, 0] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                          >
                            <Send className="h-5 w-5" />
                          </motion.div>
                          <span>Parse PDF</span>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.button>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

          {/* Error Display */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
              >
                <ErrorAlert message={error} onClose={handleErrorClose} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Enhanced Loading State */}
          <AnimatePresence>
            {isLoading && (
              <EnhancedLoadingExperience portfolioUrl="https://anirudhvasudevan.netlify.app/" />
            )}
          </AnimatePresence>

          {/* JSON Output */}
          <AnimatePresence>
            {jsonData && !isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 40, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -40, scale: 0.95 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <JsonViewer data={jsonData} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
