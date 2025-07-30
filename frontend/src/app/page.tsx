'use client';

import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send } from 'lucide-react';
import FileDropzone from '@/components/FileDropzone';
import LoadingSpinner from '@/components/LoadingSpinner';
import JsonViewer from '@/components/JsonViewer';
import ErrorAlert from '@/components/ErrorAlert';

interface ApiResponse {
  success: boolean;
  data?: any;
  error?: string;
}

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [jsonData, setJsonData] = useState<any>(null);
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
      <div className="max-w-6xl mx-auto px-6 py-16">
        {/* Header */}
        <motion.div 
          className="text-center mb-20"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <motion.h1 
            className="text-7xl font-bold text-foreground mb-8 tracking-tight font-mono"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
          >
            MasterFormat PDF Parser
          </motion.h1>
          <motion.p 
            className="text-xl text-muted-foreground max-w-4xl mx-auto leading-relaxed font-mono"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: "easeOut" }}
          >
            Upload your MasterFormat specification PDF and convert it to structured JSON format using AI-powered parsing.
          </motion.p>
        </motion.div>

        {/* Main Content */}
        <div className="space-y-16">
          {/* File Upload Section */}
          <motion.div 
            className="bg-card border border-border rounded-lg p-12"
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
                  className="flex justify-center mt-10"
                  initial={{ opacity: 0, scale: 0.8, y: 20 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.8, y: -20 }}
                  transition={{ duration: 0.5, ease: "easeOut" }}
                >
                  <motion.button
                    onClick={handleSubmit}
                    disabled={isLoading}
                    className="
                      group flex items-center space-x-3 px-8 py-4 bg-primary text-primary-foreground 
                      border-2 border-primary rounded-lg font-mono font-semibold hover:bg-primary/90 
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

          {/* Loading State */}
          <AnimatePresence>
            {isLoading && (
              <motion.div 
                className="flex flex-col items-center justify-center py-20"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              >
                <motion.div
                  initial={{ y: 20 }}
                  animate={{ y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <LoadingSpinner size="lg" />
                </motion.div>
                
                <motion.div
                  className="mt-8 text-center"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <motion.p 
                    className="text-lg text-muted-foreground font-mono mb-2"
                    animate={{ 
                      opacity: [0.7, 1, 0.7],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  >
                    Processing your PDF...
                  </motion.p>
                  
                  <motion.div className="flex items-center justify-center space-x-2">
                    <motion.div
                      className="text-sm text-muted-foreground/60 font-mono"
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      This may take a few moments
                    </motion.div>
                  </motion.div>
                  
                  {/* Progress Indicator */}
                  <motion.div 
                    className="mt-6 w-64 h-1 bg-border rounded-full overflow-hidden mx-auto"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                  >
                    <motion.div
                      className="h-full bg-primary rounded-full"
                      animate={{
                        x: ['-100%', '100%']
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    />
                  </motion.div>
                </motion.div>
              </motion.div>
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
