// @ts-check
import js from "@eslint/js";
import tseslint from "typescript-eslint";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  prettier,
  {
    ignores: ["**/dist/**", "**/.next/**", "**/node_modules/**", "**/storage/**"],
  },
  {
    // pergolando-blender-service: plain Node.js (node:http, no framework,
    // no build step — see 3d/NOTES.md) — the root config above has no
    // Node globals at all (apps/studio is Next.js/browser), so every use
    // of process/console/Buffer was flagged as undefined.
    files: ["pergolando-blender-service/**/*.js"],
    languageOptions: {
      globals: {
        process: "readonly",
        console: "readonly",
        Buffer: "readonly",
        require: "readonly",
        module: "readonly",
        __dirname: "readonly",
        __filename: "readonly",
      },
    },
  },
);
