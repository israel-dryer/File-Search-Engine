/**
 * SettingsModal Component Tests
 * 
 * Functional tests for SettingsModal using React Testing Library.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import SettingsModal from '../components/SettingsModal'
import axios from 'axios'

// Mock axios and window.confirm
vi.mock('axios')
global.confirm = vi.fn(() => true)
global.alert = vi.fn()

// Mock ModelManager component since we test it separately
vi.mock('../components/ModelManager', () => ({
    default: () => <div data-testid="model-manager">Model Manager Mock</div>
}))

describe('SettingsModal Component', () => {
    const mockConfig = {
        folders: ['C:/Users/test/Documents'],
        auto_index: false,
        provider: 'local',
        openai_api_key: '',
        gemini_api_key: '',
        anthropic_api_key: '',
        grok_api_key: '',
        local_model_path: '',
        local_model_type: 'llamacpp'
    }

    const mockFolderHistory = ['C:/Old/Folder']

    beforeEach(() => {
        vi.clearAllMocks()
        axios.get.mockImplementation((url) => {
            if (url.includes('/api/config')) return Promise.resolve({ data: mockConfig })
            if (url.includes('/api/index/status')) return Promise.resolve({ data: { running: false } })
            if (url.includes('/api/folders/history')) return Promise.resolve({ data: mockFolderHistory })
            if (url.includes('/api/cache/stats')) return Promise.resolve({ data: { total_entries: 0, total_hits: 0 } })
            return Promise.resolve({ data: {} })
        })
    })

    it('renders correctly when open', async () => {
        render(<SettingsModal isOpen={true} onClose={vi.fn()} onSave={vi.fn()} activeModel="" />)

        await waitFor(() => {
            expect(screen.getByText('Settings')).toBeDefined()
            expect(screen.getByText('C:/Users/test/Documents')).toBeDefined()
        })
    })

    it('does not render when closed', () => {
        const { container } = render(<SettingsModal isOpen={false} onClose={vi.fn()} onSave={vi.fn()} activeModel="" />)
        expect(container.firstChild).toBeNull()
    })

    it('clears search history when button is clicked', async () => {
        axios.delete.mockResolvedValueOnce({ data: { success: true } })

        render(<SettingsModal isOpen={true} onClose={vi.fn()} onSave={vi.fn()} activeModel="" />)

        await waitFor(() => screen.getByText('Settings'))

        const clearBtn = screen.getByText('Clear Search History')
        fireEvent.click(clearBtn)

        expect(global.confirm).toHaveBeenCalled()
        expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/api/search/history')
    })

    it('removes a folder from list', async () => {
        render(<SettingsModal isOpen={true} onClose={vi.fn()} onSave={vi.fn()} activeModel="" />)

        await waitFor(() => screen.getByText('C:/Users/test/Documents'))

        // Find the folder row
        const folderRow = screen.getByText('C:/Users/test/Documents').closest('div').parentElement
        // Find the delete button within it (it's the button with Trash icon, typically last child)
        const deleteBtn = folderRow.querySelector('button')

        fireEvent.click(deleteBtn)

        // It should update config locally and call save (POST /api/config)
        expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/api/config', expect.objectContaining({
            folders: []
        }))
    })

    it('clears all folder history via dropdown', async () => {
        axios.delete.mockResolvedValueOnce({ data: { success: true } })

        render(<SettingsModal isOpen={true} onClose={vi.fn()} onSave={vi.fn()} activeModel="" />)

        await waitFor(() => screen.getByText('Settings'))

        // Wait for the history button to appear (it only appears if folderHistory.length > 0)
        const historyBtn = await screen.findByTitle('Previously indexed folders')
        fireEvent.click(historyBtn)

        // Click "Clear All" inside dropdown
        const clearAllBtn = screen.getByText('Clear All')
        fireEvent.click(clearAllBtn)

        expect(global.confirm).toHaveBeenCalled()
        expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/api/folders/history')
    })

    it('closes when Escape key is pressed', () => {
        const onClose = vi.fn()
        render(<SettingsModal isOpen={true} onClose={onClose} onSave={vi.fn()} activeModel="" />)

        fireEvent.keyDown(window, { key: 'Escape' })
        expect(onClose).toHaveBeenCalled()
    })

    it('closes when clicking outside the modal', () => {
        const onClose = vi.fn()
        const { container } = render(<SettingsModal isOpen={true} onClose={onClose} onSave={vi.fn()} activeModel="" />)

        // The backdrop is the outermost div
        fireEvent.click(container.firstChild)
        expect(onClose).toHaveBeenCalled()
    })

    it('does not close when clicking inside the modal', () => {
        const onClose = vi.fn()
        render(<SettingsModal isOpen={true} onClose={onClose} onSave={vi.fn()} activeModel="" />)

        const modalContent = screen.getByText('Settings')
        fireEvent.click(modalContent)
        expect(onClose).not.toHaveBeenCalled()
    })

    it('has accessible labels', async () => {
        render(<SettingsModal isOpen={true} onClose={vi.fn()} onSave={vi.fn()} activeModel="" />)
        await waitFor(() => screen.getByText('Settings'))

        expect(screen.getByLabelText('Close settings')).toBeDefined()

        await waitFor(() => screen.getByText('C:/Users/test/Documents'))
        expect(screen.getByLabelText('Remove C:/Users/test/Documents from index')).toBeDefined()
    })
})
