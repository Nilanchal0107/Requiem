import { useSyncExternalStore } from "react";
import { LANGS, translate, type Catalog, type Lang } from "./resolve";

// One JSON file per screen per language, merged into one flat dotted-key catalogue per language.
const files = import.meta.glob<Catalog>("./*/*.json", { eager: true, import: "default" });
const catalogs = { en: {}, hi: {}, mr: {} } as Record<Lang, Catalog>;
for (const [path, messages] of Object.entries(files)) {
  const lang = path.split("/")[1];
  if ((LANGS as readonly string[]).includes(lang)) Object.assign(catalogs[lang as Lang], messages);
}

const STORAGE_KEY = "requiem.lang";
const listeners = new Set<() => void>();

function readStoredLang(): Lang {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && (LANGS as readonly string[]).includes(stored)) return stored as Lang;
  } catch {
    // Storage blocked (private window, cleared site data): use the default.
  }
  return "en";
}

let current: Lang = readStoredLang();
document.documentElement.lang = current;

export function setLang(lang: Lang) {
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // Not persisted; the choice still applies for this page view.
  }
  current = lang;
  document.documentElement.lang = lang;
  listeners.forEach((notify) => notify());
}

export function t(key: string): string {
  return translate(catalogs, current, key);
}

// Re-renders the calling component when the language changes.
export function useT(): (key: string) => string {
  const lang = useSyncExternalStore(
    (notify) => {
      listeners.add(notify);
      return () => listeners.delete(notify);
    },
    () => current,
  );
  return (key) => translate(catalogs, lang, key);
}
