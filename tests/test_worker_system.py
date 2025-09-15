"""
Comprehensive pytest tests for the worker system.
Tests task creation, execution, status tracking, and error handling.
"""

import unittest
import time
import threading
from unittest.mock import patch, MagicMock
import sys
import os

# Add GameCockAI directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
gamecock_dir = os.path.dirname(current_dir)
if gamecock_dir not in sys.path:
    sys.path.insert(0, gamecock_dir)

from worker import (
    Task, task_queue, task_store, _stop_event,
    worker, start_worker, stop_worker, add_task, get_task_status, is_worker_running,
    STATUS_PENDING, STATUS_RUNNING, STATUS_COMPLETED, STATUS_FAILED
)

class TestWorkerSystem(unittest.TestCase):
    """Test the worker system functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Stop any existing worker first
        stop_worker()
        
        # Clear any existing tasks
        while not task_queue.empty():
            try:
                task_queue.get_nowait()
            except:
                break
        
        # Clear task store
        task_store.clear()
        
        # Reset stop event
        _stop_event.clear()

    def tearDown(self):
        """Clean up after each test."""
        # Stop worker if running
        stop_worker()
        
        # Verify worker is actually stopped
        if is_worker_running():
            print(f"[Test] Warning: Worker still running after stop_worker()")
            # Force stop by setting stop event again
            _stop_event.set()
        time.sleep(0.1)  # Give worker time to stop
        
        # Clear tasks
        while not task_queue.empty():
            try:
                task_queue.get_nowait()
            except:
                break
        task_store.clear()

    def test_task_creation(self):
        """Test creating a new task."""
        def test_func(x, y):
            return x + y
        
        task = Task(test_func, 5, 10)
        
        self.assertIsNotNone(task.id)
        self.assertEqual(task.status, STATUS_PENDING)
        self.assertEqual(task.func, test_func)
        self.assertEqual(task.args, (5, 10))
        self.assertIsNone(task.result)
        self.assertIsNone(task.error)

    def test_add_task_to_queue(self):
        """Test adding a task to the queue."""
        def test_func():
            return "test result"
        
        task_id = add_task(test_func)
        
        self.assertIsNotNone(task_id)
        self.assertIn(task_id, task_store)
        self.assertEqual(task_store[task_id].status, STATUS_PENDING)
        self.assertEqual(task_queue.qsize(), 1)

    def test_get_task_status_pending(self):
        """Test getting status of a pending task."""
        def test_func():
            time.sleep(0.1)  # Add small delay to ensure we can catch pending status
            return "test result"
        
        # Don't start worker yet
        task_id = add_task(test_func)
        status = get_task_status(task_id)
        
        self.assertEqual(status['task_id'], task_id)
        self.assertEqual(status['status'], STATUS_PENDING)
        self.assertNotIn('result', status)
        self.assertNotIn('error', status)

    def test_get_task_status_nonexistent(self):
        """Test getting status of a non-existent task."""
        status = get_task_status("nonexistent-id")
        
        self.assertIn('error', status)
        self.assertEqual(status['error'], 'Task not found.')

    def test_worker_execution_success(self):
        """Test successful task execution by worker."""
        def test_func(x, y):
            return x + y
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Add task
        task_id = add_task(test_func, 3, 7)
        
        # Wait for task to complete
        max_wait = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = get_task_status(task_id)
            if status['status'] == STATUS_COMPLETED:
                break
            time.sleep(0.1)
        
        # Verify completion
        status = get_task_status(task_id)
        self.assertEqual(status['status'], STATUS_COMPLETED)
        self.assertEqual(status['result'], 10)

    def test_worker_execution_failure(self):
        """Test task execution failure handling."""
        def failing_func():
            raise ValueError("Test error")
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Add failing task
        task_id = add_task(failing_func)
        
        # Wait for task to fail
        max_wait = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = get_task_status(task_id)
            if status['status'] == STATUS_FAILED:
                break
            time.sleep(0.1)
        
        # Verify failure
        status = get_task_status(task_id)
        self.assertEqual(status['status'], STATUS_FAILED)
        self.assertIn('error', status)
        self.assertIn('Test error', status['error'])

    def test_multiple_tasks_execution(self):
        """Test execution of multiple tasks."""
        def test_func(delay, result):
            time.sleep(delay)
            return result
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Add multiple tasks
        task_ids = []
        for i in range(3):
            task_id = add_task(test_func, 0.1, f"result_{i}")
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        max_wait = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            completed = 0
            for task_id in task_ids:
                status = get_task_status(task_id)
                if status['status'] == STATUS_COMPLETED:
                    completed += 1
            if completed == len(task_ids):
                break
            time.sleep(0.1)
        
        # Verify all tasks completed
        for i, task_id in enumerate(task_ids):
            status = get_task_status(task_id)
            self.assertEqual(status['status'], STATUS_COMPLETED)
            self.assertEqual(status['result'], f"result_{i}")

    def test_worker_stop_functionality(self):
        """Test stopping the worker."""
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Stop worker
        stop_worker()
        time.sleep(0.1)  # Give worker time to stop
        
        # Verify stop event is set
        self.assertTrue(_stop_event.is_set())

    def test_task_with_kwargs(self):
        """Test task execution with keyword arguments."""
        def test_func(x, y, multiplier=1):
            return (x + y) * multiplier
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Add task with kwargs
        task_id = add_task(test_func, 2, 3, multiplier=4)
        
        # Wait for task to complete
        max_wait = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = get_task_status(task_id)
            if status['status'] == STATUS_COMPLETED:
                break
            time.sleep(0.1)
        
        # Verify completion
        status = get_task_status(task_id)
        self.assertEqual(status['status'], STATUS_COMPLETED)
        self.assertEqual(status['result'], 20)  # (2 + 3) * 4

    def test_concurrent_task_creation(self):
        """Test creating tasks from multiple threads."""
        def test_func(thread_id, task_num):
            return f"thread_{thread_id}_task_{task_num}"
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Create tasks from multiple threads
        task_ids = []
        threads = []
        
        def create_tasks(thread_id):
            for i in range(3):
                task_id = add_task(test_func, thread_id, i)
                task_ids.append(task_id)
        
        # Start multiple threads
        for i in range(3):
            thread = threading.Thread(target=create_tasks, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all tasks were created
        self.assertEqual(len(task_ids), 9)  # 3 threads * 3 tasks each
        
        # Wait for all tasks to complete
        max_wait = 10  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            completed = 0
            for task_id in task_ids:
                status = get_task_status(task_id)
                if status['status'] == STATUS_COMPLETED:
                    completed += 1
            if completed == len(task_ids):
                break
            time.sleep(0.1)
        
        # Verify all tasks completed successfully
        self.assertEqual(completed, len(task_ids))

    def test_task_status_transitions(self):
        """Test that task status transitions correctly."""
        def slow_func():
            time.sleep(0.5)
            return "done"
        
        # Add task first (before starting worker)
        task_id = add_task(slow_func)
        
        # Check initial status (should be pending)
        status = get_task_status(task_id)
        self.assertEqual(status['status'], STATUS_PENDING)
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Wait a bit and check if it's running
        time.sleep(0.2)
        status = get_task_status(task_id)
        # Status could be pending (not started yet) or running
        self.assertIn(status['status'], [STATUS_PENDING, STATUS_RUNNING])
        
        # Wait for completion
        max_wait = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = get_task_status(task_id)
            if status['status'] == STATUS_COMPLETED:
                break
            time.sleep(0.1)
        
        # Verify final status
        status = get_task_status(task_id)
        self.assertEqual(status['status'], STATUS_COMPLETED)
        self.assertEqual(status['result'], "done")

    def test_empty_queue_handling(self):
        """Test worker behavior with empty queue."""
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Worker should handle empty queue gracefully
        # (This is tested implicitly by the worker not crashing)
        time.sleep(0.5)
        
        # Stop worker
        stop_worker()
        time.sleep(0.1)
        
        # Test passes if no exceptions were raised

    def test_task_store_cleanup(self):
        """Test that completed tasks remain in task store."""
        def test_func():
            return "test result"
        
        # Start worker
        start_worker()
        time.sleep(0.1)  # Give worker time to start
        
        # Add task
        task_id = add_task(test_func)
        
        # Wait for completion
        max_wait = 5  # seconds
        start_time = time.time()
        while time.time() - start_time < max_wait:
            status = get_task_status(task_id)
            if status['status'] == STATUS_COMPLETED:
                break
            time.sleep(0.1)
        
        # Verify task is still in store
        self.assertIn(task_id, task_store)
        self.assertEqual(task_store[task_id].status, STATUS_COMPLETED)
        self.assertEqual(task_store[task_id].result, "test result")

if __name__ == '__main__':
    unittest.main()
