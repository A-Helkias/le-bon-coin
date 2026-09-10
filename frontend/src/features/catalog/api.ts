import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { apiFetch } from '../../api/client'
import type { components } from '../../api/schema'

export type Product = components['schemas']['ProductRead']
export type ProductPage = components['schemas']['Page_ProductRead_']
export type Cart = components['schemas']['CartRead']

export const catalogKeys = {
  all: ['products'] as const,
  list: (offset: number) => ['products', 'list', offset] as const,
  detail: (id: string) => ['products', 'detail', id] as const,
}

export const PAGE_SIZE = 20

export function useProducts(offset = 0) {
  return useQuery({
    queryKey: catalogKeys.list(offset),
    queryFn: () =>
      apiFetch<ProductPage>(`/products?limit=${PAGE_SIZE}&offset=${offset}`),
  })
}

export function useProduct(productId: string) {
  return useQuery({
    queryKey: catalogKeys.detail(productId),
    queryFn: () => apiFetch<Product>(`/products/${productId}`),
  })
}

export const cartKeys = {
  detail: (id: string) => ['cart', id] as const,
}

const CART_STORAGE_KEY = 'lebonc-cart-id'

/** The cart is anonymous: its id is the only thing that identifies it. */
async function currentCartId(): Promise<string> {
  const stored = localStorage.getItem(CART_STORAGE_KEY)
  if (stored) {
    return stored
  }
  const cart = await apiFetch<Cart>('/carts', { method: 'POST' })
  localStorage.setItem(CART_STORAGE_KEY, cart.id)
  return cart.id
}

export function useAddToCart() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: { productId: string; quantity: number }) => {
      const cartId = await currentCartId()
      return apiFetch<Cart>(`/carts/${cartId}/items`, {
        method: 'POST',
        body: JSON.stringify({
          product_id: input.productId,
          quantity: input.quantity,
        }),
      })
    },
    onSuccess: (cart) => {
      // Server-side state wins: invalidate and re-read rather than patching
      // a local copy. Stock changed too, so the catalogue is stale.
      void queryClient.invalidateQueries({ queryKey: cartKeys.detail(cart.id) })
      void queryClient.invalidateQueries({ queryKey: catalogKeys.all })
    },
  })
}
