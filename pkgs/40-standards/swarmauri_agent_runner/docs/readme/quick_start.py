from swarmauri_agent_runner import AgentRunner
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel

model = OpenAIToolModel(api_key="your-api-key")
runner = AgentRunner(model, SqliteRunStore(path="runs.db"))
state = runner.start("Ask me which package to inspect.")
if state.status == "input_required":
    from swarmauri_standard.messages.AnswerMessage import AnswerMessage

    question = state.event().question
    reply = AnswerMessage(
        question_id=question.question_id, answer=input(question.content)
    )
    state = runner.resume(state.run_id, reply)
