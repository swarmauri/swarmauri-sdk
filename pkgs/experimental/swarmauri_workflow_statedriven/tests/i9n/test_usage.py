import pytest

pytest.skip("Requires full Swarmauri environment", allow_module_level=True)


@pytest.mark.i9n
def test_usage():
    # File: example_workflow.py

    from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
    from swarmauri_standard.llms.OpenAIModel import OpenAIModel
    from swarmauri.agents.RagAgent import RagAgent

    from swarmauri_workflow_statedriven.base import WorkflowBase
    from swarmauri_workflow_statedriven.input_modes.identity import IdentityInputMode
    from swarmauri_workflow_statedriven.input_modes.aggregate import AggregateInputMode
    from swarmauri_workflow_statedriven.join_strategies.first_join import (
        FirstJoinStrategy,
    )
    from swarmauri_workflow_statedriven.join_strategies.all_join import AllJoinStrategy
    from swarmauri_workflow_statedriven.merge_strategies.concat_merge import (
        ConcatMergeStrategy,
    )
    from swarmauri_workflow_statedriven.merge_strategies.list_merge import (
        ListMergeStrategy,
    )
    from swarmauri_workflow_statedriven.conditions.function_condition import (
        FunctionCondition,
    )
    from swarmauri_workflow_statedriven.conditions.regex_condition import RegexCondition

    # — your existing setup for LLM, vector store, prompts, and RagAgents —
    api_key = ""
    llm = OpenAIModel(api_key=api_key, name="gpt-4o")
    vector_store = TfidfVectorStore()
    # Define Role-Specific `RagAgent` Instances
    role_documents = {
        "Requirements Analyst": [
            "Requirements should be user-centric and measurable.",
            "User stories must include roles, actions, and outcomes.",
            "Functional requirements describe what the system should do.",
            "Non-functional requirements include performance and scalability.",
        ],
        "System Designer": [
            "System architecture includes client-server and microservices models.",
            "ER diagrams are essential for database design.",
            "UML diagrams help visualize system workflows.",
            "Scalability must be a core focus of the design process.",
        ],
        "Backend Developer": [
            "APIs should follow RESTful principles.",
            "Authentication can be implemented with OAuth2 or JWT.",
            "ORM simplifies database interactions with models.",
            "Write unit tests for every API endpoint.",
        ],
        "Frontend Developer": [
            "Frontend should be responsive across devices.",
            "Use state management tools like Redux or Vuex.",
            "Ensure smooth integration with backend APIs.",
            "Accessibility (WCAG) compliance is essential for a good UI.",
        ],
        "QA Engineer": [
            "Test cases should cover both functional and non-functional requirements.",
            "Integration tests validate interactions between system components.",
            "Use tools like Selenium for automated UI testing.",
            "Load testing ensures the system handles concurrent users.",
        ],
    }

    # Prompt templates to guide agents
    prompt_templates = {
        "Requirements Analyst": (
            "Summarize the collected requirements as bullet points. "
            "Conclude with a note to the System Designer on how these requirements "
            "should be interpreted for designing the system. "
        ),
        "System Designer": (
            "Use the requirements provided to create a system architecture. "
            "Provide a brief summary of the architecture and a note to the Backend Developer "
            "on how to implement it. "
        ),
        "Backend Developer": (
            "Implement backend APIs based on the provided architecture. "
            "Summarize the API endpoints and include a note for the Frontend Developer "
            "on how to integrate with the backend. "
        ),
        "Frontend Developer": (
            "Develop the frontend UI based on the provided API specifications. "
            "Summarize the UI components and include a note to the QA Engineer "
            "on how to test the application."
        ),
        "QA Engineer": (
            "Test the application based on the provided frontend and backend. "
            "Summarize the test cases and include a note to conclude the workflow."
        ),
    }

    rag_agents = {
        role: RagAgent(
            llm=llm, vector_store=vector_store, system_context=prompt_templates[role]
        )
        for role in role_documents
    }

    def build_workflow() -> WorkflowBase:
        wf = WorkflowBase()

        # 1) Gather requirements (scalar → string) via identity + concat
        wf.add_state(
            "GatherRequirements",
            agent=rag_agents["Requirements Analyst"],
            input_mode=IdentityInputMode(),
            join_strategy=FirstJoinStrategy(),  # fire on first arrival
            merge_strategy=ConcatMergeStrategy(),  # combine text into one string
        )

        # 2) Design system uses full context
        wf.add_state(
            "DesignSystem",
            agent=rag_agents["System Designer"],
            input_mode=AggregateInputMode(),  # see all prior outputs
            join_strategy=FirstJoinStrategy(),
            merge_strategy=ConcatMergeStrategy(),
        )

        # 3a) Implement backend (identity + list)
        wf.add_state(
            "ImplementBackend",
            agent=rag_agents["Backend Developer"],
            input_mode=AggregateInputMode(),
            join_strategy=FirstJoinStrategy(),
            merge_strategy=ListMergeStrategy(),  # return list of endpoints
        )

        # 3b) Implement frontend
        wf.add_state(
            "ImplementFrontend",
            agent=rag_agents["Frontend Developer"],
            input_mode=AggregateInputMode(),
            join_strategy=FirstJoinStrategy(),
            merge_strategy=ListMergeStrategy(),  # return list of components
        )

        # 4) QA waits for BOTH backend & frontend
        wf.add_state(
            "QA",
            agent=rag_agents["QA Engineer"],
            input_mode=AggregateInputMode(),  # sees both lists & context
            join_strategy=AllJoinStrategy(),  # wait for 2 branches
            merge_strategy=ListMergeStrategy(),  # flatten into one list
        )

        # 5) Finalize only if QA produced ≥2 test cases
        wf.add_state(
            "Finalize",
            agent=rag_agents["Requirements Analyst"],
            input_mode=AggregateInputMode(),
            join_strategy=FirstJoinStrategy(),
            merge_strategy=ConcatMergeStrategy(),
        )

        # Transitions with conditions
        wf.add_transition(
            "GatherRequirements",
            "DesignSystem",
            RegexCondition(node_name="GatherRequirements", pattern=r"system"),
        )
        wf.add_transition(
            "DesignSystem", "ImplementBackend", FunctionCondition(lambda state: True)
        )
        wf.add_transition(
            "DesignSystem", "ImplementFrontend", FunctionCondition(lambda state: True)
        )
        wf.add_transition(
            "ImplementBackend", "QA", FunctionCondition(lambda state: True)
        )
        wf.add_transition(
            "ImplementFrontend", "QA", FunctionCondition(lambda state: True)
        )
        wf.add_transition(
            "QA", "Finalize", RegexCondition(node_name="QA", pattern=r"Test Case")
        )
        return wf

        # Sample initial input: free‑form requirement text
        initial_input = (
            "We need a system that supports mobile and web, "
            "with strong security and real‑time analytics."
        )

        workflow = build_workflow()
        results = workflow.run("GatherRequirements", initial_input)

        for state, output in results.items():
            print(f"{state} → {output}\n")

        assert results
