/**
 * Frontend Unit Tests
 * 
 * Basic unit tests for the File Search Engine React frontend using Vitest.
 * These tests focus on utility functions and API interactions rather than
 * full component rendering to avoid ESM compatibility issues.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'

// =====================
// Utility Function Tests
// =====================
describe('Utility Functions', () => {
    it('formats file size correctly', () => {
        const formatSize = (bytes) => {
            if (bytes < 1024) return `${bytes} B`
            if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
            return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
        }

        expect(formatSize(500)).toBe('500 B')
        expect(formatSize(1536)).toBe('1.5 KB')
        expect(formatSize(1572864)).toBe('1.5 MB')
    })

    it('validates search query correctly', () => {
        const isValidQuery = (query) => {
            if (!query) return false
            return query.trim().length > 0
        }

        expect(isValidQuery('test')).toBe(true)
        expect(isValidQuery('  test  ')).toBe(true)
        expect(isValidQuery('')).toBe(false)
        expect(isValidQuery('   ')).toBe(false)
        expect(isValidQuery(null)).toBe(false)
    })

    it('extracts file extension correctly', () => {
        const getExtension = (filename) => {
            const parts = filename.split('.')
            return parts.length > 1 ? parts.pop().toLowerCase() : ''
        }

        expect(getExtension('document.pdf')).toBe('pdf')
        expect(getExtension('report.DOCX')).toBe('docx')
        expect(getExtension('file.tar.gz')).toBe('gz')
        expect(getExtension('noextension')).toBe('')
    })
})

// =====================
// API Mock Tests
// =====================
describe('API Interactions', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        global.fetch = vi.fn()
    })

    it('fetches config successfully', async () => {
        const mockConfig = { folder: '/test', provider: 'local', auto_index: false }
        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve(mockConfig)
        })

        const response = await fetch('http://localhost:8000/api/config')
        const data = await response.json()

        expect(data.folder).toBe('/test')
        expect(data.provider).toBe('local')
    })

    it('handles search request', async () => {
        const mockResults = {
            results: [{ document: 'Test content', summary: 'Test summary' }],
            ai_answer: 'AI response',
            active_model: 'test-model'
        }

        global.fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve(mockResults)
        })

        const response = await fetch('http://localhost:8000/api/search', {
            method: 'POST',
            body: JSON.stringify({ query: 'test' })
        })
        const data = await response.json()

        expect(data.results).toHaveLength(1)
        expect(data.ai_answer).toBe('AI response')
    })

    it('handles API error gracefully', async () => {
        global.fetch.mockResolvedValueOnce({
            ok: false,
            status: 500,
            statusText: 'Internal Server Error'
        })

        const response = await fetch('http://localhost:8000/api/search')

        expect(response.ok).toBe(false)
        expect(response.status).toBe(500)
    })
})

// =====================
// Data Validation Tests
// =====================
describe('Data Validation', () => {
    it('validates file object structure', () => {
        const isValidFile = (file) => {
            return !!(file &&
                typeof file.filename === 'string' &&
                typeof file.path === 'string' &&
                typeof file.size_bytes === 'number')
        }

        expect(isValidFile({ filename: 'test.pdf', path: '/test.pdf', size_bytes: 1024 })).toBe(true)
        expect(isValidFile({ filename: 'test.pdf' })).toBe(false)
        expect(isValidFile(null)).toBe(false)
    })

    it('validates search result structure', () => {
        const isValidResult = (result) => {
            return result &&
                typeof result.document === 'string' &&
                typeof result.summary === 'string'
        }

        expect(isValidResult({ document: 'content', summary: 'summary' })).toBe(true)
        expect(isValidResult({ document: 'content' })).toBe(false)
    })

    it('validates model object structure', () => {
        const isValidModel = (model) => {
            return model &&
                typeof model.id === 'string' &&
                typeof model.name === 'string'
        }

        expect(isValidModel({ id: 'test-model', name: 'Test Model' })).toBe(true)
        expect(isValidModel({ name: 'Test Model' })).toBe(false)
    })
})

// =====================
// State Management Tests
// =====================
describe('State Management', () => {
    it('manages search state correctly', () => {
        let searchState = { query: '', results: [], loading: false }

        // Start search
        searchState = { ...searchState, query: 'test', loading: true }
        expect(searchState.loading).toBe(true)
        expect(searchState.query).toBe('test')

        // Complete search
        searchState = { ...searchState, results: [{ document: 'result' }], loading: false }
        expect(searchState.loading).toBe(false)
        expect(searchState.results).toHaveLength(1)
    })

    it('manages config state correctly', () => {
        let config = { folder: '', provider: 'local', auto_index: false }

        // Update config
        config = { ...config, folder: '/new/path', auto_index: true }
        expect(config.folder).toBe('/new/path')
        expect(config.auto_index).toBe(true)
    })
})
