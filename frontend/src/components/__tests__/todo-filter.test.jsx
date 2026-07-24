import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import TodoFilter from '../todo-filter'

describe('TodoFilter', () => {
  it('renders All, Active, and Completed buttons', () => {
    render(<TodoFilter filter="all" setFilter={() => {}} />)
    expect(screen.getByRole('button', { name: /^all$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /active/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /completed/i })).toBeInTheDocument()
  })

  it('highlights the active filter button with the active class', () => {
    render(<TodoFilter filter="active" setFilter={() => {}} />)
    const activeBtn = screen.getByRole('button', { name: /active/i })
    expect(activeBtn).toHaveClass('todo-filter__btn--active')
  })

  it('does not highlight non-active filter buttons', () => {
    render(<TodoFilter filter="all" setFilter={() => {}} />)
    const completedBtn = screen.getByRole('button', { name: /completed/i })
    expect(completedBtn).not.toHaveClass('todo-filter__btn--active')
  })

  it('calls setFilter with the clicked filter value', async () => {
    const user = userEvent.setup()
    const setFilter = vi.fn()
    render(<TodoFilter filter="all" setFilter={setFilter} />)

    await user.click(screen.getByRole('button', { name: /completed/i }))
    expect(setFilter).toHaveBeenCalledWith('completed')
    expect(setFilter).toHaveBeenCalledTimes(1)
  })

  it('can switch to the Active filter', async () => {
    const user = userEvent.setup()
    const setFilter = vi.fn()
    render(<TodoFilter filter="all" setFilter={setFilter} />)

    await user.click(screen.getByRole('button', { name: /active/i }))
    expect(setFilter).toHaveBeenCalledWith('active')
  })
})
