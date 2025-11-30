import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://web-production-e9cd4.up.railway.app",
    // Force cache bust for chart fix - UPDATE THIS TO CLEAR CACHE
    NEXT_PUBLIC_BUILD_VERSION: `4.0.0-${Date.now()}`,
  },
  // Ensure fresh builds
  generateBuildId: async () => {
    return `build-${Date.now()}-${Math.random().toString(36).substring(7)}`
  },
  // Optimize for client-side rendering
  reactStrictMode: true,
  // Disable SSR for chart components that use browser APIs
  experimental: {
    optimizePackageImports: ['lightweight-charts'],
  },
};

export default nextConfig;


