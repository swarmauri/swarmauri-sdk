"""ORM table exports for the cron API."""

from .cron_job import CronJob
from .cron_job_result import CronJobResult

__all__ = ["CronJob", "CronJobResult"]
