import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from './App';

// Mock the axios module to prevent real API calls during UI testing
vi.mock('axios', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({ 
      data: { 
        answer: "Mock AI Response", 
        context: [] 
      } 
    }))
  }
}));

describe('Axiom Dashboard UI', () => {
  
  it('renders the main header correctly', () => {
    render(<App />);
    expect(screen.getByText('Axiom')).toBeInTheDocument();
    expect(screen.getByText(/Knowledge Governance/i)).toBeInTheDocument();
  });

  it('displays the Data Governance (Upload) panel', () => {
    render(<App />);
    expect(screen.getByText(/Data Governance/i)).toBeInTheDocument();
    expect(screen.getByText(/Drop PDF here/i)).toBeInTheDocument();
  });

  it('renders the Chat interface', () => {
    render(<App />);
    // Check for the empty state message
    expect(screen.getByText('Axiom RAG Assistant')).toBeInTheDocument();
    // Check for input field
    expect(screen.getByPlaceholderText(/Ask specific questions/i)).toBeInTheDocument();
  });

  it('allows user to type in chat box', () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Ask specific questions/i) as HTMLInputElement;
    
    fireEvent.change(input, { target: { value: 'Hello Axiom' } });
    expect(input.value).toBe('Hello Axiom');
  });
});