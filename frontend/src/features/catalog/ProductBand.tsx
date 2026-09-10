import { Link } from 'react-router'

import { formatPrice } from '../../lib/format'
import type { Product } from './api'
import Availability from './Availability'
import ProductPlate from './ProductPlate'

export default function ProductBand({ product }: { product: Product }) {
  return (
    <article className="flex flex-col gap-5 sm:flex-row sm:gap-8">
      {/* The plate is not a second link to the same page: one target per row
          keeps the tab order honest. */}
      <ProductPlate product={product} />

      <div className="flex flex-1 flex-col gap-2 sm:flex-row sm:items-start sm:justify-between sm:gap-8">
        <div className="max-w-[52ch]">
          <h2 className="font-display text-base leading-tight">
            <Link to={`/produits/${product.id}`} className="hover:text-accent">
              {product.name}
            </Link>
          </h2>
          <p className="mt-1 text-xs text-mute">{product.sku}</p>
          {product.description ? (
            <p className="mt-3 text-sm leading-relaxed text-mute">
              {product.description}
            </p>
          ) : null}
        </div>

        <div className="flex items-baseline gap-4 sm:flex-col sm:items-end sm:gap-1">
          <p className="font-display text-base">
            {formatPrice(product.price_cents)}
          </p>
          <Availability stock={product.stock} />
        </div>
      </div>
    </article>
  )
}
