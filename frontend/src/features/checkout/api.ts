import { useMutation, useQueryClient } from '@tanstack/react-query'

import { apiFetch } from '../../api/client'
import type { components } from '../../api/schema'
import { cartKeys, currentCartId, releaseCart } from '../cart/api'

export type Order = components['schemas']['OrderRead']
export type OrderCreate = components['schemas']['OrderCreate']

export type CustomerDetails = Omit<OrderCreate, 'cart_id'>

export function useCreateOrder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (details: CustomerDetails) => {
      const cartId = await currentCartId()
      return apiFetch<Order>('/orders', {
        method: 'POST',
        body: JSON.stringify({ cart_id: cartId, ...details }),
      })
    },
    onSuccess: () => {
      // The server consumed the cart: keeping its id would point at a deleted
      // resource and every later read would 404.
      releaseCart()
      // Removed, not invalidated: an invalidation would refetch a cart the
      // server has just deleted.
      queryClient.removeQueries({ queryKey: cartKeys.all })
      void queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })
}
