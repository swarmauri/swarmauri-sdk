from typing import get_args

from swarmauri_typing import Intersection, IntersectionMetadata


class Root:
    pass


class Left(Root):
    pass


class Right(Root):
    pass


Common = Intersection[Left, Right]
metadata = [
    item
    for item in get_args(Common)[1:]
    if isinstance(item, IntersectionMetadata)
]

assert metadata[0].classes == (Left, Right)
