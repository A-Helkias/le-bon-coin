import { fireEvent, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { server } from '../../mocks/server'
import CartPage from '../../pages/CartPage'
import { CART_STORAGE_KEY, aCart, aCartItem, renderScreen } from '../../testing'

const API = 'http://localhost:8000'
const cart = aCart()

describe('CartPage', () => {
  beforeEach(() => {
    localStorage.setItem(CART_STORAGE_KEY, cart.id)
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('affiche les lignes du panier et son total', async () => {
    server.use(http.get(`${API}/carts/:id`, () => HttpResponse.json(cart)))

    renderScreen(<CartPage />, '/panier')

    expect(
      await screen.findByRole('heading', { name: 'Chaise en chêne' }),
    ).toBeInTheDocument()
    expect(screen.getByText(/^387,00\s€$/)).toBeInTheDocument()
  })

  it('affiche un message quand le panier ne peut pas être chargé', async () => {
    server.use(
      http.get(
        `${API}/carts/:id`,
        () => new HttpResponse(null, { status: 500 }),
      ),
    )

    renderScreen(<CartPage />, '/panier')

    expect(
      await screen.findByText('Votre panier n’a pas pu être chargé.'),
    ).toBeInTheDocument()
  })

  it('invite à parcourir le catalogue quand le panier est vide', async () => {
    server.use(
      http.get(`${API}/carts/:id`, () =>
        HttpResponse.json(aCart({ items: [] })),
      ),
    )

    renderScreen(<CartPage />, '/panier')

    expect(
      await screen.findByText('Votre panier est vide.'),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Parcourir le catalogue' }),
    ).toBeInTheDocument()
  })

  it('ne crée pas de panier pour un visiteur qui n’en a jamais eu', async () => {
    localStorage.clear()

    renderScreen(<CartPage />, '/panier')

    expect(
      await screen.findByText('Votre panier est vide.'),
    ).toBeInTheDocument()
  })

  it('met à jour le total après un changement de quantité', async () => {
    const updated = aCart({
      items: [
        aCartItem({ quantity: 3, line_total_cents: 44700 }),
        aCartItem({
          product_id: '44444444-4444-4444-8444-444444444444',
          product_name: 'Suspension en rotin',
          product_sku: 'LUM-002',
          unit_price_cents: 8900,
          quantity: 1,
          line_total_cents: 8900,
        }),
      ],
    })
    let patched = false
    server.use(
      http.get(`${API}/carts/:id`, () =>
        HttpResponse.json(patched ? updated : cart),
      ),
      http.patch(`${API}/carts/:id/items/:productId`, () => {
        patched = true
        return HttpResponse.json(updated)
      }),
    )

    renderScreen(<CartPage />, '/panier')
    const [field] = await screen.findAllByLabelText('Quantité')
    // The field is controlled by server state: clearing then typing would snap
    // back to the stored quantity mid-way. One change event says it plainly.
    fireEvent.change(field, { target: { value: '3' } })

    expect(await screen.findByText(/^536,00\s€$/)).toBeInTheDocument()
  })

  it('retire une ligne du panier', async () => {
    let removed = false
    server.use(
      http.get(`${API}/carts/:id`, () =>
        HttpResponse.json(removed ? aCart({ items: [] }) : cart),
      ),
      http.delete(`${API}/carts/:id/items/:productId`, () => {
        removed = true
        return new HttpResponse(null, { status: 204 })
      }),
    )

    renderScreen(<CartPage />, '/panier')
    const [remove] = await screen.findAllByRole('button', { name: 'Retirer' })
    await userEvent.click(remove)

    expect(
      await screen.findByText('Votre panier est vide.'),
    ).toBeInTheDocument()
  })
})
