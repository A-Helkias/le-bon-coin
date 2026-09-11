import { Link } from 'react-router'

import CartLine from '../features/cart/CartLine'
import { useCart, useCartId } from '../features/cart/api'
import { formatPrice } from '../lib/format'

export default function CartPage() {
  const hasCart = useCartId() !== null
  const { data: cart, isPending, isError, refetch } = useCart()
  const isEmpty = !hasCart || (cart !== undefined && cart.items.length === 0)

  return (
    <main className="mx-auto max-w-3xl px-6 py-12 sm:py-16">
      <h1 className="mb-10 font-display text-xl leading-none">Votre panier</h1>

      {hasCart && isPending ? (
        <div aria-live="polite" aria-busy="true">
          <span className="sr-only">Chargement du panier</span>
          <div className="h-24 w-full bg-plate" />
        </div>
      ) : null}

      {isError ? (
        <section className="bg-plate p-8">
          <p className="font-display text-base">
            Votre panier n’a pas pu être chargé.
          </p>
          <button
            type="button"
            onClick={() => void refetch()}
            className="mt-6 bg-accent px-5 py-2 text-sm text-paper"
          >
            Réessayer
          </button>
        </section>
      ) : null}

      {isEmpty && !isError ? (
        <section className="bg-plate p-8">
          <p className="font-display text-base">Votre panier est vide.</p>
          <p className="mt-2 text-sm text-mute">
            Les pièces que vous ajoutez au catalogue apparaîtront ici.
          </p>
          <Link
            to="/"
            className="mt-6 inline-block bg-accent px-5 py-2 text-sm text-paper"
          >
            Parcourir le catalogue
          </Link>
        </section>
      ) : null}

      {cart && cart.items.length > 0 ? (
        <>
          <div className="flex flex-col gap-8">
            {cart.items.map((item) => (
              <CartLine key={item.product_id} item={item} />
            ))}
          </div>

          <div className="mt-10 flex items-baseline justify-between">
            <span className="text-sm text-mute">Total</span>
            <span className="font-display text-lg">
              {formatPrice(cart.total_cents)}
            </span>
          </div>

          <Link
            to="/commande"
            className="mt-8 inline-block w-full bg-accent px-6 py-3 text-center text-sm text-paper sm:w-auto"
          >
            Passer commande
          </Link>
        </>
      ) : null}
    </main>
  )
}
