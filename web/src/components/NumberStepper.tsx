export type NumberStepperProps = {
  value: number
  min: number
  max: number
  step: number
  unit: string
  onChange: (value: number) => void
}

export function NumberStepper(_props: NumberStepperProps) {
  return <div className="text-xs text-muted-foreground">NumberStepper</div>
}
