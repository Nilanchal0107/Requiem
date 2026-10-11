export type StepperProps = {
  current: number
  total: number
  onSelect?: (step: number) => void
}

export function Stepper(_props: StepperProps) {
  return <div className="text-xs text-muted-foreground">Stepper</div>
}
