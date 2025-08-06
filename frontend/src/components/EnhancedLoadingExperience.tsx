'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Sparkles, FileText, Cpu, Database } from 'lucide-react';

interface EnhancedLoadingExperienceProps {
  portfolioUrl?: string;
}

// Loading tips that cycle through
const loadingTips = [
  {
    icon: FileText,
    title: "Processing Document",
    message: "Extracting text and structure from your PDF specification"
  },
  {
    icon: Cpu,
    title: "Chunking Content", 
    message: "Breaking document into overlapping sections to preserve context"
  },
  {
    icon: Database,
    title: "Analyzing Tables",
    message: "Identifying and processing technical specifications tables"
  },
  {
    icon: Sparkles,
    title: "AI Processing",
    message: "Converting content to structured JSON format"
  },
  {
    icon: FileText,
    title: "Deduplicating Data",
    message: "Removing redundant information and optimizing output"
  },
  {
    icon: Database,
    title: "Final Assembly",
    message: "Combining all sections into cohesive MasterFormat structure"
  }
];

export default function EnhancedLoadingExperience({ 
  portfolioUrl = "https://anirudhvasudevan.netlify.app/" 
}: EnhancedLoadingExperienceProps) {
  const [currentTipIndex, setCurrentTipIndex] = useState(0);

  // Cycle through tips every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTipIndex((prev) => (prev + 1) % loadingTips.length);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const currentTip = loadingTips[currentTipIndex];
  const IconComponent = currentTip.icon;

  return (
    <motion.div 
      className="flex flex-col items-center justify-center py-8 sm:py-12 lg:py-16 max-w-4xl mx-auto space-y-4 sm:space-y-6 lg:space-y-8 px-4 sm:px-6"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -40 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
    >
      {/* Main Processing Status Card */}
      <motion.div
        className="relative overflow-hidden bg-white dark:bg-[#1e1e1e] border border-slate-200 dark:border-slate-600 rounded-xl sm:rounded-2xl p-4 sm:p-6 lg:p-8 shadow-xl max-w-2xl w-full"
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        {/* Background decoration */}
        <div className="absolute top-0 left-0 w-full h-1 bg-slate-300 dark:bg-slate-500"></div>
        
        <div className="flex flex-col items-center text-center space-y-3 sm:space-y-4">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentTipIndex}
              className="flex flex-col items-center space-y-3 sm:space-y-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.6 }}
            >
              {/* Animated Icon */}
              <motion.div
                className="p-3 sm:p-4 bg-slate-100 dark:bg-slate-700 rounded-full"
                animate={{ 
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0]
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <IconComponent className="h-6 w-6 sm:h-7 sm:w-7 lg:h-8 lg:w-8 text-slate-600 dark:text-slate-200" />
              </motion.div>
              
              {/* Title */}
              <h3 className="text-lg sm:text-xl font-semibold text-foreground">
                {currentTip.title}
              </h3>
              
              {/* Message */}
              <p className="text-sm sm:text-base text-muted-foreground leading-relaxed max-w-xs sm:max-w-md px-2 sm:px-0">
                {currentTip.message}
              </p>
            </motion.div>
          </AnimatePresence>
          
          {/* Processing dots indicator */}
          <div className="flex justify-center space-x-1.5 sm:space-x-2 mt-4 sm:mt-6">
            {loadingTips.map((_, index) => (
              <motion.div
                key={index}
                className={`h-1.5 w-1.5 sm:h-2 sm:w-2 rounded-full transition-colors duration-300 ${
                  index === currentTipIndex ? 'bg-slate-700 dark:bg-slate-200' : 'bg-slate-300 dark:bg-slate-600'
                }`}
                animate={{
                  scale: index === currentTipIndex ? [1, 1.2, 1] : 1
                }}
                transition={{
                  duration: 0.3
                }}
              />
            ))}
          </div>
        </div>
      </motion.div>

      {/* Portfolio Link */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <motion.a
          href={portfolioUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="
            group inline-flex items-center space-x-2 sm:space-x-3 px-4 py-3 sm:px-6 sm:py-4
            bg-slate-200 dark:bg-[#1e1e1e] border border-slate-300 dark:border-slate-600 
            rounded-lg sm:rounded-xl font-medium text-sm sm:text-base text-slate-700 dark:text-slate-300
            hover:bg-slate-300 dark:hover:bg-slate-800 hover:border-slate-400 dark:hover:border-slate-500
            hover:shadow-lg transition-all duration-300
          "
          whileHover={{ scale: 1.02, y: -2 }}
          whileTap={{ scale: 0.98 }}
        >
          <motion.div
            animate={{ 
              rotate: [0, 360],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 text-slate-500 dark:text-slate-400" />
          </motion.div>
          <span className="group-hover:text-slate-800 dark:group-hover:text-slate-200 transition-colors">
            While you wait, check out my <span className="text-slate-300 dark:text-slate-400">portfolio</span>
          </span>
          <ExternalLink className="h-3 w-3 sm:h-4 sm:w-4 text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-200 transition-colors" />
        </motion.a>
      </motion.div>

      {/* Subtle footer info */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <motion.p
          className="text-xs sm:text-sm text-muted-foreground/70 max-w-xs sm:max-w-md px-4 sm:px-0"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 6, repeat: Infinity }}
        >
          Processing time varies based on document complexity • Powered by AI
        </motion.p>
      </motion.div>
    </motion.div>
  );
}
