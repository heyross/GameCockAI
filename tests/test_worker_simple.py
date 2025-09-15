#!/usr/bin/env python3
"""
Simple test to verify the worker system is functioning.
"""

import time
from worker import add_task, get_task_status, start_worker, stop_worker

def simple_test_task(message, delay=1):
    """Simple test task that just sleeps and returns a message."""
    time.sleep(delay)
    return f"Task completed: {message}"

def test_worker():
    """Test the worker system with simple tasks."""
    print("🧪 Testing Worker System")
    print("=" * 40)
    
    # Start worker
    start_worker()
    time.sleep(1)
    
    # Add multiple tasks
    print("Adding 3 test tasks...")
    task_ids = []
    for i in range(3):
        task_id = add_task(simple_test_task, f"Test Task {i+1}", 1)
        task_ids.append(task_id)
        print(f"  Task {i+1} ID: {task_id}")
    
    # Monitor completion
    print("\nMonitoring task completion...")
    completed = 0
    for i in range(10):
        completed = 0
        for task_id in task_ids:
            status = get_task_status(task_id)
            if status['status'] == 'completed':
                completed += 1
            elif status['status'] == 'failed':
                print(f"  Task {task_id} failed: {status.get('error', 'Unknown error')}")
                completed += 1
        
        print(f"  Progress: {completed}/{len(task_ids)} tasks completed")
        if completed == len(task_ids):
            break
        time.sleep(1)
    
    # Show results
    print("\nTask Results:")
    for task_id in task_ids:
        status = get_task_status(task_id)
        if status['status'] == 'completed':
            print(f"  {task_id}: {status['result']}")
        else:
            print(f"  {task_id}: {status['status']}")
    
    print("\n✅ Worker test completed!")
    stop_worker()

if __name__ == "__main__":
    test_worker()
