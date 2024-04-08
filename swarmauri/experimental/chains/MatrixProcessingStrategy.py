import asyncio
from typing import List, Any
from swarmauri.core.chains.IChainProcessingStrategy import IChainProcessingStrategy
from swarmauri.core.chains.IChainStep import IChainStep

class MatrixProcessingStrategy(IChainProcessingStrategy):
    async def execute_steps(self, steps: List[IChainStep]) -> Any:
        # Launch tasks asynchronously, maintaining the matrix structure
        results = await self.execute_matrix(steps)
        return results

    async def execute_matrix(self, matrix):
        matrix_results = []

        # Example: Execute tasks row by row, waiting for each row to complete before moving on.
        for row in matrix:
            row_results = await asyncio.gather(*[step.method(*step.args, **step.kwargs) for step in row])
            matrix_results.append(row_results)
            # Optionally, add a call to a row callback here

        # After processing all rows, you may call a final matrix callback
        # This could be a place for final aggregation or analysis of all results
        return matrix_results