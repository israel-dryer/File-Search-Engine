/**
 * ModelManager Component Tests
 * 
 * Functional tests for ModelManager using React Testing Library.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import ModelManager from '../components/ModelManager'
import axios from 'axios'

// Mock axios and window.confirm
vi.mock('axios')
global.confirm = vi.fn(() => true)

describe('ModelManager Component', () => {
    const mockAvailableModels = [
        { id: 'phi-2', name: 'Phi-2', size: '1.7 GB', ram_required: 4, recommended: true },
        { id: 'tinyllama', name: 'TinyLlama', size: '600 MB', ram_required: 2 }
    ]

    const mockLocalModels = [
        { id: 'phi-2', name: 'Phi-2', path: '/models/phi-2.gguf', size: 1700000000 }
    ]

    beforeEach(() => {
        vi.clearAllMocks()
        axios.get.mockImplementation((url) => {
            if (url.includes('/api/models/available')) return Promise.resolve({ data: mockAvailableModels })
            if (url.includes('/api/models/local')) return Promise.resolve({ data: mockLocalModels })
            if (url.includes('/api/models/status')) return Promise.resolve({ data: { downloading: false } })
            return Promise.resolve({ data: {} })
        })
    })

    it('renders and fetches models', async () => {
        render(<ModelManager activeModel="phi-2" onSelectModel={vi.fn()} selectedPath="" />)

        await waitFor(() => {
            // Use getAllByText because Phi-2 appears in both lists
            expect(screen.getAllByText('Phi-2').length).toBeGreaterThan(0)
            expect(screen.getByText(/1.6 GB/i)).toBeDefined()
        })
    })

    it('triggers download when download button is clicked', async () => {
        axios.post.mockResolvedValueOnce({ data: { status: 'success' } })

        render(<ModelManager activeModel="" onSelectModel={vi.fn()} selectedPath="" />)

        await waitFor(() => screen.getAllByText('TinyLlama')[0])

        const cards = screen.getAllByText('TinyLlama').map(el => el.closest('.border'))
        const card = cards.find(c => within(c).queryByText(/Download/i))
        const downloadBtn = within(card).getByRole('button', { name: /Download/i })

        fireEvent.click(downloadBtn)

        expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/models/download/tinyllama')
    })

    it('triggers select model callback', async () => {
        const onSelectModel = vi.fn()
        render(<ModelManager activeModel="" onSelectModel={onSelectModel} selectedPath="" />)

        await waitFor(() => screen.getAllByText('Phi-2')[0])

        // Find the Select button. It might be multiple if multiple models?
        // But only downloaded models have Select button.
        const selectBtn = screen.getByText('Select')
        fireEvent.click(selectBtn)

        expect(onSelectModel).toHaveBeenCalledWith('/models/phi-2.gguf')
    })

    it('triggers delete model when delete button is clicked', async () => {
        axios.delete.mockResolvedValueOnce({ data: { success: true } })

        render(<ModelManager activeModel="" onSelectModel={vi.fn()} selectedPath="" />)

        await waitFor(() => screen.getAllByText('Phi-2')[0])

        const trashBtn = screen.getByTitle('Delete Model')
        fireEvent.click(trashBtn)

        expect(global.confirm).toHaveBeenCalled()
        expect(axios.delete).toHaveBeenCalledWith(
            'http://localhost:8000/api/models/delete',
            expect.objectContaining({ data: { path: '/models/phi-2.gguf' } })
        )
    })
})
