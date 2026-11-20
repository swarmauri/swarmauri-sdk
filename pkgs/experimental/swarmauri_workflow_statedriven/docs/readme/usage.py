from swarmauri_workflow_statedriven.graph import WorkflowGraph

workflow = WorkflowGraph()
# Define nodes and transitions...
result = workflow.execute(start="start", initial_input={})
