/**
 * SearchHistory Component Tests
 * 
 * Tests for the SearchHistory component including list rendering
 * and delete interactions.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SearchHistory from '../components/SearchHistory'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('SearchHistory Component', () => {
    const mockHistory = [
        { id: 1, query: 'react hooks', timestamp: new Date().toISOString(), result_count: 5 },
        { id: 2, query: 'vitest testing', timestamp: new Date().toISOString(), result_count: 12 }
    ]

    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('renders nothing when not open', () => {
        render(<SearchHistory isOpen={false} />)
        expect(screen.queryByText('Search History')).toBeNull()
    })

    it('fetches and renders history when opened', async () => {
        axios.get.mockResolvedValueOnce({ data: mockHistory })

        render(<SearchHistory isOpen={true} onClose={vi.fn()} onSelectQuery={vi.fn()} />)

        expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/api/search/history')

        // Wait for loading to finish and items to appear
        await waitFor(() => {
            expect(screen.getByText('react hooks')).toBeDefined()
            expect(screen.getByText('vitest testing')).toBeDefined()
        })
    })

    it('calls onSelectQuery and onClose when an item is clicked', async () => {
        axios.get.mockResolvedValueOnce({ data: mockHistory })
        const onSelectQuery = vi.fn()
        const onClose = vi.fn()

        render(<SearchHistory isOpen={true} onClose={onClose} onSelectQuery={onSelectQuery} />)

        await waitFor(() => screen.getByText('react hooks'))

        fireEvent.click(screen.getByText('react hooks'))

        expect(onSelectQuery).toHaveBeenCalledWith('react hooks')
        expect(onClose).toHaveBeenCalled()
    })

    it('deletes an item when delete button is clicked', async () => {
        axios.get.mockResolvedValueOnce({ data: mockHistory })
        axios.delete.mockResolvedValueOnce({ data: { success: true } })

        render(<SearchHistory isOpen={true} onClose={vi.fn()} onSelectQuery={vi.fn()} />)

        await waitFor(() => screen.getByText('react hooks'))

        // Find delete buttons (Trash2 icon usually inside a button)
        const deleteButtons = screen.getAllByRole('button')
        // Filter for the specific delete button if needed, but here we can just pick the one for the item
        // Since buttons are likely: Close (1) + Delete (2). 
        // Let's use a more specific selector implies knowing structure. 
        // We can look for the button containing the delete icon or just use index.
        // Actually, the component has aria-label or accessible role? No.
        // The delete button is the one inside the list item.

        // Let's assume the last 2 buttons are delete buttons because the first one is likely Close
        // Better trigger:
        const items = screen.getAllByText(/results/i) // Get context of items
        const firstItem = items[0].closest('div').parentElement
        const deleteBtn = firstItem.querySelector('button')

        fireEvent.click(deleteBtn)

        expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/api/search/history/1')

        // Verify item is removed from view (optimistic update or after re-render)
        await waitFor(() => {
            expect(screen.queryByText('react hooks')).toBeNull()
        })
    })

    it('handles empty history', async () => {
        axios.get.mockResolvedValueOnce({ data: [] })

        render(<SearchHistory isOpen={true} />)

        await waitFor(() => {
            expect(screen.getByText('No history')).toBeDefined()
        })
    })
})
