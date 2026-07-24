import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TodoItem from '../todo-item'

const sampleTodo = { id: 1, title: 'Learn React', completed: false }

describe('TodoItem', () => {
  it('renders the todo title text', () => {
    render(<TodoItem todo={sampleTodo} onToggle={() => {}} onDelete={() => {}} />)
    expect(screen.getByText('Learn React')).toBeInTheDocument()
  })

  it('checkbox reflects completed state — unchecked when not completed', () => {
    render(<TodoItem todo={sampleTodo} onToggle={() => {}} onDelete={() => {}} />)
    expect(screen.getByRole('checkbox')).not.toBeChecked()
  })

  it('checkbox reflects completed state — checked when completed', () => {
    const doneTodo = { ...sampleTodo, completed: true }
    render(<TodoItem todo={doneTodo} onToggle={() => {}} onDelete={() => {}} />)
    expect(screen.getByRole('checkbox')).toBeChecked()
  })

  it('clicking checkbox calls onToggle with id and current completed value', async () => {
    const user = userEvent.setup()
    const onToggle = vi.fn()
    render(<TodoItem todo={sampleTodo} onToggle={onToggle} onDelete={() => {}} />)

    await user.click(screen.getByRole('checkbox'))
    expect(onToggle).toHaveBeenCalledWith(1, false)
    expect(onToggle).toHaveBeenCalledTimes(1)
  })

  it('clicking delete button calls onDelete with id', async () => {
    const user = userEvent.setup()
    const onDelete = vi.fn()
    render(<TodoItem todo={sampleTodo} onToggle={() => {}} onDelete={onDelete} />)

    await user.click(screen.getByRole('button', { name: /delete todo/i }))
    expect(onDelete).toHaveBeenCalledWith(1)
    expect(onDelete).toHaveBeenCalledTimes(1)
  })
})
