export type ExplanationUnavailableProps = {
  onRetry?: () => void
}

export function ExplanationUnavailable(_props: ExplanationUnavailableProps) {
  return <div className="text-xs text-muted-foreground">ExplanationUnavailable</div>
}
