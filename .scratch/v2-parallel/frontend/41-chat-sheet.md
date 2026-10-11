# 41: Chat sheet (stretch)

**What to build:** From the report, Ask opens a chat sheet with suggested starter questions. Replies show filled-in numbers, citations linking to the Scheme source, and suggested changes that open the what-if sheet.

**Owner:** Frontend

**Blocked by:** None (stretch; pick up only when your core tickets are done). Reuses the renderer from 20.

**Status:** done

## Acceptance criteria

- [x] Against the fixture chat route, a reply renders with no `{{`, and the citation link and suggested change are visible.
- [x] `npm run check` and `npm run build` pass.

## Comments

- Commit: "V2-41: Chat sheet" (see `git log`).
- `useChat` now POSTs `/api/chat`; the sheet keeps its conversation while closed and sends the last 10 turns as history.
- Replies go through `FigureText` (report figures merged with the reply's own `figures`), so no `{{` reaches the screen. Citations are links to the Scheme source; a suggested change shows the Path to Yes wording and "Try it", which closes the chat and opens the what-if sheet with that change.
- `changeText` is now exported from `ExplanationTab.tsx` and shared with the chat; the Path to Yes card is unchanged.
- Deferred: no streaming and no `tools_used` display. A failed send puts the question back in the box.
- Not browser-tested; verified by `npm run check` (the old "not implemented" assert is now a real `useChat` request check) and `npm run build`. The fixture reply's `{{funding_gap}}` exists in the fixture report's figures.
