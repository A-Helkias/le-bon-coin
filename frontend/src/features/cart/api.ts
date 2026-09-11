import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useSyncExternalStore } from 'react'

import { apiFetch } from '../../api/client'
import type { components } from '../../api/schema'

export type Cart = components['schemas']['CartRead']
export type CartItem = components['schemas']['CartItemRead']

const CART_STORAGE_KEY = 'lebonc-cart-id'

export const cartKeys = {
  all: ['cart'] as const,
  // The id is part of the cache key: when a checkout consumes the cart, the key
  // changes and no stale content can survive under the previous identity.
  detail: (cartId: string | null) => ['cart', cartId] as const,
}

/** The cart is anonymous: its identifier is the only thing that claims it. */
export function storedCartId(): string | null {
  try {
    return localStorage.getItem(CART_STORAGE_KEY)
  } catch {
    // Private browsing, or storage disabled: the visitor simply has no cart yet.
    return null
  }
}

async function openCart(): Promise<string> {
  const cart = await apiFetch<Cart>('/carts', { method: 'POST' })
  try {
    localStorage.setItem(CART_STORAGE_KEY, cart.id)
  } catch {
    // Nothing to do: the cart exists server-side, it just will not be found again.
  }
  announce()
  return cart.id
}

/** Return the current cart id, creating one on first need. */
export async function currentCartId(): Promise<string> {
  return storedCartId() ?? (await openCart())
}

function forgetCart(): void {
  try {
    localStorage.removeItem(CART_STORAGE_KEY)
  } catch {
    // Ignored for the same reason as above.
  }
  announce()
}

// localStorage is not reactive: a component reading it during render never
// learns that it changed. The header lives outside the routed subtree, so it
// does not even re-render on navigation — without this it would show the
// contents of a cart the checkout already consumed.
const listeners = new Set<() => void>()

function announce(): void {
  for (const listener of listeners) {
    listener()
  }
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener)
  return () => {
    listeners.delete(listener)
  }
}

export function useCartId(): string | null {
  return useSyncExternalStore(subscribe, storedCartId, () => null)
}

/**
 * Read the current cart.
 *
 * A visitor who has never added anything has no cart id, and none is created
 * just to display an empty cart.
 */
export function useCart() {
  const cartId = useCartId()

  return useQuery({
    queryKey: cartKeys.detail(cartId),
    queryFn: () => {
      if (cartId === null) {
        throw new Error('Aucun panier à lire.')
      }
      return apiFetch<Cart>(`/carts/${cartId}`)
    },
    enabled: cartId !== null,
  })
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
    onSuccess: () => invalidateCartAndCatalogue(queryClient),
  })
}

export function useSetQuantity() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: { productId: string; quantity: number }) => {
      const cartId = await currentCartId()
      return apiFetch<Cart>(`/carts/${cartId}/items/${input.productId}`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity: input.quantity }),
      })
    },
    onSuccess: () => invalidateCartAndCatalogue(queryClient),
  })
}

export function useRemoveFromCart() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (productId: string) => {
      const cartId = await currentCartId()
      await apiFetch<null>(`/carts/${cartId}/items/${productId}`, {
        method: 'DELETE',
      })
    },
    onSuccess: () => invalidateCartAndCatalogue(queryClient),
  })
}

/** Called once a checkout consumed the cart server-side. */
export function releaseCart(): void {
  forgetCart()
}

function invalidateCartAndCatalogue(
  queryClient: ReturnType<typeof useQueryClient>,
): void {
  // Server-side state wins: invalidate and re-read rather than patching a local
  // copy. Stock moved too, so the catalogue is stale as well.
  void queryClient.invalidateQueries({ queryKey: cartKeys.all })
  void queryClient.invalidateQueries({ queryKey: ['products'] })
}
