import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'

import { server } from '../../mocks/server'
import ProductPage from '../../pages/ProductPage'
import { aProduct, renderScreen } from '../../testing'

const API = 'http://localhost:8000'
const product = aProduct()
const route = `/produits/${product.id}`

describe('ProductPage', () => {
  it('affiche la pièce, son prix et sa disponibilité', async () => {
    server.use(
      http.get(`${API}/products/:id`, () => HttpResponse.json(product)),
    )

    renderScreen(<ProductPage />, route, '/produits/:productId')

    expect(
      await screen.findByRole('heading', { name: product.name }),
    ).toBeInTheDocument()
    // getByText normalises the DOM text — the no-break space before the sign
    // becomes a plain one — but not the expected string, so match loosely.
    expect(screen.getByText(/^149,00\s€$/)).toBeInTheDocument()
    expect(screen.getByText('En stock, 4 pièces')).toBeInTheDocument()
  })

  it('indique que la pièce n’existe pas sur un 404', async () => {
    server.use(
      http.get(
        `${API}/products/:id`,
        () =>
          new HttpResponse(
            JSON.stringify({ detail: "Ce produit n'existe pas." }),
            {
              status: 404,
              headers: { 'Content-Type': 'application/json' },
            },
          ),
      ),
    )

    renderScreen(<ProductPage />, route, '/produits/:productId')

    expect(
      await screen.findByText('Cette pièce n’existe pas.'),
    ).toBeInTheDocument()
  })

  it('ajoute la pièce au panier et le confirme', async () => {
    const cart = {
      id: '22222222-2222-4222-8222-222222222222',
      user_id: null,
      items: [],
      total_cents: 0,
      created_at: '2026-09-01T10:00:00Z',
      updated_at: '2026-09-01T10:00:00Z',
    }
    server.use(
      http.get(`${API}/products/:id`, () => HttpResponse.json(product)),
      http.post(`${API}/carts`, () => HttpResponse.json(cart, { status: 201 })),
      http.post(`${API}/carts/:cartId/items`, () =>
        HttpResponse.json(cart, { status: 201 }),
      ),
    )

    renderScreen(<ProductPage />, route, '/produits/:productId')
    await userEvent.click(
      await screen.findByRole('button', { name: 'Ajouter au panier' }),
    )

    expect(await screen.findByText('Ajouté au panier')).toBeInTheDocument()
  })

  it('désactive le bouton et le dit quand la pièce est épuisée', async () => {
    server.use(
      http.get(`${API}/products/:id`, () =>
        HttpResponse.json(aProduct({ stock: 0 })),
      ),
    )

    renderScreen(<ProductPage />, route, '/produits/:productId')

    const button = await screen.findByRole('button', { name: 'Épuisé' })
    expect(button).toBeDisabled()
  })
})
