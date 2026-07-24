import React from 'react'

/**
 * Single todo row: checkbox, title text, delete button.
 * Calls onToggle(id, currentCompleted) and onDelete(id).
 */
export default function TodoItem({ todo, onToggle, onDelete }) {
  return (
    <li className={`todo-item ${todo.completed ? 'todo-item--done' : ''}`}>
      <input
        type="checkbox"
        className="todo-item__checkbox"
        checked={todo.completed}
        onChange={() => onToggle(todo.id, todo.completed)}
      />
      <span className="todo-item__text">{todo.title}</span>
      <button
        className="todo-item__delete"
        onClick={() => onDelete(todo.id)}
        aria-label="Delete todo"
      >
        &times;
      </button>
    </li>
  )
}
