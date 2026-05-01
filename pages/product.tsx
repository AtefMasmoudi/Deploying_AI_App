"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useAuth } from "@clerk/nextjs";
import { fetchEventSource } from "@microsoft/fetch-event-source";

export default function Product() {
  const { getToken } = useAuth();
  const [idea, setIdea] = useState<string>("…loading");

  useEffect(() => {
    let buffer = "";

    (async () => {
      try {
        const jwt = await getToken();

        if (!jwt) {
          setIdea("Authentication required");
          return;
        }

        await fetchEventSource("http://localhost:8000/api", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${jwt}`,
          },

          onmessage(ev) {
            buffer += ev.data;
            setIdea(buffer);
          },

          onerror(err) {
            console.error("SSE error:", err);
          },
        });
      } catch (err) {
        console.error("Request failed:", err);
        setIdea("Failed to connect to server");
      }
    })();
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
            Business Idea Generator
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-lg">
            AI-powered innovation at your fingertips
          </p>
        </header>

        {/* Content */}
        <div className="max-w-3xl mx-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            {idea === "…loading" ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-pulse text-gray-400">
                  Generating your business idea...
                </div>
              </div>
            ) : (
              <div className="text-gray-700 dark:text-gray-300">
                <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                  {idea}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
