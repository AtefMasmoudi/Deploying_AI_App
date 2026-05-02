"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useAuth } from "@clerk/nextjs";
import { fetchEventSource } from "@microsoft/fetch-event-source";

export default function Product() {
  const { getToken, isLoaded, isSignedIn } = useAuth();
  const [quote, setQuote] = useState<string>("...loading");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;

    let buffer = "";
    const controller = new AbortController();

    (async () => {
      try {
        const jwt = await getToken({ template: "backend" });
        if (!jwt) {
          setError("Authentication required");
          return;
        }

        await fetchEventSource("/api", {
          headers: { Authorization: `Bearer ${jwt}` },
          signal: controller.signal,
          async onopen(response) {
            if (
              response.ok &&
              response.headers
                .get("content-type")
                ?.includes("text/event-stream")
            ) {
              setError(null);
              return;
            }
            setError(`Server returned ${response.status}. Check Vercel logs.`);
          },
          onmessage(ev) {
            buffer += ev.data;
            setQuote(buffer);
          },
          onerror(err) {
            console.error("SSE error:", err);
            setError("Connection error. Please refresh.");
            return undefined;
          },
          onclose() {
            console.log("SSE connection closed");
          },
        });
      } catch (err: any) {
        setError(`Failed: ${err.message}`);
      }
    })();

    return () => controller.abort();
  }, [isLoaded, isSignedIn, getToken]);

  if (!isLoaded) {
    return (
      <main
        className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100
                       dark:from-gray-900 dark:to-gray-800"
      >
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-pulse text-gray-400">Loading...</div>
        </div>
      </main>
    );
  }

  if (!isSignedIn) {
    return (
      <main
        className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100
                       dark:from-gray-900 dark:to-gray-800"
      >
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Please Sign In</h1>
            <p className="text-gray-600">
              Sign in to get your daily motivation.
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main
      className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100
                     dark:from-gray-900 dark:to-gray-800"
    >
      <div className="container mx-auto px-4 py-12">
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

        {error && (
          <div className="max-w-3xl mx-auto mb-6">
            <div
              className="bg-red-50 dark:bg-red-900/20 border border-red-200
                            dark:border-red-800 rounded-lg p-4 text-red-700
                            dark:text-red-300"
            >
              {error}
            </div>
          </div>
        )}

        <div className="max-w-3xl mx-auto">
          <div
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8
                          backdrop-blur-lg bg-opacity-95"
          >
            {quote === "...loading" && !error ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-pulse text-gray-400">
                  Crafting your motivation...
                </div>
              </div>
            ) : (
              <div className="mprose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
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
