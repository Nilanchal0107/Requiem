import { postJson } from "../api.ts"
import type { components } from "../types/contracts.ts"

type ChatRequest = components["schemas"]["ChatRequest"]
type ChatResponse = components["schemas"]["ChatResponse"]

/** Returns a function that POSTs one Ask turn to /api/chat. */
export function useChat(): (request: ChatRequest) => Promise<ChatResponse> {
  return (request) => postJson<ChatResponse>("/api/chat", request)
}
