"use client";

import Link from "next/link";
import { SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";
import { Show } from "@clerk/nextjs";

export default function Home() {
  return (
    <main
      className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100
                     dark:from-gray-900 dark:to-gray-800"
    >
      <div className="container mx-auto px-4 py-12">
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            DailyMotivation
          </h1>
          <div>
            <Show when="signed-out">
              <SignInButton mode="modal">
                <button
                  className="bg-purple-600 hover:bg-purple-700 text-white
                                   font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Sign In
                </button>
              </SignInButton>
            </Show>
            <Show when="signed-in">
              <div className="flex items-center gap-4">
                <Link
                  href="/product"
                  className="bg-purple-600 hover:bg-purple-700 text-white
                             font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>
                <UserButton />
              </div>
            </Show>
          </div>
        </nav>

        <div className="text-center py-24">
          <h2
            className="text-6xl font-bold bg-gradient-to-r from-purple-600
                         to-pink-600 bg-clip-text text-transparent mb-6"
          >
            Start Your Day
            <br />
            With Inspiration
          </h2>
          <p
            className="text-xl text-gray-600 dark:text-gray-400 mb-12
                        max-w-2xl mx-auto"
          >
            Get your daily dose of AI-powered motivation delivered in real-time.
            Start your day inspired.
          </p>
          <Show when="signed-out">
            <SignInButton mode="modal">
              <button
                className="bg-gradient-to-r from-purple-600 to-pink-600
                                 hover:from-purple-700 hover:to-pink-700
                                 text-white font-bold py-4 px-8 rounded-xl
                                 text-lg transition-all transform hover:scale-105"
              >
                Get Started Free
              </button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <Link href="/product">
              <button
                className="bg-gradient-to-r from-purple-600 to-pink-600
                                 hover:from-purple-700 hover:to-pink-700
                                 text-white font-bold py-4 px-8 rounded-xl
                                 text-lg transition-all transform hover:scale-105"
              >
                Get Your Motivation
              </button>
            </Link>
          </Show>
        </div>
      </div>
    </main>
  );
}
