import { useState } from "react"
import { MapPin } from "lucide-react"
import { listLocalities, type Block, type District, type Village } from "@/api"
import { ErrorState } from "@/components/ErrorState"
import { SourceBadge } from "@/components/SourceBadge"
import { Input } from "@/components/ui/input"
import { useLoad } from "@/hooks/useLoad"
import { useLang, useT } from "@/i18n"
import { cn } from "@/lib/utils"
import type { StepProps } from "@/pages/new/draft"
import { formatValue } from "@/lib/format"

const SELECT = "h-12 w-full rounded-lg border border-border-strong bg-background px-3 text-base outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:opacity-45"

export default function StepWhere({ draft, patch, errors }: StepProps) {
  const t = useT()
  const lang = useLang()
  const [search, setSearch] = useState("")
  const { district, block } = draft
  const districts = useLoad(() => listLocalities() as Promise<District[]>, "districts")
  const blocks = useLoad(district ? () => listLocalities(district) as Promise<Block[]> : null, `blocks:${district}`)
  const villages = useLoad(district && block ? () => listLocalities(district, block) as Promise<Village[]> : null, `villages:${district}:${block}`)

  const failed = districts.error || blocks.error || villages.error
  const retry = () => [districts, blocks, villages].forEach((l) => l.error && l.retry())
  const picked = villages.items?.find((v) => v.code === draft.village_code)
  const shown = (villages.items ?? []).filter((v) => v.name.toLowerCase().includes(search.trim().toLowerCase()))

  return (
    <div className="flex flex-col gap-4">
      <h2 className="text-h2">{t("wizard.where.title")}</h2>
      {failed && <ErrorState message={t("wizard.where.loadError")} retryLabel={t("wizard.retry")} onRetry={retry} />}

      <label className="flex flex-col gap-2 font-semibold">
        {t("wizard.where.district")}
        <select
          className={SELECT}
          value={district ?? ""}
          onChange={(e) => patch({ district: e.target.value || null, block: null, village_code: null })}
        >
          <option value="">{t("wizard.where.choose")}</option>
          {districts.items?.map((d) => (
            <option key={d.code} value={d.code}>
              {d.name}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-2 font-semibold">
        {t("wizard.where.block")}
        <select
          className={SELECT}
          disabled={!district}
          value={block ?? ""}
          onChange={(e) => patch({ block: e.target.value || null, village_code: null })}
        >
          <option value="">{t("wizard.where.choose")}</option>
          {blocks.items?.map((b) => (
            <option key={b.code} value={b.code}>
              {b.name}
            </option>
          ))}
        </select>
      </label>

      <div className="flex flex-col gap-2">
        <label htmlFor="village-search" className="font-semibold">
          {t("wizard.where.village")}
        </label>
        <Input
          id="village-search"
          disabled={!block}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder={t("wizard.where.search")}
          className="h-12"
        />
        <div
          role="radiogroup"
          aria-label={t("wizard.where.village")}
          aria-invalid={errors.village ? true : undefined}
          tabIndex={errors.village ? -1 : undefined}
          className="flex flex-col gap-2 outline-none"
        >
          {shown.map((v) => (
            <button
              key={v.code}
              type="button"
              role="radio"
              aria-checked={v.code === draft.village_code}
              onClick={() => patch({ village_code: v.code })}
              className={cn(
                "flex h-12 items-center gap-2 rounded-lg border px-3 text-left outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50",
                v.code === draft.village_code ? "border-primary bg-primary-soft font-semibold" : "border-border-strong bg-background",
              )}
            >
              <MapPin aria-hidden="true" className="size-5" />
              {v.name}
            </button>
          ))}
        </div>
        {block && villages.items && shown.length === 0 && <p className="text-sm text-text-muted">{t("wizard.where.none")}</p>}
        {errors.village && (
          <p role="alert" className="text-sm text-destructive">
            {errors.village}
          </p>
        )}
      </div>

      {picked && (
        <div className="flex flex-col items-start gap-1 rounded-xl bg-primary-soft p-3">
          <p className="font-semibold">
            {picked.name} · {formatValue(picked.households, "count", lang)} {t("wizard.where.homes")}
          </p>
          <SourceBadge source="census" />
        </div>
      )}
    </div>
  )
}
