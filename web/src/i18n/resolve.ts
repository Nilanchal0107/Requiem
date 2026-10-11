// Pure lookup, no Vite or DOM APIs, so the node check can run it.
export const LANGS = ["en", "hi", "mr"] as const;
export type Lang = (typeof LANGS)[number];
export type Catalog = Record<string, string>;

// Missing keys fall back to en; a key nobody has is shown as its own name.
export function translate(catalogs: Record<Lang, Catalog>, lang: Lang, key: string): string {
  return catalogs[lang][key] ?? catalogs.en[key] ?? key;
}
