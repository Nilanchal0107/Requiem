import { useT } from "@/i18n"

// The twelve sections of the Bank DPR, in the order from the PRD (F5).
const SECTION_COUNT = 12

export function BankTab() {
  const t = useT()
  return (
    <ol className="flex flex-col gap-2 text-sm">
      {Array.from({ length: SECTION_COUNT }, (_, i) => (
        <li key={i}>{t(`report.bank.section.${i + 1}`)}</li>
      ))}
    </ol>
  )
}
