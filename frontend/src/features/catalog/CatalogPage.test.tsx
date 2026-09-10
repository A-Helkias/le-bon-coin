import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { describe, expect, it } from 'vitest'

import { server } from '../../mocks/server'
import CatalogPage from '../../pages/CatalogPage'
import { aProduct, renderScreen } from './testing'

const PRODUCTS_URL = 'http://localhost:8000/products'

describe('CatalogPage', () => {
  it('affiche les pièces du catalogue et leurs prix en euros', async () => {
    server.use(
      http.get(PRODUCTS_URL, () =>
        HttpResponse.json({
          items: [aProduct({ name: 'Chaise en chêne', price_cents: 14900 })],
          total: 1,
        }),
      ),
    )

    renderScreen(<CatalogPage />)

    expect(
      await screen.findByRole('heading', { name: 'Chaise en chêne' }),
    ).toBeInTheDocument()
    // getByText normalises the DOM text — the no-break space before the sign
    // becomes a plain one — but not the expected string, so match loosely.
    expect(screen.getByText(/^149,00\s€$/)).toBeInTheDocument()
    expect(
      screen.getByText('Mobilier et objets d’intérieur — 1 pièce'),
    ).toBeInTheDocument()
  })

  it('affiche un message et un bouton Réessayer quand l’API échoue', async () => {
    server.use(
      http.get(PRODUCTS_URL, () => new HttpResponse(null, { status: 500 })),
    )

    renderScreen(<CatalogPage />)

    expect(
      await screen.findByText('Le catalogue n’a pas pu être chargé.'),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Réessayer' }),
    ).toBeInTheDocument()
  })

  it('invite à revenir quand le catalogue est vide', async () => {
    server.use(
      http.get(PRODUCTS_URL, () => HttpResponse.json({ items: [], total: 0 })),
    )

    renderScreen(<CatalogPage />)

    expect(
      await screen.findByText('Aucune pièce au catalogue pour le moment.'),
    ).toBeInTheDocument()
  })

  it('mène à la fiche de la pièce quand on clique son nom', async () => {
    const product = aProduct()
    server.use(
      http.get(PRODUCTS_URL, () =>
        HttpResponse.json({ items: [product], total: 1 }),
      ),
    )

    renderScreen(<CatalogPage />)
    const link = await screen.findByRole('link', { name: product.name })

    expect(link).toHaveAttribute('href', `/produits/${product.id}`)
    await userEvent.click(link)
  })

  it('rend une plaque nue plutôt qu’une image cassée sans photo', async () => {
    server.use(
      http.get(PRODUCTS_URL, () =>
        HttpResponse.json({
          items: [aProduct({ image_url: null, sku: 'TABLE-014' })],
          total: 1,
        }),
      ),
    )

    renderScreen(<CatalogPage />)

    expect(
      await screen.findByRole('heading', { name: 'Chaise en chêne' }),
    ).toBeInTheDocument()
    expect(screen.queryByRole('img')).not.toBeInTheDocument()
    expect(screen.getByText('TABLE-014')).toBeInTheDocument()
  })

  it('signale une rupture de stock', async () => {
    server.use(
      http.get(PRODUCTS_URL, () =>
        HttpResponse.json({ items: [aProduct({ stock: 0 })], total: 1 }),
      ),
    )

    renderScreen(<CatalogPage />)

    expect(await screen.findByText('Épuisé')).toBeInTheDocument()
  })
})
