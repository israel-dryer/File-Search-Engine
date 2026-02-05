/**
 * SearchResults Component Tests
 * 
 * Functional tests for SearchResults using React Testing Library.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import SearchResults from '../components/SearchResults'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('SearchResults Component', () => {
    const mockResults = [
        {
            id: 'doc1',
            document: 'This is the content of document 1',
            summary: 'Summary of document 1',
            file_path: '/path/to/doc1.pdf',
            file_name: 'doc1.pdf',
            tags: ['AI', 'ML']
        },
        {
            id: 'doc2',
            document: 'Content of document 2',
            summary: 'Summary of document 2',
            file_path: '/path/to/doc2.txt',
            file_name: 'doc2.txt',
            tags: ['Data']
        }
    ]

    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('renders nothing when no results and no AI answer', () => {
        const { container } = render(<SearchResults results={[]} aiAnswer="" />)
        expect(container.firstChild).toBeNull()
    })

    it('renders list of results', () => {
        render(<SearchResults results={mockResults} aiAnswer="" />)

        expect(screen.getByText('This is the content of document 1')).toBeDefined()
        expect(screen.getByText('doc1.pdf')).toBeDefined()
    })

    it('triggers open file API when card is clicked', async () => {
        axios.post.mockResolvedValueOnce({ data: { success: true } })

        render(<SearchResults results={mockResults} aiAnswer="" />)

        const card = screen.getByText('doc1.pdf').closest('.result-card')
        fireEvent.click(card)

        expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/open-file', { path: '/path/to/doc1.pdf' })
    })

    it('triggers open file API when external link button is clicked', async () => {
        axios.post.mockResolvedValueOnce({ data: { success: true } })

        render(<SearchResults results={mockResults} aiAnswer="" />)

        const card = screen.getByText('doc1.pdf').closest('.result-card')
        // Now we can use the title attribute for robust selection
        const button = within(card).getByTitle('Open file externally')

        fireEvent.click(button)

        expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/open-file', { path: '/path/to/doc1.pdf' })
    })

    it('triggers open file API when card is activated via keyboard (Enter)', async () => {
        axios.post.mockResolvedValueOnce({ data: { success: true } })

        render(<SearchResults results={mockResults} aiAnswer="" />)

        const card = screen.getByText('doc1.pdf').closest('.result-card')
        card.focus()
        fireEvent.keyDown(card, { key: 'Enter', code: 'Enter', charCode: 13 })

        expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/open-file', { path: '/path/to/doc1.pdf' })
    })

    it('triggers open file API when card is activated via keyboard (Space)', async () => {
        axios.post.mockResolvedValueOnce({ data: { success: true } })

        render(<SearchResults results={mockResults} aiAnswer="" />)

        const card = screen.getByText('doc1.pdf').closest('.result-card')
        card.focus()
        fireEvent.keyDown(card, { key: ' ', code: 'Space', charCode: 32 })

        expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/open-file', { path: '/path/to/doc1.pdf' })
    })

    it('renders AI answer when provided', () => {
        render(<SearchResults results={[]} aiAnswer="This is an AI generated answer." />)
        expect(screen.getAllByText('This is an AI generated answer.').length).toBeGreaterThan(0)
    })
})
