import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import SearchBar from '../components/SearchBar'

describe('SearchBar Shortcuts', () => {
    it('focuses input when Ctrl+K is pressed', () => {
        render(<SearchBar onSearch={vi.fn()} />)
        const input = screen.getByPlaceholderText(/search/i)

        // Ensure input is not focused initially
        expect(document.activeElement).not.toBe(input)

        fireEvent.keyDown(window, { key: 'k', ctrlKey: true })

        expect(document.activeElement).toBe(input)
    })

    it('focuses input when / is pressed', () => {
        render(<SearchBar onSearch={vi.fn()} />)
        const input = screen.getByPlaceholderText(/search/i)

        expect(document.activeElement).not.toBe(input)

        fireEvent.keyDown(window, { key: '/' })

        expect(document.activeElement).toBe(input)
    })

    it('does not focus on / if already typing in an input', () => {
        render(
            <div>
                <input aria-label="Other Input" />
                <SearchBar onSearch={vi.fn()} />
            </div>
        )
        const otherInput = screen.getByLabelText('Other Input')
        const searchInput = screen.getByPlaceholderText(/search/i)

        otherInput.focus()
        expect(document.activeElement).toBe(otherInput)

        fireEvent.keyDown(window, { key: '/' })

        expect(document.activeElement).toBe(otherInput)
        expect(document.activeElement).not.toBe(searchInput)
    })
})
