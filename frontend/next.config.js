/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // In development, proxy to the backend container
    // In production, the API URL should be configured via environment variables
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';

    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
  // Enable static optimization
  output: 'standalone',
};

module.exports = nextConfig;