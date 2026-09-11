import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { server } from '../../mocks/server'
import CheckoutPage from '../../pages/CheckoutPage'
import { CART_STORAGE_KEY, aCart, anOrder, renderScreen } from '../../testing'

const API = 'http://localhost:8000'
const cart = aCart()

async function fillTheForm(): Promise<void> {
  await userEvent.type(screen.getByLabelText('Nom et prénom'), 'Camille Martin')
  await userEvent.type(
    screen.getByLabelText('Adresse e-mail'),
    'camille@example.com',
  )
  await userEvent.type(
    screen.getByLabelText('Adresse de livraison'),
    '12 rue des Lilas',
  )
  await userEvent.type(screen.getByLabelText('Code postal'), '75011')
  await userEvent.type(screen.getByLabelText('Ville'), 'Paris')
}

describe('CheckoutPage', () => {
  beforeEach(() => {
    localStorage.setItem(CART_STORAGE_KEY, cart.id)
    server.use(http.get(`${API}/carts/:id`, () => HttpResponse.json(cart)))
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('présente le formulaire et le total à régler', async () => {
    renderScreen(<CheckoutPage />, '/commande')

    expect(
      await screen.findByRole('heading', { name: 'Votre commande' }),
    ).toBeInTheDocument()
    expect(screen.getByLabelText('Adresse e-mail')).toBeInTheDocument()
    expect(await screen.findByText(/^387,00\s€$/)).toBeInTheDocument()
  })

  it('remonte le message du serveur quand la commande échoue', async () => {
    server.use(
      http.post(
        `${API}/orders`,
        () =>
          new HttpResponse(
            JSON.stringify({ detail: 'Votre panier est vide.' }),
            { status: 422, headers: { 'Content-Type': 'application/json' } },
          ),
      ),
    )

    renderScreen(<CheckoutPage />, '/commande')
    await fillTheForm()
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la commande' }),
    )

    expect(
      await screen.findByText('Votre panier est vide.'),
    ).toBeInTheDocument()
  })

  it('vide le panier stocké une fois la commande passée', async () => {
    server.use(
      http.post(`${API}/orders`, () =>
        HttpResponse.json(anOrder(), { status: 201 }),
      ),
    )

    renderScreen(<CheckoutPage />, '/commande')
    await fillTheForm()
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la commande' }),
    )

    // The server consumed the cart; keeping its id would point at a deleted
    // resource on the next read.
    await screen.findByRole('heading', { name: 'Votre commande' })
    expect(localStorage.getItem(CART_STORAGE_KEY)).toBeNull()
  })

  it('refuse de commander un panier vide', async () => {
    server.use(
      http.get(`${API}/carts/:id`, () =>
        HttpResponse.json(aCart({ items: [] })),
      ),
    )

    renderScreen(<CheckoutPage />, '/commande')

    expect(
      await screen.findByText(
        'Votre panier est vide, il n’y a rien à commander.',
      ),
    ).toBeInTheDocument()
  })
})
