import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TodoInput from '../todo-input'

describe('TodoInput', () => {
  it('renders an input field and Add button', () => {
    render(<TodoInput onAdd={() => {}} />)
    expect(screen.getByPlaceholderText('What needs to be done?')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /add/i })).toBeInTheDocument()
  })

  it('calls onAdd with trimmed text when Add button is clicked', async () => {
    const user = userEvent.setup()
    const onAdd = vi.fn()
    render(<TodoInput onAdd={onAdd} />)

    const input = screen.getByPlaceholderText('What needs to be done?')
    await user.type(input, '  Buy milk  ')
    await user.click(screen.getByRole('button', { name: /add/i }))

    expect(onAdd).toHaveBeenCalledWith('Buy milk')
    expect(onAdd).toHaveBeenCalledTimes(1)
  })

  it('calls onAdd when Enter is pressed', async () => {
    const user = userEvent.setup()
    const onAdd = vi.fn()
    render(<TodoInput onAdd={onAdd} />)

    const input = screen.getByPlaceholderText('What needs to be done?')
    await user.type(input, 'Walk the dog')
    await user.keyboard('{Enter}')

    expect(onAdd).toHaveBeenCalledWith('Walk the dog')
    expect(onAdd).toHaveBeenCalledTimes(1)
  })

  it('does not call onAdd when input is empty or whitespace-only', async () => {
    const user = userEvent.setup()
    const onAdd = vi.fn()
    render(<TodoInput onAdd={onAdd} />)

    // Empty submit
    await user.click(screen.getByRole('button', { name: /add/i }))
    expect(onAdd).not.toHaveBeenCalled()

    // Whitespace-only submit
    const input = screen.getByPlaceholderText('What needs to be done?')
    await user.type(input, '   ')
    await user.click(screen.getByRole('button', { name: /add/i }))
    expect(onAdd).not.toHaveBeenCalled()
  })

  it('clears the input field after adding', async () => {
    const user = userEvent.setup()
    const onAdd = vi.fn()
    render(<TodoInput onAdd={onAdd} />)

    const input = screen.getByPlaceholderText('What needs to be done?')
    await user.type(input, 'New task')
    await user.click(screen.getByRole('button', { name: /add/i }))

    expect(input).toHaveValue('')
  })
})
