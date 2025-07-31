'use client';

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from 'react';

interface JsonViewerProps {
  data: Record<string, unknown> | unknown | null;
  title?: string;
}

export default function JsonViewer({ data, title = 'Parsed JSON Output' }: JsonViewerProps) {
  const [copied, setCopied] = useState(false);
  const jsonString = JSON.stringify(data, null, 2);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(jsonString);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto">
      <div className="bg-[#1e1e1e] border border-[#3c3c3c] rounded-2xl overflow-hidden shadow-2xl">
        {/* VS Code-style header */}
        <div className="px-6 py-4 bg-[#2d2d30] border-b border-[#3c3c3c] flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex space-x-2">
              <div className="w-3 h-3 bg-[#ff5f56] rounded-full"></div>
              <div className="w-3 h-3 bg-[#ffbd2e] rounded-full"></div>
              <div className="w-3 h-3 bg-[#27ca3f] rounded-full"></div>
            </div>
            <div className="flex items-center space-x-2 text-[#cccccc]">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm0 4a1 1 0 011-1h12a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1V8z" clipRule="evenodd" />
              </svg>
              <span className="text-sm font-medium">{title}</span>
            </div>
          </div>
          
          <button
            onClick={handleCopy}
            className="
              flex items-center space-x-2 px-3 py-1.5 bg-[#007acc] text-white rounded-md 
              hover:bg-[#005a9e] transition-all duration-200 text-sm font-medium
              transform hover:scale-105
            "
          >
            {copied ? (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Copied!</span>
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                <span>Copy</span>
              </>
            )}
          </button>
        </div>

        {/* JSON Content with VS Code Dark Theme */}
        <div className="relative bg-[#1e1e1e]">
          <div className="max-h-[700px] overflow-auto vscode-scrollbar">
            <SyntaxHighlighter
              language="json"
              style={vscDarkPlus}
              customStyle={{
                margin: 0,
                padding: '2rem',
                backgroundColor: '#1e1e1e',
                fontSize: '0.9rem',
                lineHeight: '1.8',
                fontFamily: '"Cascadia Code", "Fira Code", "SF Mono", Monaco, "Roboto Mono", Consolas, "Courier New", monospace',
                border: 'none',
                borderRadius: 0,
              }}
              showLineNumbers={true}
              wrapLines={false}
              lineNumberStyle={{
                color: '#858585',
                paddingRight: '1.5rem',
                marginRight: '1.5rem',
                borderRight: '1px solid #3c3c3c',
                minWidth: '3rem',
                textAlign: 'right',
                userSelect: 'none',
                fontSize: '0.85rem',
                backgroundColor: '#1e1e1e',
              }}
              codeTagProps={{
                style: {
                  fontFamily: '"Cascadia Code", "Fira Code", "SF Mono", Monaco, "Roboto Mono", Consolas, "Courier New", monospace',
                }
              }}
            >
              {jsonString}
            </SyntaxHighlighter>
          </div>
        </div>
      </div>
    </div>
  );
} 