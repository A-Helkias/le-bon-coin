import { useState } from 'react'

import ProductBand from '../features/catalog/ProductBand'
import { PAGE_SIZE, useProducts } from '../features/catalog/api'

export default function CatalogPage() {
  const [offset, setOffset] = useState(0)
  const { data, isPending, isError, refetch } = useProducts(offset)

  return (
    <main className="mx-auto max-w-4xl px-6 py-12 sm:py-20">
      <header className="mb-12 sm:mb-20">
        <h1 className="font-display text-2xl leading-none">Le Bon Coin</h1>
        <p className="mt-3 text-sm text-mute">
          Mobilier et objets d’intérieur
          {data
            ? ` — ${data.total} ${data.total > 1 ? 'pièces' : 'pièce'}`
            : null}
        </p>
      </header>

      {isPending ? <LoadingPlates /> : null}

      {isError ? (
        <section className="bg-plate p-8">
          <p className="font-display text-base">
            Le catalogue n’a pas pu être chargé.
          </p>
          <p className="mt-2 text-sm text-mute">
            La boutique est momentanément injoignable.
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

      {data && data.items.length === 0 ? (
        <section className="bg-plate p-8">
          <p className="font-display text-base">
            Aucune pièce au catalogue pour le moment.
          </p>
          <p className="mt-2 text-sm text-mute">
            Les prochaines arrivées seront visibles ici.
          </p>
        </section>
      ) : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="flex flex-col gap-16">
            {data.items.map((product) => (
              <ProductBand key={product.id} product={product} />
            ))}
          </div>

          {data.total > PAGE_SIZE ? (
            <nav className="mt-20 flex items-center justify-between text-sm">
              <button
                type="button"
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                className="text-accent disabled:text-mute disabled:opacity-50"
              >
                Page précédente
              </button>
              <span className="text-mute">
                {offset + 1}–{Math.min(offset + PAGE_SIZE, data.total)} sur{' '}
                {data.total}
              </span>
              <button
                type="button"
                disabled={offset + PAGE_SIZE >= data.total}
                onClick={() => setOffset(offset + PAGE_SIZE)}
                className="text-accent disabled:text-mute disabled:opacity-50"
              >
                Page suivante
              </button>
            </nav>
          ) : null}
        </>
      ) : null}
    </main>
  )
}

/** Bare plates while the catalogue loads — no skeleton text pretending to be content. */
function LoadingPlates() {
  return (
    <div className="flex flex-col gap-16" aria-live="polite" aria-busy="true">
      <span className="sr-only">Chargement du catalogue</span>
      {[0, 1, 2].map((row) => (
        <div key={row} className="flex flex-col gap-5 sm:flex-row sm:gap-8">
          <div className="aspect-[4/3] w-full bg-plate sm:h-40 sm:w-56 sm:shrink-0" />
        </div>
      ))}
    </div>
  )
}
