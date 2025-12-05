import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import StatCard from './StatCard.svelte';

describe('StatCard', () => {
    it('renders title and value', () => {
        render(StatCard, { title: 'Test Title', value: '123' });
        expect(screen.getByText('Test Title')).toBeTruthy();
        expect(screen.getByText('123')).toBeTruthy();
    });

    it('renders subtitle when provided', () => {
        render(StatCard, { title: 'Test', value: '123', subtitle: 'Test Subtitle' });
        expect(screen.getByText('Test Subtitle')).toBeTruthy();
    });
});
