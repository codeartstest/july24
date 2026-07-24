import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TodoList from '../todo-list'

const sampleTodos = [
  { id: 1, title: 'Task A', completed: false },
  { id: 2, title: 'Task B', completed: true },
  { id: 3, title: 'Task C', completed: false },
]

describe('TodoList', () => {
  it('renders multiple todo items', () => {
    render(
      <TodoList todos={sampleTodos} loading={false} onToggle={() => {}} onDelete={() => {}} />,
    )
    expect(screen.getByText('Task A')).toBeInTheDocument()
    expect(screen.getByText('Task B')).toBeInTheDocument()
    expect(screen.getByText('Task C')).toBeInTheDocument()
  })

  it('shows empty state message when there are no todos', () => {
    render(
      <TodoList todos={[]} loading={false} onToggle={() => {}} onDelete={() => {}} />,
    )
    expect(screen.getByText(/no todos yet/i)).toBeInTheDocument()
  })

  it('shows loading state when loading is true', () => {
    render(
      <TodoList todos={[]} loading={true} onToggle={() => {}} onDelete={() => {}} />,
    )
    expect(screen.getByText(/loading/i)).toBeInTheDocument()
  })
})
