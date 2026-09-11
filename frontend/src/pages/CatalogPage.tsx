import { useSearchParams } from 'react-router'

import CatalogFilters from '../features/catalog/CatalogFilters'
import ProductBand from '../features/catalog/ProductBand'
import { PAGE_SIZE, useProducts } from '../features/catalog/api'
import type {
  CatalogFilters as Filters,
  ProductSort,
} from '../features/catalog/api'

const SORTS: ProductSort[] = ['recent', 'price_asc', 'price_desc']

function readFilters(params: URLSearchParams): Filters {
  const sort = params.get('sort') as ProductSort | null
  return {
    search: params.get('q') ?? '',
    category: params.get('category') ?? '',
    sort: sort && SORTS.includes(sort) ? sort : 'recent',
    offset: Number(params.get('offset') ?? 0),
  }
}

export default function CatalogPage() {
  // The filters live in the URL so a search can be shared, bookmarked, and
  // survive a reload — and so the browser's back button behaves.
  const [params, setParams] = useSearchParams()
  const filters = readFilters(params)
  const { data, isPending, isError, refetch } = useProducts(filters)

  function update(next: Partial<Filters>): void {
    const merged = { ...filters, ...next }
    const query = new URLSearchParams()
    if (merged.search) query.set('q', merged.search)
    if (merged.category) query.set('category', merged.category)
    if (merged.sort !== 'recent') query.set('sort', merged.sort)
    // Any filter change sends the reader back to the first page: staying on
    // page 4 of a result set that now holds two items shows nothing.
    if (next.offset) query.set('offset', String(next.offset))
    setParams(query)
  }

  const isFiltered = filters.search !== '' || filters.category !== ''

  return (
    <main className="mx-auto max-w-5xl px-6 py-12 sm:py-16">
      <p className="mb-10 text-sm text-mute">
        Mobilier et objets d’intérieur
        {data
          ? ` — ${data.total} ${data.total > 1 ? 'pièces' : 'pièce'}`
          : null}
      </p>

      <CatalogFilters
        search={filters.search}
        category={filters.category}
        sort={filters.sort}
        onChange={update}
      />

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
          {isFiltered ? (
            <>
              <p className="font-display text-base">
                Aucune pièce ne correspond à cette recherche.
              </p>
              <button
                type="button"
                onClick={() => setParams(new URLSearchParams())}
                className="mt-6 bg-accent px-5 py-2 text-sm text-paper"
              >
                Voir tout le catalogue
              </button>
            </>
          ) : (
            <>
              <p className="font-display text-base">
                Aucune pièce au catalogue pour le moment.
              </p>
              <p className="mt-2 text-sm text-mute">
                Les prochaines arrivées seront visibles ici.
              </p>
            </>
          )}
        </section>
      ) : null}

      {data && data.items.length > 0 ? (
        <>
          <div className="flex flex-col gap-14">
            {data.items.map((product) => (
              <ProductBand key={product.id} product={product} />
            ))}
          </div>

          {data.total > PAGE_SIZE ? (
            <nav className="mt-16 flex items-center justify-between text-sm">
              <button
                type="button"
                disabled={filters.offset === 0}
                onClick={() =>
                  update({ offset: Math.max(0, filters.offset - PAGE_SIZE) })
                }
                className="text-accent disabled:text-mute disabled:opacity-50"
              >
                Page précédente
              </button>
              <span className="text-mute">
                {filters.offset + 1}–
                {Math.min(filters.offset + PAGE_SIZE, data.total)} sur{' '}
                {data.total}
              </span>
              <button
                type="button"
                disabled={filters.offset + PAGE_SIZE >= data.total}
                onClick={() => update({ offset: filters.offset + PAGE_SIZE })}
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
    <div className="flex flex-col gap-14" aria-live="polite" aria-busy="true">
      <span className="sr-only">Chargement du catalogue</span>
      {[0, 1, 2].map((row) => (
        <div key={row} className="flex flex-col gap-5 sm:flex-row sm:gap-8">
          <div className="aspect-[4/3] w-full bg-plate sm:h-40 sm:w-56 sm:shrink-0" />
        </div>
      ))}
    </div>
  )
}
