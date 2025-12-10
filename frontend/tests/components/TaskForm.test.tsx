import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { TaskForm } from '../../components/TaskForm';

// Mock API module
jest.mock('../../lib/api', () => ({
  api: {
    createTask: jest.fn(),
    updateTask: jest.fn(),
  },
}));

const { api } = require('../../lib/api');

describe('TaskForm Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    api.createTask.mockResolvedValueOnce(undefined); // Reset createTask mock
  });

  test('renders form elements', async () => {
    await userEvent.setup();
    await act(async () => {
      render(<TaskForm userId="test-user-id" onTaskUpdated={jest.fn()} onSubmit={jest.fn()} />);
    });

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument();
  });

  test('validates required title field', async () => {
    await userEvent.setup();
    const mockOnSubmit = jest.fn(async () => {}); // Simulate a successful onSubmit

    const { container } = render(
      <TaskForm userId="test-user-id" onTaskUpdated={jest.fn()} onSubmit={mockOnSubmit} />
    );

    const titleInput = screen.getByLabelText(/title/i) as HTMLInputElement;
    const descriptionInput = screen.getByLabelText(/description/i);
    const form = container.querySelector('form') as HTMLFormElement;

    // Ensure title is empty
    await userEvent.clear(titleInput);
    await userEvent.type(descriptionInput, 'Test description');

    // Submit form programmatically (bypasses HTML5 validation)
    await act(async () => {
      fireEvent.submit(form);
    });

    await waitFor(() => {
      expect(screen.getByText(/title is required/i)).toBeInTheDocument();
      expect(mockOnSubmit).not.toHaveBeenCalled(); // onSubmit should not be called due to validation
    });
  });

  test('submits task when valid data is provided', async () => {
    await userEvent.setup();
    const mockOnTaskUpdated = jest.fn();
    const mockTask = {
      id: 'test-id',
      user_id: 'test-user-id',
      title: 'Test Task',
      description: 'Test Description',
      completed: false,
      created_at: '2025-12-06T12:00:00Z',
      updated_at: '2025-12-06T12:00:00Z',
    };

    api.createTask.mockResolvedValue(mockTask);
    const mockSubmit = jest.fn(async (data) => {
      return api.createTask('test-user-id', data);
    });

    let component;
    await act(async () => {
      component = render(<TaskForm userId="test-user-id" onTaskUpdated={mockOnTaskUpdated} onSubmit={mockSubmit} />);
    });

    const titleInput = screen.getByLabelText(/title/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    await act(async () => {
      await userEvent.type(titleInput, 'Test Task');
      await userEvent.type(descriptionInput, 'Test Description');
      await userEvent.click(submitButton);
    });
  });

  test('shows error message when task creation fails', async () => {
    await userEvent.setup();
    api.createTask.mockRejectedValue(new Error('Failed to create task'));
    const mockSubmit = jest.fn(async (data) => {
      return Promise.reject(new Error('Failed to create task'));
    });

    let component;
    await act(async () => {
      component = render(<TaskForm userId="test-user-id" onTaskUpdated={jest.fn()} onSubmit={mockSubmit} />);
    });

    const titleInput = screen.getByLabelText(/title/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const submitButton = screen.getByRole('button', { name: /add task/i });

    await act(async () => {
      await userEvent.type(titleInput, 'Test Task');
      await userEvent.type(descriptionInput, 'Test Description');
      await userEvent.click(submitButton);
    });

    await waitFor(() => {
      expect(screen.getByText(/failed to create task/i)).toBeInTheDocument();
    });
  });
});