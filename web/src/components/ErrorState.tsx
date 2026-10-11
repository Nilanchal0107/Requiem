import { Button } from "@/components/ui/button"

export type ErrorStateProps = {
  message: string
  retryLabel: string
  onRetry?: () => void
}

export function ErrorState({ message, retryLabel, onRetry }: ErrorStateProps) {
  return (
    <div role="alert" className="flex flex-col items-start gap-2">
      <p className="text-sm text-destructive">{message}</p>
      {onRetry && (
        <Button variant="outline" className="h-12" onClick={onRetry}>
          {retryLabel}
        </Button>
      )}
    </div>
  )
}
