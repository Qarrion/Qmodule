import logging, asyncio

# Define ANSI escape codes for colors
TASK_COLORS = {
    "task1": "\033[91m",  # Red
    "task2": "\033[92m",  # Green
    "task3": "\033[94m",  # Blue
    "reset": "\033[0m"    # Reset to default
}

class TaskColorFormatter(logging.Formatter):
    def format(self, record):
        # Get the task name from the log record, default to 'default'
        task_name = getattr(record, 'task_name', 'default')
        
        # Get the color for the task name, default to no color
        color = TASK_COLORS.get(task_name, TASK_COLORS["reset"])
        
        # Apply the color to the log message
        record.msg = f"{color}{record.msg}{TASK_COLORS['reset']}"
        
        # Call the original formatter to handle the rest of the formatting
        return super().format(record)

# Setup logging
logger = logging.getLogger("asyncio_tasks")
handler = logging.StreamHandler()
formatter = TaskColorFormatter('%(asctime)s - %(task_name)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Custom log method to include task name
def log_task_message(task_name, message):
    logger.info(message, extra={"task_name": task_name})

async def task(name, duration):
    for i in range(5):
        log_task_message(name, f"Running iteration {i + 1}")
        await asyncio.sleep(duration)
    log_task_message(name, "Completed")

async def main():
    await asyncio.gather(
        task("task1", 1),
        task("task2", 1.5),
        task("task3", 2),
    )

if __name__ == "__main__":
    asyncio.run(main())