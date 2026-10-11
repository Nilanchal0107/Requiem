type Nav = {
  share?: (data: { title: string; url: string }) => Promise<void>
  clipboard?: { writeText: (text: string) => Promise<void> }
}

/** Opens the phone's share sheet; where that isn't supported (or fails) copies the link instead. */
export async function shareLink(nav: Nav, data: { title: string; url: string }): Promise<"shared" | "copied" | "cancelled"> {
  if (nav.share) {
    try {
      await nav.share(data)
      return "shared"
    } catch (err) {
      // Closing the share sheet is not a failure and must not copy anything.
      if (err instanceof Error && err.name === "AbortError") return "cancelled"
    }
  }
  await nav.clipboard?.writeText(data.url)
  return "copied"
}
