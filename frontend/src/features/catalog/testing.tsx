import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactNode } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router'

import type { Product } from './api'

/**
 * Fixtures for tests only. The rule against inventing business data covers the
 * application; simulating a backend response is what tests are for.
 */
export function aProduct(overrides: Partial<Product> = {}): Product {
  return {
    id: '11111111-1111-4111-8111-111111111111',
    sku: 'CHAISE-001',
    name: 'Chaise en chêne',
    description: 'Assise en paille tressée, piètement massif.',
    image_url: 'https://cdn.example.com/chaise.jpg',
    price_cents: 14900,
    stock: 4,
    is_active: true,
    created_at: '2026-09-01T10:00:00Z',
    updated_at: '2026-09-01T10:00:00Z',
    ...overrides,
  }
}

/** Renders through the real router and the real query layer. */
export function renderScreen(ui: ReactNode, route = '/') {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path="/" element={ui} />
          <Route path="/produits/:productId" element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}
