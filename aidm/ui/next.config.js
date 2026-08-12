/** @type {import('next').NextConfig} */
// ★ P0-08: 静态导出——Docker 阶段2 直接 COPY /app/ui/out 提供产物，
// 不依赖 Next.js server；干净 checkout 下 npm run build 必须产出 out/
const nextConfig = {
  reactStrictMode: true,
  output: "export",
  images: { unoptimized: true },
};
module.exports = nextConfig;