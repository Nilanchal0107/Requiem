import type { components } from "@/types/contracts"

// FIXTURE ONLY: a canned intake for the V1 stream demo (Niphad village, dairy, ₹1,00,000, demo persona).
// V2 deletes this file and posts what the wizard collects.
export const CANNED_INTAKE: components["schemas"]["IntakeInput"] = {
  village_code: "FX1002",
  archetype_id: "dairy",
  unit_scale: 5,
  own_contribution: 100000,
  eligibility: {
    age: 34,
    gender: "female",
    social_category: "obc",
    education: "10th_pass",
    business_status: "new",
    prior_subsidy: false,
    prior_tarun_repaid: false,
    artisan_trade: false,
    farmland: "none",
  },
  language: "en",
}
