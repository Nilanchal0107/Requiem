import { useState } from "react"
import { parseIntake, type IntakeParseResponse } from "@/api"
import { Button } from "@/components/ui/button"
import { useLang, useT } from "@/i18n"

export default function DescribeBox({ onParsed }: { onParsed: (parsed: IntakeParseResponse) => void }) {
  const t = useT()
  const lang = useLang()
  const [text, setText] = useState("")
  const [busy, setBusy] = useState(false)
  const [failed, setFailed] = useState(false)

  async function go() {
    setBusy(true)
    setFailed(false)
    try {
      onParsed(await parseIntake(text.trim(), lang))
    } catch {
      setFailed(true)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label htmlFor="describe" className="font-semibold">
        {t("wizard.describe")}
      </label>
      <textarea
        id="describe"
        rows={3}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={t("wizard.describe.placeholder")}
        className="w-full rounded-lg border border-border-strong bg-background p-3 text-base outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50"
      />
      {failed && (
        <p role="alert" className="text-sm text-destructive">
          {t("wizard.describe.error")}
        </p>
      )}
      <Button variant="outline" className="h-12" disabled={busy || !text.trim()} onClick={go}>
        {t("wizard.describe.go")}
      </Button>
    </div>
  )
}
