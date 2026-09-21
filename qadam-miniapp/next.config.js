/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    BACKEND_URL: process.env.BACKEND_URL,
    BOT_USERNAME: process.env.BOT_USERNAME,
  },
};

module.exports = nextConfig;