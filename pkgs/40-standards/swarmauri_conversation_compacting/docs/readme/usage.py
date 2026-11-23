from swarmauri_conversation_compacting import CompactingConversation
from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.HumanMessage import HumanMessage

conversation = CompactingConversation(keep_recent_turns=1)
conversation.add_messages(
    [
        HumanMessage(content="Use Python 3.12 for this project."),
        AgentMessage(content="I'll target Python 3.12."),
        HumanMessage(content="What should the project metadata say?"),
    ]
)

plan = conversation.plan_compaction()
if plan is not None:
    # Summarize plan.previous_summary together with plan.older_messages.
    conversation.apply_compaction(plan, "The project targets Python 3.12.")
