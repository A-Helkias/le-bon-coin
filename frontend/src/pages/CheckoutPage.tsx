import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router'

import { useCart } from '../features/cart/api'
import { useCreateOrder } from '../features/checkout/api'
import type { CustomerDetails } from '../features/checkout/api'
import { formatPrice } from '../lib/format'

const FIELDS: { name: keyof CustomerDetails; label: string; type: string }[] = [
  { name: 'customer_name', label: 'Nom et prénom', type: 'text' },
  { name: 'customer_email', label: 'Adresse e-mail', type: 'email' },
  { name: 'shipping_address', label: 'Adresse de livraison', type: 'text' },
  { name: 'shipping_postal_code', label: 'Code postal', type: 'text' },
  { name: 'shipping_city', label: 'Ville', type: 'text' },
]

export default function CheckoutPage() {
  const navigate = useNavigate()
  const { data: cart } = useCart()
  const createOrder = useCreateOrder()

  function submit(event: FormEvent<HTMLFormElement>): void {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const details = Object.fromEntries(
      form.entries(),
    ) as unknown as CustomerDetails

    createOrder.mutate(details, {
      onSuccess: (order) => {
        void navigate(`/commande/${order.id}`, { state: { order } })
      },
    })
  }

  if (cart && cart.items.length === 0) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12 sm:py-16">
        <section className="bg-plate p-8">
          <p className="font-display text-base">
            Votre panier est vide, il n’y a rien à commander.
          </p>
          <Link
            to="/"
            className="mt-6 inline-block bg-accent px-5 py-2 text-sm text-paper"
          >
            Parcourir le catalogue
          </Link>
        </section>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12 sm:py-16">
      <h1 className="mb-10 font-display text-xl leading-none">
        Votre commande
      </h1>

      <form onSubmit={submit} className="flex flex-col gap-6">
        {FIELDS.map((field) => (
          <div key={field.name}>
            <label htmlFor={field.name} className="block text-xs text-mute">
              {field.label}
            </label>
            <input
              id={field.name}
              name={field.name}
              type={field.type}
              required
              className="mt-1 w-full border-b border-plate bg-transparent py-2 text-sm focus:border-accent focus:outline-none"
            />
          </div>
        ))}

        <div>
          <label htmlFor="shipping_country" className="block text-xs text-mute">
            Pays
          </label>
          <select
            id="shipping_country"
            name="shipping_country"
            defaultValue="FR"
            className="mt-1 border-b border-plate bg-transparent py-2 text-sm focus:border-accent focus:outline-none"
          >
            <option value="FR">France</option>
            <option value="BE">Belgique</option>
            <option value="CH">Suisse</option>
            <option value="LU">Luxembourg</option>
          </select>
        </div>

        {cart ? (
          <div className="mt-4 flex items-baseline justify-between border-t border-plate pt-6">
            <span className="text-sm text-mute">
              {cart.items.length}{' '}
              {cart.items.length > 1 ? 'articles' : 'article'}
            </span>
            <span className="font-display text-lg">
              {formatPrice(cart.total_cents)}
            </span>
          </div>
        ) : null}

        <button
          type="submit"
          disabled={createOrder.isPending}
          className="mt-2 w-full bg-accent px-6 py-3 text-sm text-paper disabled:bg-mute sm:w-auto sm:self-start"
        >
          {createOrder.isPending ? 'Envoi en cours' : 'Valider la commande'}
        </button>

        <p aria-live="polite" className="text-sm text-accent">
          {createOrder.isError ? createOrder.error.message : null}
        </p>
      </form>
    </main>
  )
}
