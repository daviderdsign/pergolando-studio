import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // pdfjs-dist ships its worker as a co-located file it dynamically resolves
  // at runtime; bundling it breaks that resolution, so it must run as a
  // plain Node dependency instead (server-side PDF text extraction only,
  // never loaded in the browser).
  serverExternalPackages: ["pdfjs-dist"],
};

export default nextConfig;
