const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/**
 * Single entry point for every call to the backend.
 *
 * Components never call fetch directly: they go through a TanStack Query hook
 * declared in their feature, and that hook calls this.
 */
export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })

  if (!response.ok) {
    // The backend puts the French, user-facing label in `detail`.
    const body: unknown = await response.json().catch(() => null)
    const detail =
      typeof body === 'object' && body !== null && 'detail' in body
        ? String((body as { detail: unknown }).detail)
        : 'Une erreur est survenue. Réessayez dans un instant.'
    throw new ApiError(detail, response.status)
  }

  // 204 No Content has no body at all: parsing it would reject, and every
  // DELETE in the API answers 204.
  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}
