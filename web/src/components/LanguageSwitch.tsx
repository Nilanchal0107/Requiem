import { Languages } from "lucide-react"
import { setLang, useLang } from "@/i18n"
import type { Lang } from "@/i18n/resolve"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

// Each language is written in its own script, so it is readable before it is chosen.
const OPTIONS: { lang: Lang; short: string; name: string }[] = [
  { lang: "en", short: "EN", name: "English" },
  { lang: "hi", short: "हि", name: "हिन्दी" },
  { lang: "mr", short: "म", name: "मराठी" },
]

export function LanguageSwitch() {
  const lang = useLang()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="h-12 min-w-12 px-3" aria-label="Language / भाषा">
          <Languages />
          {OPTIONS.find((o) => o.lang === lang)?.short}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuRadioGroup value={lang} onValueChange={(v) => setLang(v as Lang)}>
          {OPTIONS.map((o) => (
            <DropdownMenuRadioItem key={o.lang} value={o.lang} className="h-12 text-base">
              {o.name}
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
