import type { components } from "../types/contracts.ts"

type ChatRequest = components["schemas"]["ChatRequest"]
type ChatResponse = components["schemas"]["ChatResponse"]

// Declared in V1, implemented in V2. Calling the hook throws until then.
/** Returns a function that POSTs one Ask turn to /api/chat. */
export function useChat(): (_request: ChatRequest) => Promise<ChatResponse> {
  throw new Error("useChat: not implemented")
}
