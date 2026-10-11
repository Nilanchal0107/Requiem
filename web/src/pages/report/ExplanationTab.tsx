import { useT } from "@/i18n"
import type { components } from "@/types/contracts"

type Explanation = components["schemas"]["Explanation"]

export type ExplanationTabProps = {
  explanation: Explanation | null
}

export function ExplanationTab({ explanation }: ExplanationTabProps) {
  const t = useT()
  if (!explanation) return <p className="text-sm">{t("report.notReady")}</p>
  return (
    <ul className="flex flex-col gap-4">
      {explanation.sections.map((section) => (
        <li key={section.key} className="flex flex-col gap-1">
          <h2 className="text-base font-semibold">{section.title}</h2>
          <p className="text-sm">{section.text}</p>
        </li>
      ))}
    </ul>
  )
}
