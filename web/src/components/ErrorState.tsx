export type ErrorStateProps = {
  message: string
  onRetry?: () => void
}

export function ErrorState(_props: ErrorStateProps) {
  return <div className="text-xs text-muted-foreground">ErrorState</div>
}
