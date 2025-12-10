import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { TaskList } from '../../components/TaskList';

// Mock API module
jest.mock('../../lib/api', () => ({
  api: {
    listTasks: jest.fn(),
  },
}));

const { api } = require('../../lib/api');

describe('TaskList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', async () => {
    // Mock API call to take some time
    api.listTasks.mockImplementation(() => new Promise(() => {})); // Never resolving promise for loading state

    render(<TaskList userId="test-user-id" tasks={[]} onToggleComplete={jest.fn()} onEdit={jest.fn()} onDelete={jest.fn()} loading={true} />);

    // Should show loading indicator
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  test('renders tasks when API call succeeds', async () => {
    const mockTasks = [
      {
        id: '1',
        user_id: 'test-user-id',
        title: 'Test Task 1',
        description: 'Test Description 1',
        completed: false,
        created_at: '2025-12-06T12:00:00Z',
        updated_at: '2025-12-06T12:00:00Z',
      },
      {
        id: '2',
        user_id: 'test-user-id',
        title: 'Test Task 2',
        description: 'Test Description 2',
        completed: true,
        created_at: '2025-12-06T12:05:00Z',
        updated_at: '2025-12-06T12:05:00Z',
      },
    ];

    api.listTasks.mockResolvedValue(mockTasks);

    render(<TaskList userId="test-user-id" tasks={mockTasks} onToggleComplete={jest.fn()} onEdit={jest.fn()} onDelete={jest.fn()} />);

    // Wait for tasks to be loaded and rendered
    await waitFor(() => {
      expect(screen.getByText('Test Task 1')).toBeInTheDocument();
      expect(screen.getByText('Test Task 2')).toBeInTheDocument();
    });
  });

  test('renders error state when API call fails', async () => {
    api.listTasks.mockRejectedValue(new Error('Failed to fetch tasks'));

    render(<TaskList userId="test-user-id" tasks={[]} onToggleComplete={jest.fn()} onEdit={jest.fn()} onDelete={jest.fn()} loading={false} />);

    // Wait for error state to be displayed
    await waitFor(() => {
      expect(screen.getByText(/No tasks yet/i)).toBeInTheDocument();
    });
  });
});