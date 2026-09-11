import { Link } from 'react-router'

import { formatPrice } from '../../lib/format'
import type { CartItem } from './api'
import { useRemoveFromCart, useSetQuantity } from './api'

export default function CartLine({ item }: { item: CartItem }) {
  const setQuantity = useSetQuantity()
  const remove = useRemoveFromCart()
  const busy = setQuantity.isPending || remove.isPending

  const quantityFieldId = `quantity-${item.product_id}`

  return (
    <article className="flex flex-col gap-4 border-b border-plate pb-8 sm:flex-row sm:items-start sm:gap-8">
      <div className="flex-1">
        <h2 className="font-display text-base leading-tight">
          <Link
            to={`/produits/${item.product_id}`}
            className="hover:text-accent"
          >
            {item.product_name}
          </Link>
        </h2>
        <p className="mt-1 text-xs text-mute">{item.product_sku}</p>
        <p className="mt-2 text-sm text-mute">
          {formatPrice(item.unit_price_cents)} l’unité
        </p>
      </div>

      <div className="flex items-end gap-6">
        <div>
          <label htmlFor={quantityFieldId} className="block text-xs text-mute">
            Quantité
          </label>
          <input
            id={quantityFieldId}
            type="number"
            min={1}
            value={item.quantity}
            disabled={busy}
            onChange={(event) => {
              const quantity = Number(event.target.value)
              if (quantity >= 1) {
                setQuantity.mutate({ productId: item.product_id, quantity })
              }
            }}
            className="mt-1 w-20 border-b border-plate bg-transparent py-2 text-sm focus:border-accent focus:outline-none"
          />
        </div>

        <p className="font-display text-base">
          {formatPrice(item.line_total_cents)}
        </p>

        <button
          type="button"
          disabled={busy}
          onClick={() => remove.mutate(item.product_id)}
          className="pb-2 text-sm text-accent disabled:opacity-50"
        >
          Retirer
        </button>
      </div>
    </article>
  )
}
