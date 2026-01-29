/**
 * SearchBar Component Tests
 * 
 * Functional tests for the SearchBar component.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import SearchBar from '../components/SearchBar'

describe('SearchBar Component', () => {
    it('updates input value when typing', () => {
        render(<SearchBar onSearch={vi.fn()} />)

        const input = screen.getByPlaceholderText(/search/i)
        fireEvent.change(input, { target: { value: 'machine learning' } })

        expect(input.value).toBe('machine learning')
    })

    it('triggers onSearch when form is submitted', () => {
        const onSearch = vi.fn()
        render(<SearchBar onSearch={onSearch} />)

        const input = screen.getByPlaceholderText(/search/i)
        fireEvent.change(input, { target: { value: 'neural networks' } })

        fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })

        // Use form submit if available
        const form = input.closest('form')
        if (form) fireEvent.submit(form)

        expect(onSearch).toHaveBeenCalledWith('neural networks')
    })

    it('shows loading state', () => {
        render(<SearchBar isLoading={true} onSearch={vi.fn()} />)
        const input = screen.getByPlaceholderText(/search/i)
        expect(input.disabled).toBe(true)
    })
})
