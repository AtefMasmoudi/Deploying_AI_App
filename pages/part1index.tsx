"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [quote, setQuote] = useState<string>("...loading");

  useEffect(() => {
    fetch("/api")
      .then((res) => res.text())
      .then(setQuote)
      .catch((err) => setQuote("Error: " + err.message));
  }, []);

  return (
    <main className="p-8 font-sans">
      <h1 className="text-3xl font-bold mb-4">Daily Motivation</h1>
      <div
        className="w-full max-w-2xl p-6 bg-white dark:bg-gray-800 
                            border border-gray-300 dark:border-gray-600 
                            rounded-lg shadow-sm"
      >
        <p className="text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
          {quote}
        </p>
      </div>
    </main>
  );
}
