import { Link, useLocation, useParams } from 'react-router'

import type { Order } from '../features/checkout/api'
import { formatDate, formatPrice } from '../lib/format'

export default function OrderConfirmationPage() {
  const { orderId = '' } = useParams()
  // The order comes from the checkout that just created it. Re-fetching it
  // would need an admin route; the response is already authoritative.
  const order = (useLocation().state as { order?: Order } | null)?.order

  if (!order) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12 sm:py-16">
        <section className="bg-plate p-8">
          <p className="font-display text-base">
            Le détail de cette commande n’est plus affichable.
          </p>
          <p className="mt-2 text-sm text-mute">
            Elle a bien été enregistrée sous la référence {orderId}.
          </p>
          <Link
            to="/"
            className="mt-6 inline-block bg-accent px-5 py-2 text-sm text-paper"
          >
            Retour au catalogue
          </Link>
        </section>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-3xl px-6 py-12 sm:py-16">
      <h1 className="font-display text-xl leading-tight">
        Commande confirmée.
      </h1>
      <p className="mt-3 text-sm text-mute">
        Un message de confirmation part à l’adresse {order.customer_email}.
      </p>

      <dl className="mt-10 grid grid-cols-2 gap-y-3 text-sm">
        <dt className="text-mute">Référence</dt>
        <dd className="text-right">{order.id}</dd>
        <dt className="text-mute">Passée le</dt>
        <dd className="text-right">{formatDate(order.created_at)}</dd>
        <dt className="text-mute">Livrée à</dt>
        <dd className="text-right">
          {order.shipping_address}, {order.shipping_postal_code}{' '}
          {order.shipping_city}
        </dd>
      </dl>

      <div className="mt-10 flex flex-col gap-4 border-t border-plate pt-8">
        {order.items.map((item) => (
          <div
            key={item.product_id}
            className="flex items-baseline justify-between"
          >
            <span className="text-sm">
              {item.product_name}
              <span className="ml-2 text-mute">×{item.quantity}</span>
            </span>
            <span className="text-sm">
              {formatPrice(item.line_total_cents)}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-8 flex items-baseline justify-between border-t border-plate pt-6">
        <span className="text-sm text-mute">Total</span>
        <span className="font-display text-lg">
          {formatPrice(order.total_cents)}
        </span>
      </div>

      <Link to="/" className="mt-10 inline-block text-sm text-accent">
        Retour au catalogue
      </Link>
    </main>
  )
}
