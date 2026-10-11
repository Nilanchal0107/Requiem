/** The page to return to after login: only same-site paths, so `?next=` cannot send the Entrepreneur elsewhere. */
export function safeNext(next: string | null): string {
  return next && next.startsWith("/") && !next.startsWith("//") && !next.startsWith("/\\") ? next : "/"
}
