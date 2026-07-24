/**
 * Fetch wrapper for the Todo REST API.
 *
 * All endpoints are prefixed with /api (proxied to the backend by Vite
 * dev server or served directly in production).
 *
 * Contract (see design.md §2.2):
 *   GET    /api/todos        → 200  [{id, title, completed, created_at, updated_at}]
 *   POST   /api/todos        → 201  {id, title, completed, created_at, updated_at}
 *   GET    /api/todos/{id}   → 200  {id, title, completed, created_at, updated_at}
 *   PATCH  /api/todos/{id}   → 200  {id, title, completed, created_at, updated_at}
 *   DELETE /api/todos/{id}   → 204  (no body)
 */

const BASE_URL = '/api/todos'

/**
 * Internal helper: performs fetch, normalises errors, parses JSON.
 *
 * @param {string} url       - Full URL path
 * @param {object} options   - Fetch options (method, body, etc.)
 * @returns {Promise<object|null>} Parsed JSON body or null for 204
 */
async function request(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!res.ok) {
    // Attempt to extract a human-readable error message
    const body = await res.json().catch(() => ({}))
    const message = body.detail
      ? typeof body.detail === 'string'
        ? body.detail
        : body.detail.map((d) => d.msg).join(', ')
      : `Request failed: ${res.status}`
    throw new Error(message)
  }

  // 204 No Content — nothing to parse
  if (res.status === 204) {
    return null
  }

  return res.json()
}

export const todoApi = {
  /** GET /api/todos — list all todos */
  list() {
    return request(BASE_URL)
  },

  /** GET /api/todos/{id} — get a single todo */
  get(id) {
    return request(`${BASE_URL}/${id}`)
  },

  /** POST /api/todos — create a new todo */
  create(title) {
    return request(BASE_URL, {
      method: 'POST',
      body: JSON.stringify({ title }),
    })
  },

  /** PATCH /api/todos/{id} — update todo fields (title?, completed?) */
  update(id, data) {
    return request(`${BASE_URL}/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  },

  /** DELETE /api/todos/{id} — delete a todo (returns 204) */
  remove(id) {
    return request(`${BASE_URL}/${id}`, {
      method: 'DELETE',
    })
  },
}
