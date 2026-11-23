from swarmauri_agent_package_maintenance import PackageMaintenanceAgent
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_base.skills.SkillCatalog import SkillCatalog
from swarmauri_standard.tool_llms.OpenAIToolModel import OpenAIToolModel
from swarmauri_toolkit_containertoolkit import ContainerToolkit

agent = PackageMaintenanceAgent(
    llm=OpenAIToolModel(api_key="your-api-key"),
    store=SqliteRunStore(path="maintenance.db"),
    skills=SkillCatalog([]),
    container=ContainerToolkit(container_name="sdk-checks"),
    repository_scope="sdk-checks",
    members={"swarmauri_core": "pkgs/10-interfaces/swarmauri_core"},
)
# Mount the SDK checkout as /workspace in the configured container first.
state = agent.exec("Ask which package I want to check.")
