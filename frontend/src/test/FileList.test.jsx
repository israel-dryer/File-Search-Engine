/**
 * FileList Component Tests
 * 
 * Tests for the FileList component including list rendering
 * and file removal interactions.
 */

import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import FileList from '../components/FileList'

describe('FileList Component', () => {
    const mockFiles = [
        {
            id: 1,
            filename: 'report.pdf',
            path: '/docs/report.pdf',
            size_bytes: 1024 * 1024,
            modified_date: new Date().toISOString(),
            chunk_count: 5
        },
        {
            id: 2,
            filename: 'data.xlsx',
            path: '/docs/data.xlsx',
            size_bytes: 5 * 1024,
            modified_date: new Date().toISOString(),
            chunk_count: 2
        }
    ]

    it('renders empty state when no files provided', () => {
        render(<FileList files={[]} />)
        expect(screen.getByText('No files indexed yet')).toBeDefined()
    })

    it('renders list of files', () => {
        render(<FileList files={mockFiles} />)

        expect(screen.getByText('Indexed Files (2)')).toBeDefined()
        expect(screen.getByText('report.pdf')).toBeDefined()
        expect(screen.getByText('data.xlsx')).toBeDefined()
    })

    it('formats file sizes correctly', () => {
        render(<FileList files={mockFiles} />)

        expect(screen.getByText(/1 MB/)).toBeDefined()
        expect(screen.getByText(/5 KB/)).toBeDefined()
    })

    it('calls onRemove when trash button is clicked', () => {
        const onRemove = vi.fn()
        render(<FileList files={mockFiles} onRemove={onRemove} />)

        // Click delete on first item
        const deleteButtons = screen.getAllByRole('button')
        fireEvent.click(deleteButtons[0])

        expect(onRemove).toHaveBeenCalledWith(1)
    })

    it('does not show remove buttons if onRemove is not provided', () => {
        render(<FileList files={mockFiles} />) // No onRemove prop

        const buttons = screen.queryAllByRole('button')
        expect(buttons.length).toBe(0)
    })
})
