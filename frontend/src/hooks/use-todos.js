import { useState, useEffect, useCallback } from 'react'
import { todoApi } from '../api/todo-api'

/**
 * Custom hook that manages todo state and API interactions.
 *
 * State: todos[], loading, error, filter
 * Actions: addTodo, toggleTodo, deleteTodo
 * Derived: filteredTodos (client-side filtering by filter value)
 *
 * @returns {{
 *   todos: Array,
 *   loading: boolean,
 *   error: string|null,
 *   filter: string,
 *   setFilter: Function,
 *   addTodo: Function,
 *   toggleTodo: Function,
 *   deleteTodo: Function
 * }}
 */
export function useTodos() {
  const [todos, setTodos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('all')

  // Fetch all todos on mount
  useEffect(() => {
    let cancelled = false

    async function fetchTodos() {
      try {
        setLoading(true)
        setError(null)
        const data = await todoApi.list()
        if (!cancelled) {
          setTodos(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Failed to load todos')
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchTodos()
    return () => {
      cancelled = true
    }
  }, [])

  const addTodo = useCallback(async (text) => {
    try {
      const newTodo = await todoApi.create(text)
      setTodos((prev) => [newTodo, ...prev])
    } catch (err) {
      setError(err.message || 'Failed to add todo')
    }
  }, [])

  const toggleTodo = useCallback(async (id, currentCompleted) => {
    try {
      const updated = await todoApi.update(id, {
        completed: !currentCompleted,
      })
      setTodos((prev) =>
        prev.map((t) => (t.id === id ? updated : t)),
      )
    } catch (err) {
      setError(err.message || 'Failed to toggle todo')
    }
  }, [])

  const deleteTodo = useCallback(async (id) => {
    try {
      await todoApi.remove(id)
      setTodos((prev) => prev.filter((t) => t.id !== id))
    } catch (err) {
      setError(err.message || 'Failed to delete todo')
    }
  }, [])

  // Client-side filtering: All / Active / Completed
  const filteredTodos = todos.filter((t) => {
    if (filter === 'active') return !t.completed
    if (filter === 'completed') return t.completed
    return true
  })

  return {
    todos: filteredTodos,
    loading,
    error,
    filter,
    setFilter,
    addTodo,
    toggleTodo,
    deleteTodo,
  }
}
