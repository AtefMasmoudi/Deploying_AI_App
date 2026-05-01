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
    <main className="p-8 font-sans">
      <h1 className="text-3xl font-bold mb-4">Daily Motivation</h1>
      <div
        className="w-full max-w-2xl p-6 bg-white dark:bg-gray-800 
                            border border-gray-300 dark:border-gray-600 
                            rounded-lg shadow-md"
      >
        <div className="prose prose-gray dark:prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
            {quote}
          </ReactMarkdown>
        </div>
      </div>
    </main>
  );
}
