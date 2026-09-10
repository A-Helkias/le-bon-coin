const priceFormatter = new Intl.NumberFormat('fr-FR', {
  style: 'currency',
  currency: 'EUR',
})

/** Format a price for display. The API returns amounts as integer cents. */
export function formatPrice(cents: number): string {
  return priceFormatter.format(cents / 100)
}

const dateFormatter = new Intl.DateTimeFormat('fr-FR', {
  day: '2-digit',
  month: '2-digit',
  year: 'numeric',
})

/** Format an ISO 8601 timestamp coming from the API. */
export function formatDate(isoDate: string): string {
  return dateFormatter.format(new Date(isoDate))
}
