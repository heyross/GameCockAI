import uuid
import threading
from queue import Queue, Empty

# --- Task Statuses ---
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

class Task:
    """Represents a job for the worker to execute."""
    def __init__(self, func, *args, **kwargs):
        self.id = str(uuid.uuid4())
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.status = STATUS_PENDING
        self.result = None
        self.error = None

# --- Global Task Management ---
task_queue = Queue()
task_store = {}
_stop_event = threading.Event()

def worker():
    """The worker thread function that processes tasks from the queue."""
    while not _stop_event.is_set():
        try:
            task = task_queue.get(timeout=1)  # Wait for 1 second
            task.status = STATUS_RUNNING
            task_store[task.id] = task
            print(f"[Worker] Starting task {task.id}...")
            
            try:
                result = task.func(*task.args, **kwargs)
                task.result = result
                task.status = STATUS_COMPLETED
                print(f"[Worker] Task {task.id} completed successfully.")
            except Exception as e:
                task.error = str(e)
                task.status = STATUS_FAILED
                print(f"[Worker] Task {task.id} failed: {e}")

            task_store[task.id] = task
            task_queue.task_done()

        except Empty:
            # Queue is empty, continue waiting
            continue

def start_worker():
    """Starts the background worker thread."""
    print("[WorkerManager] Starting worker thread...")
    threading.Thread(target=worker, daemon=True).start()

def stop_worker():
    """Stops the background worker thread."""
    print("[WorkerManager] Stopping worker thread...")
    _stop_event.set()

def add_task(func, *args, **kwargs):
    """Adds a new task to the queue and returns its ID."""
    task = Task(func, *args, **kwargs)
    task_store[task.id] = task
    task_queue.put(task)
    print(f"[WorkerManager] Task {task.id} added to the queue.")
    return task.id

def get_task_status(task_id: str):
    """Retrieves the status and result of a specific task."""
    task = task_store.get(task_id)
    if not task:
        return {"error": "Task not found."}
    
    status_info = {
        "task_id": task.id,
        "status": task.status,
    }
    if task.status == STATUS_COMPLETED:
        status_info["result"] = task.result
    elif task.status == STATUS_FAILED:
        status_info["error"] = task.error
        
    return status_info
