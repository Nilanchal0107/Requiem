import type { Lang } from "../../i18n/resolve.ts"
import type { components } from "../../types/contracts.ts"

type IntakeInput = components["schemas"]["IntakeInput"]
type Eligibility = components["schemas"]["Eligibility"]

/** What the wizard holds while the Entrepreneur is still filling it in; null means not chosen yet. */
export type Draft = {
  step: number
  district: string | null
  block: string | null
  village_code: string | null
  archetype_id: string | null
  unit_scale: number | null
  own_contribution: number | null
  eligibility: Partial<Eligibility>
}

export const EMPTY_DRAFT: Draft = {
  step: 0,
  district: null,
  block: null,
  village_code: null,
  archetype_id: null,
  unit_scale: null,
  own_contribution: null,
  // Gender, category and schooling have no honest default, so they start unset and must be chosen.
  eligibility: { age: 30, business_status: "new", prior_subsidy: false, prior_tarun_repaid: false, artisan_trade: false, farmland: "none" },
}

/** What every wizard step receives. `errors` is field name → message, already translated. */
export type StepProps = {
  draft: Draft
  patch: (changes: Partial<Draft>) => void
  errors: Record<string, string>
}

const KEY = "requiem.wizardDraft"
type Store = Pick<Storage, "getItem" | "setItem" | "removeItem">

// Storage can be blocked (private window, cleared site data): the wizard then just works without a draft.
const safe = <T>(fn: () => T, fallback: T): T => {
  try {
    return fn()
  } catch {
    return fallback
  }
}

export function loadDraft(store: Store = localStorage): Draft {
  return safe(() => {
    const raw = store.getItem(KEY)
    if (!raw) return EMPTY_DRAFT
    const saved = JSON.parse(raw) as Partial<Draft>
    return { ...EMPTY_DRAFT, ...saved, eligibility: { ...EMPTY_DRAFT.eligibility, ...saved.eligibility } }
  }, EMPTY_DRAFT)
}

export const saveDraft = (draft: Draft, store: Store = localStorage) => safe(() => store.setItem(KEY, JSON.stringify(draft)), undefined)
export const clearDraft = (store: Store = localStorage) => safe(() => store.removeItem(KEY), undefined)

const ELIGIBILITY_CHOICES = ["gender", "social_category", "education"] as const

/** Field name → i18n key of the error. Empty when the step is complete. `required` is the Archetype's eligibility_fields. */
export function validate(step: number, draft: Draft, required: string[]): Record<string, string> {
  const errors: Record<string, string> = {}
  if (step === 0 && !draft.village_code) errors.village = "wizard.error.village"
  if (step === 1 && !draft.archetype_id) errors.archetype = "wizard.error.archetype"
  if (step === 2 && draft.own_contribution === null) errors.own_contribution = "wizard.error.money"
  if (step === 3) for (const f of ELIGIBILITY_CHOICES) if (required.includes(f) && !draft.eligibility[f]) errors[f] = `wizard.error.${f}`
  return errors
}

/** The first step with a problem, or null when the whole draft can be posted. */
export function firstBadStep(draft: Draft, required: string[]): number | null {
  const bad = [0, 1, 2, 3].find((s) => Object.keys(validate(s, draft, required)).length > 0)
  return bad ?? null
}

/** Only call when `firstBadStep` is null. */
export function toIntake(draft: Draft, language: Lang): IntakeInput {
  return {
    village_code: draft.village_code!,
    archetype_id: draft.archetype_id!,
    unit_scale: draft.unit_scale!,
    own_contribution: draft.own_contribution!,
    eligibility: draft.eligibility as Eligibility,
    language,
  }
}
