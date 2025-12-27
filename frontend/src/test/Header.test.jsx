import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import Header from '../components/Header';

describe('Header Component', () => {
    const defaultProps = {
        darkMode: true,
        toggleDarkMode: vi.fn(),
        openSettings: vi.fn(),
        activeModel: null,
        availableModels: [],
        onModelChange: vi.fn()
    };

    it('renders the File Search brand', () => {
        render(<Header {...defaultProps} />);
        expect(screen.getByText('File Search')).toBeDefined();
    });

    it('renders settings and theme toggle buttons', () => {
        render(<Header {...defaultProps} />);
        expect(screen.getByLabelText('Settings')).toBeDefined();
        expect(screen.getByLabelText('Toggle theme')).toBeDefined();
    });

    it('does NOT show model selector when activeModel is null', () => {
        render(<Header {...defaultProps} activeModel={null} />);
        expect(screen.queryByText(/Default Embeddings/i)).toBeNull();
    });

    it('shows model selector when activeModel is set', () => {
        render(<Header {...defaultProps} activeModel="Test Model" />);
        expect(screen.getByText('Test Model')).toBeDefined();
    });

    it('opens model dropdown when clicked', () => {
        render(<Header {...defaultProps} activeModel="Test Model" availableModels={[{ name: 'model1.gguf' }, { name: 'model2.gguf' }]} />);

        const modelButton = screen.getByText('Test Model');
        fireEvent.click(modelButton);

        expect(screen.getByText('model1')).toBeDefined();
        expect(screen.getByText('model2')).toBeDefined();
    });

    it('calls onModelChange when a model is selected', () => {
        const onModelChange = vi.fn();
        render(<Header {...defaultProps} activeModel="Test Model" availableModels={[{ name: 'newmodel.gguf' }]} onModelChange={onModelChange} />);

        fireEvent.click(screen.getByText('Test Model'));
        fireEvent.click(screen.getByText('newmodel'));

        expect(onModelChange).toHaveBeenCalledWith('newmodel');
    });

    it('shows "No local models found" when availableModels is empty', () => {
        render(<Header {...defaultProps} activeModel="Default" availableModels={[]} />);

        fireEvent.click(screen.getByText('Default'));

        expect(screen.getByText('No local models found')).toBeDefined();
    });

    it('toggles dark mode when theme button is clicked', () => {
        const toggleDarkMode = vi.fn();
        render(<Header {...defaultProps} toggleDarkMode={toggleDarkMode} />);

        fireEvent.click(screen.getByLabelText('Toggle theme'));

        expect(toggleDarkMode).toHaveBeenCalled();
    });

    it('opens settings when settings button is clicked', () => {
        const openSettings = vi.fn();
        render(<Header {...defaultProps} openSettings={openSettings} />);

        fireEvent.click(screen.getByLabelText('Settings'));

        expect(openSettings).toHaveBeenCalled();
    });
});
