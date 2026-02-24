class MockScheduler:
    def add_job(self, func, trigger, **kwargs):
        print(f"Scheduled job: {func.__name__} with trigger {trigger}")
    def shutdown(self):
        print("Scheduler shutting down")

def start_scheduler():
    """Returns a mock scheduler to satisfy main.py startup requirements"""
    print("Background scheduler placeholder started")
    return MockScheduler()
