import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || "https://web-production-e9cd4.up.railway.app",
    // Force cache bust for chart fix
    NEXT_PUBLIC_BUILD_VERSION: "2.0.0",
  },
  // Ensure fresh builds
  generateBuildId: async () => {
    return `build-${Date.now()}-${Math.random().toString(36).substring(7)}`
  },
};

export default nextConfig;


