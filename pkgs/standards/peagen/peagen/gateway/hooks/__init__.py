# peagen/gateway/hooks/__init__.py

from .keys import (
    pre_key_upload,
    post_key_upload,
    post_key_fetch,
    pre_key_delete,
    post_key_delete,
)

from .pools import (
    pre_pool_create, 
    post_pool_create,
)

from .secrets import (
    post_secret_add,
    post_secret_delete,
)

from .tasks import (
    pre_task_create,
    post_task_create,
    pre_task_update,
    post_task_update,
    pre_task_read,
    post_task_read,
)

from .workers import (
    pre_worker_create,
    post_worker_create,
    pre_worker_update,
    post_worker_update,
    post_workers_list,
)

from .works import (
    post_work_update,
)

__all__ = [
    "pre_key_upload",
    "post_key_upload",
    "post_key_fetch",
    "pre_key_delete",
    "post_key_delete",
    "pre_pool_create", 
    "post_pool_create",
    "post_secret_add",
    "post_secret_delete",
    "pre_task_create",
    "post_task_create",
    "pre_task_update",
    "post_task_update",
    "pre_task_read",
    "post_task_read",
    "pre_worker_create",
    "post_worker_create",
    "pre_worker_update",
    "post_worker_update",
    "post_workers_list",
    "post_work_update",
]