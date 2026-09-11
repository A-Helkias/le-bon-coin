import { useQuery } from '@tanstack/react-query'

import { apiFetch } from '../../api/client'
import type { components } from '../../api/schema'

export type Product = components['schemas']['ProductRead']
export type ProductPage = components['schemas']['Page_ProductRead_']
export type ProductSort = components['schemas']['ProductSort']

export type CatalogFilters = {
  search: string
  category: string
  sort: ProductSort
  offset: number
}

export const PAGE_SIZE = 12

export const catalogKeys = {
  all: ['products'] as const,
  // The filters belong in the key: without them two different searches would
  // share one cache entry.
  list: (filters: CatalogFilters) => ['products', 'list', filters] as const,
  detail: (id: string) => ['products', 'detail', id] as const,
  categories: ['products', 'categories'] as const,
}

function buildQuery(filters: CatalogFilters): string {
  const params = new URLSearchParams({
    limit: String(PAGE_SIZE),
    offset: String(filters.offset),
    sort: filters.sort,
  })
  if (filters.search) {
    params.set('q', filters.search)
  }
  if (filters.category) {
    params.set('category', filters.category)
  }
  return params.toString()
}

export function useProducts(filters: CatalogFilters) {
  return useQuery({
    queryKey: catalogKeys.list(filters),
    queryFn: () => apiFetch<ProductPage>(`/products?${buildQuery(filters)}`),
  })
}

export function useProduct(productId: string) {
  return useQuery({
    queryKey: catalogKeys.detail(productId),
    queryFn: () => apiFetch<Product>(`/products/${productId}`),
  })
}

/** The aisles come from the catalogue, never from a list written here. */
export function useCategories() {
  return useQuery({
    queryKey: catalogKeys.categories,
    queryFn: () => apiFetch<string[]>('/products/categories'),
  })
}
