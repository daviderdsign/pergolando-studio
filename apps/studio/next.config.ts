import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Only set for the NAS build, where Studio is served at
  // pergolando.rdsign-app.it/studio behind Cloudflare path routing — local
  // dev keeps STUDIO_BASE_PATH unset and stays mounted at "/".
  basePath: process.env.STUDIO_BASE_PATH || undefined,
  // pdfjs-dist ships its worker as a co-located file it dynamically resolves
  // at runtime; bundling it breaks that resolution, so it must run as a
  // plain Node dependency instead (server-side PDF text extraction only,
  // never loaded in the browser).
  serverExternalPackages: ["pdfjs-dist"],
};

export default nextConfig;
