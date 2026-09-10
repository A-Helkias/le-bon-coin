import type { RequestHandler } from 'msw'

/**
 * Network handlers shared by every test. Feature tests add their own with
 * `server.use(...)` rather than editing this list.
 */
export const handlers: RequestHandler[] = []
