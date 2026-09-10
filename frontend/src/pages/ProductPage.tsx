import { Link, useParams } from 'react-router'

import Availability from '../features/catalog/Availability'
import ProductPlate from '../features/catalog/ProductPlate'
import { useAddToCart, useProduct } from '../features/catalog/api'
import { formatPrice } from '../lib/format'

export default function ProductPage() {
  const { productId = '' } = useParams()
  const { data: product, isPending, isError } = useProduct(productId)
  const addToCart = useAddToCart()

  return (
    <main className="mx-auto max-w-4xl px-6 py-12 sm:py-20">
      <Link to="/" className="text-sm text-accent">
        Retour au catalogue
      </Link>

      {isPending ? (
        <div className="mt-10" aria-live="polite" aria-busy="true">
          <span className="sr-only">Chargement de la pièce</span>
          <div className="aspect-[4/5] w-full bg-plate sm:w-1/2" />
        </div>
      ) : null}

      {isError ? (
        <section className="mt-10 bg-plate p-8">
          <p className="font-display text-base">Cette pièce n’existe pas.</p>
          <p className="mt-2 text-sm text-mute">
            Elle a peut-être quitté le catalogue.
          </p>
        </section>
      ) : null}

      {product ? (
        <div className="mt-10 flex flex-col gap-10 sm:flex-row sm:gap-14">
          <div className="sm:w-1/2 sm:shrink-0">
            <ProductPlate product={product} size="full" />
          </div>

          <div className="sm:sticky sm:top-20 sm:self-start">
            <h1 className="font-display text-xl leading-tight">
              {product.name}
            </h1>
            <p className="mt-2 text-xs text-mute">{product.sku}</p>

            <p className="mt-8 font-display text-lg">
              {formatPrice(product.price_cents)}
            </p>
            <p className="mt-1">
              <Availability stock={product.stock} verbose />
            </p>

            {product.description ? (
              <p className="mt-8 max-w-[52ch] text-sm leading-relaxed text-mute">
                {product.description}
              </p>
            ) : null}

            <button
              type="button"
              disabled={product.stock === 0 || addToCart.isPending}
              onClick={() =>
                addToCart.mutate({ productId: product.id, quantity: 1 })
              }
              className="mt-10 w-full bg-accent px-6 py-3 text-sm text-paper disabled:cursor-not-allowed disabled:bg-mute sm:w-auto"
            >
              {product.stock === 0 ? 'Épuisé' : 'Ajouter au panier'}
            </button>

            <p aria-live="polite" className="mt-3 text-sm text-mute">
              {addToCart.isSuccess ? 'Ajouté au panier' : null}
              {addToCart.isError
                ? 'Cette pièce n’a pas pu être ajoutée au panier.'
                : null}
            </p>
          </div>
        </div>
      ) : null}
    </main>
  )
}
