"use client";

// app/page.tsx

import Link from "next/link";
import { SignInButton, Show, UserButton } from "@clerk/nextjs";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DailyMotivation — AI-Powered Inspiration",
  description:
    "Get your daily dose of AI-powered motivation delivered in real-time.",
};

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            DailyMotivation
          </h1>
          <div className="flex items-center gap-4">
            <Show when="signed-out">
              <SignInButton mode="modal">
                <button className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </Show>
            <Show when="signed-in">
              <Link
                href="/product"
                className="bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
              >
                Go to App
              </Link>
              <UserButton showName />
            </Show>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-24">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-6">
            Start Your Day
            <br />
            With Inspiration
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
            Harness the power of AI to fuel your journey in production AI
            engineering
          </p>

          {/* Pricing Preview */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 max-w-sm mx-auto mb-8">
            <h3 className="text-2xl font-bold mb-2">Premium Subscription</h3>
            <p className="text-4xl font-bold text-purple-600 mb-2">
              $10<span className="text-lg text-gray-600">/month</span>
            </p>
            <ul className="text-left text-gray-600 dark:text-gray-400 mb-6 space-y-2">
              <li>✓ Unlimited motivation generation</li>
              <li>✓ Advanced AI models (Llama 3.1)</li>
              <li>✓ Real-time streaming</li>
              <li>✓ Priority support</li>
            </ul>
          </div>

          <Show when="signed-out">
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Start Your Free Trial
              </button>
            </SignInButton>
          </Show>
          <Show when="signed-in">
            <Link href="/product">
              <button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Access Premium Features
              </button>
            </Link>
          </Show>
        </div>
      </div>
    </main>
  );
}
