/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@sprint-radar/ui', '@sprint-radar/design-tokens'],
  
  // API proxy to Python backend
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/api/v1/:path*', // Python backend
      },
    ]
  },
}

module.exports = nextConfig