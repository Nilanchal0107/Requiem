import type { components } from "@/types/contracts"

type EngineResult = components["schemas"]["EngineResult"]

export type NumbersTabProps = {
  engine: EngineResult
}

export function NumbersTab({ engine }: NumbersTabProps) {
  return (
    <ul className="flex flex-col gap-1 font-mono text-sm">
      {Object.keys(engine.figures).map((id) => (
        <li key={id}>{id}</li>
      ))}
    </ul>
  )
}
