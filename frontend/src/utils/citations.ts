// Zerlegt eine Antwort in Textteile und Belege wie [2], [1, 3] oder [1][2].
// Nummern ohne passende Quelle bleiben normaler Text.

export type CitationRef = { n: number; valid: boolean }

export type AnswerSegment =
  | { type: 'text'; value: string }
  | { type: 'cite'; refs: CitationRef[] }

const CITATION_PATTERN = /\[(\d+(?:\s*[,;]\s*\d+)*)\]/g

export function parseCitations(text: string, sourceCount: number): AnswerSegment[] {
  const segments: AnswerSegment[] = []
  let last = 0

  for (const match of text.matchAll(CITATION_PATTERN)) {
    const refs = match[1]!
      .split(/[,;]/)
      .map((part) => Number(part.trim()))
      .map((n) => ({ n, valid: n >= 1 && n <= sourceCount }))

    // Keine einzige gültige Nummer: als Text stehen lassen (z. B. "[2024]")
    if (!refs.some((r) => r.valid)) continue

    if (match.index > last) segments.push({ type: 'text', value: text.slice(last, match.index) })
    segments.push({ type: 'cite', refs })
    last = match.index + match[0].length
  }

  if (last < text.length) segments.push({ type: 'text', value: text.slice(last) })
  return segments
}
