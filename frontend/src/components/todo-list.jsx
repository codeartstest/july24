import React from 'react'
import TodoItem from './todo-item'

/**
 * Renders the list of TodoItem components.
 * Shows loading and empty states.
 */
export default function TodoList({ todos, loading, onToggle, onDelete }) {
  if (loading) {
    return <p className="todo-list__empty">Loading…</p>
  }

  if (todos.length === 0) {
    return <p className="todo-list__empty">No todos yet. Add one above!</p>
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onDelete={onDelete}
        />
      ))}
    </ul>
  )
}
