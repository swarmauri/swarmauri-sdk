# peagen/gateway/hooks/__init__.py

from .keys import (
    pre_key_upload,
    post_key_upload,
    post_key_fetch,
    pre_key_delete,
    post_key_delete,
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

from .works import (
    post_work_update,
)

__all__ = [
    "pre_key_upload",
    "post_key_upload",
    "post_key_fetch",
    "pre_key_delete",
    "post_key_delete",
    "post_secret_add",
    "post_secret_delete",
    "pre_task_create",
    "post_task_create",
    "pre_task_update",
    "post_task_update",
    "pre_task_read",
    "post_task_read",
    "post_work_update",
]
