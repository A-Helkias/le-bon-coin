import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import type { ReactNode } from 'react'

import type { Cart, CartItem } from './features/cart/api'
import type { Product } from './features/catalog/api'
import type { Order } from './features/checkout/api'

/**
 * Fixtures for tests only. The rule against inventing business data covers the
 * application; simulating a backend response is exactly what tests are for.
 */
export function aProduct(overrides: Partial<Product> = {}): Product {
  return {
    id: '11111111-1111-4111-8111-111111111111',
    sku: 'ASS-001',
    name: 'Chaise en chêne',
    description: 'Assise en paille tressée, piètement massif.',
    category: 'Assises',
    image_url: 'https://cdn.example.com/chaise.jpg',
    price_cents: 14900,
    stock: 4,
    is_active: true,
    created_at: '2026-09-01T10:00:00Z',
    updated_at: '2026-09-01T10:00:00Z',
    ...overrides,
  }
}

export function aCartItem(overrides: Partial<CartItem> = {}): CartItem {
  return {
    product_id: '11111111-1111-4111-8111-111111111111',
    product_name: 'Chaise en chêne',
    product_sku: 'ASS-001',
    unit_price_cents: 14900,
    quantity: 2,
    line_total_cents: 29800,
    ...overrides,
  }
}

export function aCart(overrides: Partial<Cart> = {}): Cart {
  const items = overrides.items ?? [
    aCartItem(),
    aCartItem({
      product_id: '44444444-4444-4444-8444-444444444444',
      product_name: 'Suspension en rotin',
      product_sku: 'LUM-002',
      unit_price_cents: 8900,
      quantity: 1,
      line_total_cents: 8900,
    }),
  ]
  return {
    id: '22222222-2222-4222-8222-222222222222',
    user_id: null,
    items,
    total_cents: items.reduce((sum, item) => sum + item.line_total_cents, 0),
    created_at: '2026-09-01T10:00:00Z',
    updated_at: '2026-09-01T10:00:00Z',
    ...overrides,
  }
}

export function anOrder(overrides: Partial<Order> = {}): Order {
  return {
    id: '33333333-3333-4333-8333-333333333333',
    user_id: null,
    status: 'pending',
    total_cents: 29800,
    customer_email: 'camille@example.com',
    customer_name: 'Camille Martin',
    shipping_address: '12 rue des Lilas',
    shipping_postal_code: '75011',
    shipping_city: 'Paris',
    shipping_country: 'FR',
    items: [
      {
        product_id: '11111111-1111-4111-8111-111111111111',
        product_name: 'Chaise en chêne',
        product_sku: 'ASS-001',
        unit_price_cents: 14900,
        quantity: 2,
        line_total_cents: 29800,
      },
    ],
    created_at: '2026-09-01T10:00:00Z',
    updated_at: '2026-09-01T10:00:00Z',
    ...overrides,
  }
}

/**
 * Renders through the real router and the real query layer.
 *
 * `path` is declared so a screen reading `useParams` receives them, exactly as
 * it would under the application's own routes.
 */
export function renderScreen(ui: ReactNode, route = '/', path = '*') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path={path} element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

export const CART_STORAGE_KEY = 'lebonc-cart-id'
