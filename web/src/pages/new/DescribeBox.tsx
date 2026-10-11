import { useRef, useState } from "react"
import { LoaderCircle, Mic, Square } from "lucide-react"
import { parseIntake, transcribe, type IntakeParseResponse } from "@/api"
import { Button } from "@/components/ui/button"
import { useLang, useT } from "@/i18n"

export default function DescribeBox({ onParsed }: { onParsed: (parsed: IntakeParseResponse) => void }) {
  const t = useT()
  const lang = useLang()
  const [text, setText] = useState("")
  const [busy, setBusy] = useState(false)
  const [failed, setFailed] = useState(false)
  const [voiceFailed, setVoiceFailed] = useState(false)
  const [listening, setListening] = useState(false)
  const [hearing, setHearing] = useState(false)
  const recorder = useRef<MediaRecorder | null>(null)

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

  async function startVoice() {
    setVoiceFailed(false)
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream)
      const chunks: Blob[] = []
      rec.ondataavailable = (e) => chunks.push(e.data)
      rec.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop())
        setListening(false)
        setHearing(true)
        try {
          const { text: heard } = await transcribe(new Blob(chunks, { type: rec.mimeType }), lang)
          setText((old) => [old.trim(), heard].filter(Boolean).join(" "))
        } catch {
          setVoiceFailed(true)
        } finally {
          setHearing(false)
        }
      }
      rec.start()
      recorder.current = rec
      setListening(true)
    } catch {
      setVoiceFailed(true)
    }
  }

  const VoiceIcon = hearing ? LoaderCircle : listening ? Square : Mic

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
      {(failed || voiceFailed) && (
        <p role="alert" className="text-sm text-destructive">
          {t(voiceFailed ? "wizard.describe.voiceError" : "wizard.describe.error")}
        </p>
      )}
      <div className="flex gap-2">
        {"MediaRecorder" in window && (
          <Button
            variant="outline"
            className="h-12 flex-1 gap-2"
            disabled={hearing}
            aria-pressed={listening}
            onClick={() => (listening ? recorder.current?.stop() : startVoice())}
          >
            <VoiceIcon aria-hidden="true" className={`size-5 ${hearing ? "animate-spin" : ""}`} />
            {t(hearing ? "wizard.describe.hearing" : listening ? "wizard.describe.stop" : "wizard.describe.speak")}
          </Button>
        )}
        <Button variant="outline" className="h-12 flex-1" disabled={busy || listening || hearing || !text.trim()} onClick={go}>
          {t("wizard.describe.go")}
        </Button>
      </div>
    </div>
  )
}
