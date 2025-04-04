/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    reactStrictMode: true,
    swcMinify: true,
    // Ensure PostCSS processing happens during build
    webpack: (config:any) => {
        return config;
    },
};

export default nextConfig;

