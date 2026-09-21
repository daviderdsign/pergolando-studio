/**
 * Next.js's `basePath` config auto-prefixes <Link>/useRouter navigation, but
 * not plain fetch()/img-src calls — those need this applied by hand. Empty
 * in local dev (STUDIO_BASE_PATH unset), "/studio" on the NAS build.
 */
export function apiPath(path: string): string {
  const base = process.env.NEXT_PUBLIC_BASE_PATH ?? "";
  return `${base}${path}`;
}
