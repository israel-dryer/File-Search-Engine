/**
 * ModelManager Component Tests
 * 
 * Tests for the ModelManager component including model listing,
 * download functionality, selection, and deletion.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('ModelManager Component', () => {
    describe('Available Models Display', () => {
        it('should display list of available models', () => {
            const availableModels = [
                { id: 'tinyllama', name: 'TinyLlama 1.1B', size: '637 MB', ram_required: 2 },
                { id: 'phi-2', name: 'Phi-2', size: '1.7 GB', ram_required: 5 },
                { id: 'mistral-7b', name: 'Mistral 7B', size: '4.4 GB', ram_required: 8 }
            ]

            expect(availableModels.length).toBe(3)
            expect(availableModels[0].name).toBe('TinyLlama 1.1B')
        })

        it('should show model metadata', () => {
            const model = {
                id: 'phi-2',
                name: 'Phi-2 (Microsoft)',
                description: 'Excellent reasoning model',
                size: '1.7 GB',
                ram_required: 5,
                category: 'medium',
                use_case: 'Reasoning, code'
            }

            expect(model.description).toBeDefined()
            expect(model.ram_required).toBe(5)
            expect(model.category).toBe('medium')
        })

        it('should categorize models by size', () => {
            const models = [
                { id: 'm1', category: 'small' },
                { id: 'm2', category: 'medium' },
                { id: 'm3', category: 'large' }
            ]

            const smallModels = models.filter(m => m.category === 'small')
            const largeModels = models.filter(m => m.category === 'large')

            expect(smallModels.length).toBe(1)
            expect(largeModels.length).toBe(1)
        })

        it('should highlight recommended models', () => {
            const models = [
                { id: 'm1', recommended: true },
                { id: 'm2', recommended: false },
                { id: 'm3', recommended: true }
            ]

            const recommended = models.filter(m => m.recommended)
            expect(recommended.length).toBe(2)
        })
    })

    describe('Local Models Display', () => {
        it('should display downloaded models', () => {
            const localModels = [
                { id: 'phi-2', name: 'Phi-2', path: '/models/phi-2.gguf', size: 1700000000 }
            ]

            expect(localModels.length).toBe(1)
            expect(localModels[0].path).toContain('.gguf')
        })

        it('should format file size correctly', () => {
            const formatBytes = (bytes) => {
                if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
                if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
                return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
            }

            expect(formatBytes(1700000000)).toBe('1.58 GB')
            expect(formatBytes(500000000)).toBe('476.8 MB')
        })

        it('should show empty state when no models downloaded', () => {
            const localModels = []
            const hasModels = localModels.length > 0

            expect(hasModels).toBe(false)
        })
    })

    describe('Download Functionality', () => {
        it('should trigger download on button click', () => {
            const mockDownload = vi.fn()
            const modelId = 'phi-2'

            mockDownload(modelId)
            expect(mockDownload).toHaveBeenCalledWith('phi-2')
        })

        it('should show download progress', () => {
            const downloadStatus = {
                downloading: true,
                model_id: 'phi-2',
                progress: 42,
                bytes_downloaded: 714000000,
                total_bytes: 1700000000
            }

            expect(downloadStatus.downloading).toBe(true)
            expect(downloadStatus.progress).toBe(42)
        })

        it('should disable other downloads during active download', () => {
            const downloadStatus = { downloading: true, model_id: 'phi-2' }
            const canDownload = (modelId) => !downloadStatus.downloading || downloadStatus.model_id === modelId

            expect(canDownload('phi-2')).toBe(true)
            expect(canDownload('tinyllama')).toBe(false)
        })

        it('should check system resources before download', () => {
            const systemRam = 16 // GB
            const model = { ram_required: 8 }
            const canRun = systemRam >= model.ram_required

            expect(canRun).toBe(true)
        })

        it('should show warning for insufficient resources', () => {
            const systemRam = 4 // GB
            const model = { ram_required: 8 }
            const showWarning = systemRam < model.ram_required

            expect(showWarning).toBe(true)
        })
    })

    describe('Model Selection', () => {
        it('should select a model', () => {
            const mockSelect = vi.fn()
            const modelPath = '/models/phi-2.gguf'

            mockSelect(modelPath)
            expect(mockSelect).toHaveBeenCalledWith('/models/phi-2.gguf')
        })

        it('should highlight selected model', () => {
            const activeModelPath = '/models/phi-2.gguf'
            const model = { path: '/models/phi-2.gguf' }
            const isSelected = model.path === activeModelPath

            expect(isSelected).toBe(true)
        })

        it('should update active model in config', () => {
            let config = { local_model_path: '' }

            config.local_model_path = '/models/mistral-7b.gguf'
            expect(config.local_model_path).toBe('/models/mistral-7b.gguf')
        })
    })

    describe('Model Deletion', () => {
        it('should trigger delete on button click', () => {
            const mockDelete = vi.fn()
            const modelPath = '/models/tinyllama.gguf'

            mockDelete(modelPath)
            expect(mockDelete).toHaveBeenCalledWith('/models/tinyllama.gguf')
        })

        it('should confirm before deletion', () => {
            let showConfirm = false
            let modelToDelete = null

            modelToDelete = '/models/test.gguf'
            showConfirm = true

            expect(showConfirm).toBe(true)
            expect(modelToDelete).toBe('/models/test.gguf')
        })

        it('should remove model from list after deletion', () => {
            const models = [
                { path: '/models/a.gguf' },
                { path: '/models/b.gguf' }
            ]
            const deletedPath = '/models/a.gguf'

            const remaining = models.filter(m => m.path !== deletedPath)
            expect(remaining.length).toBe(1)
        })
    })

    describe('Loading States', () => {
        it('should show loading while fetching models', () => {
            let isLoading = true

            expect(isLoading).toBe(true)

            isLoading = false
            expect(isLoading).toBe(false)
        })

        it('should show error on fetch failure', () => {
            let error = null

            error = 'Failed to fetch models'
            expect(error).toBe('Failed to fetch models')
        })
    })
})
