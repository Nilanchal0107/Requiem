# 05: LLM client, cache and Entrepreneur View

**What to build:** Given an `EngineResult` and a language, `explain_report` returns a verified Entrepreneur View `Explanation` in English, Hindi or Marathi. It runs live against Gemini with Groq as fallback, and works offline in replay mode.

**Owner:** AIML

**Blocked by:** 04

**Status:** ready-for-agent

## Notes

- The client is OpenAI-compatible: Gemini first, Groq if Gemini fails. Keys come from `.env` only.
- The cache key is a hash of model, messages and tools. `LLM_MODE=live|record|replay`, and replay raises on a cache miss instead of calling out.
- The prompt gets Figure ids and units, never values.
- If verify fails, regenerate once. If it fails again, strip the failing sentences and report verified / total.
- Engine input for tests: build it inside the test, or use the fixture report's engine block. Don't wait for tickets 02 and 03.

## Acceptance criteria

- [ ] In replay mode, with a committed cache file, `explain_report` returns a contract-valid `Explanation` with no digits and every placeholder resolving.
- [ ] A replay-mode test with a cached bad reply (containing a digit) shows one regeneration, then sentence stripping and a verified count below the total.
- [ ] A replay cache miss raises instead of calling the network.
- [ ] Record mode run once by hand for the demo persona in Marathi. The cache file is committed.
