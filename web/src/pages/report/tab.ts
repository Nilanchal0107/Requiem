export const TABS = ["explanation", "numbers", "bank"] as const;

export type Tab = (typeof TABS)[number];

// Anything that isn't a known tab name falls back to the default, so a hand-edited URL never breaks the page.
export function parseTab(value: string | null): Tab {
  return (TABS as readonly string[]).includes(value ?? "") ? (value as Tab) : "explanation";
}
