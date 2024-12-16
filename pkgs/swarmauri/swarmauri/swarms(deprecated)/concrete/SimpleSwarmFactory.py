import json
import pickle
from typing import List
from swarmauri_core.chains.ISwarmFactory import (
    ISwarmFactory , 
    CallableChainItem, 
    AgentDefinition, 
    FunctionDefinition
)
class SimpleSwarmFactory(ISwarmFactory):
    def __init__(self):
        self.swarms = []
        self.callable_chains = []

    def create_swarm(self, agents=[]):
        swarm = {"agents": agents}
        self.swarms.append(swarm)
        return swarm

    def create_agent(self, agent_definition: AgentDefinition):
        # For simplicity, agents are stored in a list
        # Real-world usage might involve more sophisticated management and instantiation based on type and configuration
        agent = {"definition": agent_definition._asdict()}
        self.agents.append(agent)
        return agent

    def create_callable_chain(self, chain_definition: List[CallableChainItem]):
        chain = {"definition": [item._asdict() for item in chain_definition]}
        self.callable_chains.append(chain)
        return chain

    def register_function(self, function_definition: FunctionDefinition):
        if function_definition.identifier in self.functions:
            raise ValueError(f"Function {function_definition.identifier} is already registered.")
        
        self.functions[function_definition.identifier] = function_definition
    
    def export_configuration(self, format_type: str = 'json'):
        # Now exporting both swarms and callable chains
        config = {"swarms": self.swarms, "callable_chains": self.callable_chains}
        if format_type == "json":
            return json.dumps(config)
        elif format_type == "pickle":
            return pickle.dumps(config)

    def load_configuration(self, config_data, format_type: str = 'json'):
        # Loading both swarms and callable chains
        config = json.loads(config_data) if format_type == "json" else pickle.loads(config_data)
        self.swarms = config.get("swarms", [])
        self.callable_chains = config.get("callable_chains", [])