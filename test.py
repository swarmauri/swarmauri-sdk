from typing import List


class Solution:
    def maxScore(self, nums: List[int], weights: List[int], r: int, p: int) -> int:
        # 1. Invalid inputs
        n = len(nums)
        if n != len(weights) or r < 0 or p < 0:
            return -1

        # 2. Collect all positive weights
        pos = [w for w in weights if w > 0]
        if not pos:
            return 0  # no positive gain possible

        # 3. Sum of single uses
        sum1 = sum(pos)

        # 4. We can double-count at most r of them
        reuse_count = min(r, len(pos))
        # pick the largest 'reuse_count' weights to reuse
        pos.sort(reverse=True)
        sum2 = sum(pos[:reuse_count])

        # 5. Total maximum score
        return sum1 + sum2
