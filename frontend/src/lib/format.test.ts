import { describe, expect, it } from 'vitest'

import { formatDate, formatPrice } from './format'

// The fr-FR locale separates the amount from the currency sign with a no-break
// space (U+00A0), not a plain one. Escaping it keeps the literal readable.
const NBSP = '\u00a0'

describe('formatPrice', () => {
  it('rend un montant en centimes au format français', () => {
    expect(formatPrice(1999)).toBe(`19,99${NBSP}€`)
  })

  it('rend un montant nul', () => {
    expect(formatPrice(0)).toBe(`0,00${NBSP}€`)
  })
})

describe('formatDate', () => {
  it('rend une date ISO au format français', () => {
    expect(formatDate('2026-09-10T08:30:00Z')).toBe('10/09/2026')
  })
})
