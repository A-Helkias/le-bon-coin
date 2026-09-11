import type { ProductSort } from './api'
import { useCategories } from './api'

type Props = {
  search: string
  category: string
  sort: ProductSort
  onChange: (next: {
    search?: string
    category?: string
    sort?: ProductSort
  }) => void
}

const SORTS: { value: ProductSort; label: string }[] = [
  { value: 'recent', label: 'Nouveautés' },
  { value: 'price_asc', label: 'Prix croissant' },
  { value: 'price_desc', label: 'Prix décroissant' },
]

export default function CatalogFilters({
  search,
  category,
  sort,
  onChange,
}: Props) {
  const { data: categories } = useCategories()

  return (
    <div className="mb-12 flex flex-col gap-5 sm:flex-row sm:items-end sm:gap-8">
      <div className="flex-1">
        <label htmlFor="catalog-search" className="block text-xs text-mute">
          Rechercher une pièce
        </label>
        <input
          id="catalog-search"
          type="search"
          value={search}
          onChange={(event) => onChange({ search: event.target.value })}
          className="mt-1 w-full border-b border-plate bg-transparent py-2 text-sm focus:border-accent focus:outline-none"
        />
      </div>

      <div>
        <label htmlFor="catalog-category" className="block text-xs text-mute">
          Rayon
        </label>
        <select
          id="catalog-category"
          value={category}
          onChange={(event) => onChange({ category: event.target.value })}
          className="mt-1 border-b border-plate bg-transparent py-2 text-sm focus:border-accent focus:outline-none"
        >
          <option value="">Tous les rayons</option>
          {categories?.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label htmlFor="catalog-sort" className="block text-xs text-mute">
          Trier par
        </label>
        <select
          id="catalog-sort"
          value={sort}
          onChange={(event) =>
            onChange({ sort: event.target.value as ProductSort })
          }
          className="mt-1 border-b border-plate bg-transparent py-2 text-sm focus:border-accent focus:outline-none"
        >
          {SORTS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  )
}
