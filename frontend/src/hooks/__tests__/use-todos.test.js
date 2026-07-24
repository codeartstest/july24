import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'

// Mock the todoApi module — hoisted above imports by Vitest
vi.mock('../../api/todo-api', () => ({
  todoApi: {
    list: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    remove: vi.fn(),
    get: vi.fn(),
  },
}))

import { useTodos } from '../use-todos'
import { todoApi } from '../../api/todo-api'

describe('useTodos', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // ------------------------------------------------------------------ fetch

  it('fetches todos on mount via GET (todoApi.list)', async () => {
    const mockTodos = [
      { id: 1, title: 'Task 1', completed: false },
      { id: 2, title: 'Task 2', completed: true },
    ]
    todoApi.list.mockResolvedValue(mockTodos)

    const { result } = renderHook(() => useTodos())

    // Initially loading
    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(todoApi.list).toHaveBeenCalledTimes(1)
    expect(result.current.todos).toEqual(mockTodos)
    expect(result.current.error).toBeNull()
  })

  // ------------------------------------------------------------------ addTodo

  it('addTodo calls POST (todoApi.create) and prepends to list', async () => {
    const existing = { id: 1, title: 'Old', completed: false }
    const created = { id: 2, title: 'New', completed: false }
    todoApi.list.mockResolvedValue([existing])
    todoApi.create.mockResolvedValue(created)

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.todos).toHaveLength(1)
    })

    await act(async () => {
      await result.current.addTodo('New')
    })

    expect(todoApi.create).toHaveBeenCalledWith('New')
    expect(result.current.todos).toHaveLength(2)
    // New todo is prepended (index 0)
    expect(result.current.todos[0]).toEqual(created)
    expect(result.current.todos[1]).toEqual(existing)
  })

  // ---------------------------------------------------------------- toggleTodo

  it('toggleTodo calls PATCH (todoApi.update) and updates state', async () => {
    const todo = { id: 1, title: 'Toggle me', completed: false }
    const updated = { id: 1, title: 'Toggle me', completed: true }
    todoApi.list.mockResolvedValue([todo])
    todoApi.update.mockResolvedValue(updated)

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.todos).toHaveLength(1)
    })

    expect(result.current.todos[0].completed).toBe(false)

    await act(async () => {
      await result.current.toggleTodo(1, false)
    })

    expect(todoApi.update).toHaveBeenCalledWith(1, { completed: true })
    expect(result.current.todos[0].completed).toBe(true)
  })

  // ---------------------------------------------------------------- deleteTodo

  it('deleteTodo calls DELETE (todoApi.remove) and removes from list', async () => {
    const todo = { id: 1, title: 'Delete me', completed: false }
    todoApi.list.mockResolvedValue([todo])
    todoApi.remove.mockResolvedValue(null)

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.todos).toHaveLength(1)
    })

    await act(async () => {
      await result.current.deleteTodo(1)
    })

    expect(todoApi.remove).toHaveBeenCalledWith(1)
    expect(result.current.todos).toHaveLength(0)
  })

  // ------------------------------------------------------------------ filters

  it('filter defaults to "all"', async () => {
    todoApi.list.mockResolvedValue([])
    const { result } = renderHook(() => useTodos())

    expect(result.current.filter).toBe('all')
  })

  it('filter=active shows only incomplete todos', async () => {
    const todos = [
      { id: 1, title: 'Active task', completed: false },
      { id: 2, title: 'Done task', completed: true },
    ]
    todoApi.list.mockResolvedValue(todos)

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.todos).toHaveLength(2)
    })

    act(() => {
      result.current.setFilter('active')
    })

    expect(result.current.filter).toBe('active')
    expect(result.current.todos).toHaveLength(1)
    expect(result.current.todos[0].title).toBe('Active task')
  })

  it('filter=completed shows only completed todos', async () => {
    const todos = [
      { id: 1, title: 'Active task', completed: false },
      { id: 2, title: 'Done task', completed: true },
    ]
    todoApi.list.mockResolvedValue(todos)

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.todos).toHaveLength(2)
    })

    act(() => {
      result.current.setFilter('completed')
    })

    expect(result.current.filter).toBe('completed')
    expect(result.current.todos).toHaveLength(1)
    expect(result.current.todos[0].title).toBe('Done task')
  })

  // ----------------------------------------------------------- loading & error

  it('sets loading=true during fetch and loading=false after', async () => {
    todoApi.list.mockResolvedValue([])

    const { result } = renderHook(() => useTodos())

    expect(result.current.loading).toBe(true)

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.todos).toEqual([])
  })

  it('sets error message when fetch fails', async () => {
    todoApi.list.mockRejectedValue(new Error('Network error'))

    const { result } = renderHook(() => useTodos())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.error).toBe('Network error')
    expect(result.current.todos).toEqual([])
  })
})
