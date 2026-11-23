from swarmauri_agent_compacting import CompactingAgent
from swarmauri_conversation_compacting import CompactingConversation


def make_agent(model, count_tokens):
    return CompactingAgent(
        llm=model,
        conversation=CompactingConversation(
            trigger_tokens=24_000,
            keep_recent_turns=4,
        ),
        count_input_tokens=count_tokens,
        max_input_tokens=28_000,
    )


def run_turn(agent, prompt):
    reply = agent.exec(prompt)
    changed = agent.compact()
    return reply, changed


async def run_turn_async(agent, prompt):
    reply = await agent.aexec(prompt)
    changed = await agent.acompact()
    return reply, changed
