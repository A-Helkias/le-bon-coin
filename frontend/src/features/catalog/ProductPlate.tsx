import type { Product } from './api'

type Props = {
  product: Product
  /** Detail pages give the plate more room than catalogue bands. */
  size?: 'band' | 'full'
}

/**
 * The coloured ground every object sits on.
 *
 * A product without a photograph is not a hole in the layout: the plate is
 * there either way, and carries the reference when there is nothing to show.
 */
export default function ProductPlate({ product, size = 'band' }: Props) {
  const box =
    size === 'full'
      ? 'aspect-[4/5] w-full'
      : 'aspect-[4/3] w-full sm:h-40 sm:w-56 sm:shrink-0'

  // A bare plate carries no text: the reference already sits beside it, and
  // repeating it here would say the same thing twice.
  return (
    <div className={`${box} overflow-hidden bg-plate`}>
      {product.image_url ? (
        <img
          src={product.image_url}
          alt={product.name}
          loading="lazy"
          className="plate-photo h-full w-full object-cover"
        />
      ) : null}
    </div>
  )
}
