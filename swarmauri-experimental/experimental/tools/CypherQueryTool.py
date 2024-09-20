import json
from neo4j import GraphDatabase
from typing import Dict
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class CypherQueryTool(ToolBase):
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password

        # Define only the 'query' parameter since uri, user, and password are set at initialization
        parameters = [
            Parameter(
                name="query",
                type="string",
                description="The Cypher query to execute.",
                required=True,
            )
        ]

        super().__init__(
            name="CypherQueryTool",
            description="Executes a Cypher query against a Neo4j database.",
            parameters=parameters,
        )

    def _get_connection(self):
        return GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def __call__(self, query) -> Dict[str, str]:
        # Establish connection to the database
        driver = self._get_connection()
        session = driver.session()

        # Execute the query
        result = session.run(query)
        records = result.data()

        # Close the connection
        session.close()
        driver.close()

        # Convert records to JSON string, assuming it's JSON serializable
        return {"records_data": json.dumps(records)}
