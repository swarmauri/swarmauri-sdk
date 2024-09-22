from typing import Dict

import sqlite3
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class SQLite3QueryTool(ToolBase):
    def __init__(self, db_name: str):
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="SQL query to execute",
                required=True,
            )
        ]
        super().__init__(
            name="SQLQueryTool",
            description="Executes an SQL query and returns the results.",
            parameters=parameters,
        )
        self.db_name = db_name

    def __call__(self, query) -> Dict[str, str]:
        """
        Execute the provided SQL query.

        Parameters:
        - query (str): The SQL query to execute.

        Returns:
        - Dict[str, str]: A dictionary containing the result of the query.
        """
        try:
            connection = sqlite3.connect(
                self.db_name
            )  # Connect to the specific database file
            cursor = connection.cursor()

            cursor.execute(query)
            rows = cursor.fetchall()
            result = "\n".join(str(row) for row in rows)
        except Exception as e:
            result = f"Error executing query: {e}"
        finally:
            connection.close()

        return {"query_result": result}
