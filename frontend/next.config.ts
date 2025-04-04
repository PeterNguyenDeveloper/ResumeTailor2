/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    reactStrictMode: true,
    // Ensure PostCSS processing happens during build
    webpack: (config:any) => {
        return config;
    },
    async rewrites() {
        return [
            {
                source: '/api/:path*',
                destination: 'http://137.184.12.12:5000/api/:path*',
            },
        ];
    },
};

export default nextConfig;

