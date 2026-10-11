import type { components } from "../types/contracts.ts"
import type { Lang } from "../i18n/resolve.ts"

type Figure = components["schemas"]["Figure"]

const LOCALE: Record<Lang, string> = { en: "en-IN", hi: "hi-IN-u-nu-deva", mr: "mr-IN-u-nu-deva" }
// Indian grouping (lakh/crore) comes from the *-IN locales; hi/mr add Devanagari digits.
const num = (n: number, lang: Lang, max = 2) =>
  new Intl.NumberFormat(LOCALE[lang], { maximumFractionDigits: max }).format(n)

/** Formats a Figure's value: Indian grouping (en-IN), Devanagari digits for hi/mr (-u-nu-deva). Bank View always passes "en". */
export function formatFigure(figure: Figure, lang: Lang): string {
  const n = num(figure.value, lang)
  // Only money and percent carry a mark; months/count read in the sentence ("{{emi}} per month", "in {{payback_months}} months").
  if (figure.unit === "INR") return `₹${n}`
  if (figure.unit === "%") return `${n}%`
  return n
}

const WORDS: Record<Lang, { thousand: string; lakh: string; crore: string }> = {
  en: { thousand: "thousand", lakh: "lakh", crore: "crore" },
  hi: { thousand: "हज़ार", lakh: "लाख", crore: "करोड़" }, // needs native review
  mr: { thousand: "हजार", lakh: "लाख", crore: "कोटी" }, // needs native review
}

/** Words line under a money input: "₹1 lakh" / "₹1 लाख". */
export function formatMoneyWords(amount: number, lang: Lang): string {
  const w = WORDS[lang]
  const [div, word] = amount >= 1e7 ? [1e7, w.crore] : amount >= 1e5 ? [1e5, w.lakh] : amount >= 1e3 ? [1e3, w.thousand] : [1, ""]
  return `₹${num(amount / div, lang)}${word && ` ${word}`}`
}

/** A bare value in a unit, for places with no Figure to hand (tables, scheme terms). */
export const formatValue = (value: number, unit: Figure["unit"], lang: Lang) =>
  formatFigure({ id: "", label: "", value, unit, source: "computed" }, lang)

/** Plain rupee amount with the language's grouping, for tables and chart tables. */
export const formatInr = (value: number, lang: Lang) => formatValue(value, "INR", lang)

/** "11 Oct 2026" / "११ ऑक्टो. २०२६" from an ISO date. */
export const formatDate = (iso: string, lang: Lang) =>
  new Intl.DateTimeFormat(LOCALE[lang], { dateStyle: "medium", timeZone: "UTC" }).format(new Date(iso))

/** Headline form: lakh/crore words from one lakh up ("₹4.17 lakh"), exact below that, so EMIs read "₹9,632". */
export function formatHeadline(figure: Figure, lang: Lang): string {
  return figure.unit === "INR" && figure.value >= 1e5 ? formatMoneyWords(figure.value, lang) : formatFigure(figure, lang)
}

/** Short chart label: "₹1.6L" / "₹१.६ लाख". */
export const formatCompact = (value: number, lang: Lang) =>
  `₹${new Intl.NumberFormat(LOCALE[lang], { notation: "compact", maximumFractionDigits: 1 }).format(value)}`
