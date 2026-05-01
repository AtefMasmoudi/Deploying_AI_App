"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";

export default function Home() {
  const [quote, setQuote] = useState<string>("...loading");

  useEffect(() => {
    const evt = new EventSource("/api");
    let buffer = "";

    evt.onmessage = (e) => {
      buffer += e.data;
      setQuote(buffer);
    };
    evt.onerror = () => {
      console.error("SSE error, closing");
      evt.close();
    };

    return () => {
      evt.close();
    };
  }, []);

  return (
    <main
      className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 
                         dark:from-gray-900 dark:to-gray-800"
    >
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center mb-12">
          <h1
            className="text-5xl font-bold bg-gradient-to-r from-purple-600 
                                   to-pink-600 bg-clip-text text-transparent mb-4"
          >
            Daily Motivation
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            Your daily dose of inspiration
          </p>
        </header>

        {/* Content Card */}
        <div className="max-w-3xl mx-auto">
          <div
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 
                                    backdrop-blur-lg bg-opacity-95"
          >
            {quote === "...loading" ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-pulse text-gray-400">
                  Crafting your motivation...
                </div>
              </div>
            ) : (
              <div className="markdown-content text-gray-700 dark:text-gray-300">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                  {quote}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
