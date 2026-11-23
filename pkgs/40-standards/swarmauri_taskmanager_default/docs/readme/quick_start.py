from swarmauri_taskmanager_default import DefaultTaskManager


def configure_task_admission(
    *, controller, expires_at, permissions, subject, task_store, tenant
):
    """Bind caller-owned resources before executing this integration."""
    manager = DefaultTaskManager(store=task_store, executions=controller)
    # subject and permissions have already been admitted by host policy.
    task = manager.start(subject, tenant, permissions, expires_at)
    manager.pause(task.task_id)
    manager.resume(task.task_id)
    manager.stop(task.task_id)
