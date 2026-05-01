"use client";

import Link from "next/link";
import { SignInButton, UserButton, useUser } from "@clerk/nextjs";

export default function Home() {
  const { isSignedIn, isLoaded } = useUser();

  //if (!isLoaded) return null; // avoid flicker
  if (!isLoaded) {
    return <div className="text-white p-10">Loading authentication...</div>;
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            IdeaGen
          </h1>

          <div>
            {!isSignedIn ? (
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            ) : (
              <div className="flex items-center gap-4">
                <Link
                  href="/product"
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>

                <UserButton />
              </div>
            )}
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-24">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Generate Your Next
            <br />
            Big Business Idea
          </h2>

          <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Harness the power of AI to discover innovative business
            opportunities tailored for the AI agent economy
          </p>

          {!isSignedIn ? (
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Get Started Free
              </button>
            </SignInButton>
          ) : (
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Generate Ideas Now
              </button>
            </Link>
          )}
        </div>
      </div>
    </main>
  );
}
