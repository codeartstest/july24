import React from 'react'

const FILTERS = ['all', 'active', 'completed']

/**
 * All / Active / Completed filter buttons.
 * Highlights the active filter.
 */
export default function TodoFilter({ filter, setFilter }) {
  return (
    <div className="todo-filter">
      {FILTERS.map((f) => (
        <button
          key={f}
          className={`todo-filter__btn ${
            filter === f ? 'todo-filter__btn--active' : ''
          }`}
          onClick={() => setFilter(f)}
        >
          {f.charAt(0).toUpperCase() + f.slice(1)}
        </button>
      ))}
    </div>
  )
}
