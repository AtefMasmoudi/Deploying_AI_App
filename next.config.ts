import type { NextConfig } from "next";

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: "/api",
        destination: "http://127.0.0.1:8000/api",
      },
    ];
  },
};

export default nextConfig;
