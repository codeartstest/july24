import React from 'react'
import { useTodos } from './hooks/use-todos'
import TodoInput from './components/todo-input'
import TodoList from './components/todo-list'
import TodoFilter from './components/todo-filter'

/**
 * Root component — renders the todo app layout.
 * Delegates state management to the useTodos hook.
 */
export default function App() {
  const {
    todos,
    loading,
    error,
    filter,
    setFilter,
    addTodo,
    toggleTodo,
    deleteTodo,
  } = useTodos()

  return (
    <div className="app">
      <header className="app-header">
        <h1>Todo List</h1>
      </header>
      <main className="app-main">
        <TodoInput onAdd={addTodo} />
        {error && <p className="app-error">{error}</p>}
        <TodoFilter filter={filter} setFilter={setFilter} />
        <TodoList
          todos={todos}
          loading={loading}
          onToggle={toggleTodo}
          onDelete={deleteTodo}
        />
      </main>
    </div>
  )
}
