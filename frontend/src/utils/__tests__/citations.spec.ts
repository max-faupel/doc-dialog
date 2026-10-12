import { describe, expect, it } from 'vitest'
import { parseCitations } from '../citations'

describe('parseCitations', () => {
  it('zerlegt Text mit einfachem Beleg', () => {
    expect(parseCitations('Drei Monate [1].', 2)).toEqual([
      { type: 'text', value: 'Drei Monate ' },
      { type: 'cite', refs: [{ n: 1, valid: true }] },
      { type: 'text', value: '.' },
    ])
  })

  it('erkennt mehrere Nummern und markiert ungültige', () => {
    const segments = parseCitations('Siehe [1, 3]', 2)
    expect(segments[1]).toEqual({
      type: 'cite',
      refs: [
        { n: 1, valid: true },
        { n: 3, valid: false },
      ],
    })
  })

  it('lässt Klammern ohne gültige Nummer als Text stehen', () => {
    expect(parseCitations('Stand [2024]', 2)).toEqual([{ type: 'text', value: 'Stand [2024]' }])
  })
})
