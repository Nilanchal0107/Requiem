import { Calculator, Landmark, Lightbulb, MapPin, User, Users, type LucideIcon } from "lucide-react"
import { useT } from "@/i18n"
import { cn } from "@/lib/utils"
import type { components } from "@/types/contracts"

type Source = components["schemas"]["Figure"]["source"]

export type SourceBadgeProps = {
  source: Source
}

const ICONS: Record<Source, LucideIcon> = {
  census: Users,
  osm: MapPin,
  user: User,
  assumption: Lightbulb,
  scheme: Landmark,
  computed: Calculator,
}

export function SourceBadge({ source }: SourceBadgeProps) {
  const t = useT()
  const Icon = ICONS[source]
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full bg-surface-soft px-2 py-0.5 text-sm text-text-muted",
        source === "assumption" && "border border-dotted border-text-muted",
      )}
    >
      <Icon aria-hidden="true" className="size-4" />
      {t(`source.${source}`)}
    </span>
  )
}
