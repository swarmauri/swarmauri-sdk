import os
import json
from collections import defaultdict, deque
from jinja2 import Environment, FileSystemLoader
from pprint import pprint

# ------------------------------------------------------------------------------
# 1. SETUP: Adjust these paths as needed
# ------------------------------------------------------------------------------
BASE_DIR = os.getcwd()  # Use current working directory

# This JSON file contains a list of project payloads
PROJECTS_PAYLOAD_PATH = os.path.join(BASE_DIR, "projects_payloads.json")

# Directories for templates
COPY_TEMPLATES_DIR = os.path.join(BASE_DIR, "templatesv2", "component")
AGENT_PROMPT_TEMPLATE = os.path.join(BASE_DIR, "templatesv2", "component", "agent.j2")

# Path to your "files payload" template, which is a Jinja2 + JSON
FILES_PAYLOAD_TEMPLATE_PATH = os.path.join(BASE_DIR, "templatesv2", "component", "payload.json.j2")

# Path to swarmauri package (adjust if necessary)
SWARMAURI_PACKAGE_PATH = os.path.join("E:\\swarmauri_github\\swarmauri-sdk\\pkgs")


def main():
    """
    Main entry point. Loads the list of project payloads from PROJECTS_PAYLOAD_PATH.
    Then processes each payload in turn.
    """
    # 1) Load an array of project payloads
    projects_list = load_projects_list(PROJECTS_PAYLOAD_PATH)

    # 2) Iterate through each project payload and process it
    for project_index, global_attrs in enumerate(projects_list, start=1):
        print(f"\n[INFO] ---- Processing Project #{project_index} ----")
        process_single_project_payload(global_attrs)


def process_single_project_payload(global_attrs):
    """
    Processes a single project payload by performing the following steps:
      1. Load the files payload (list of file records) from Jinja2 template.
      2. Resolve placeholders in file records.
      3. Perform a topological sort based on dependencies.
      4. Render and save files (COPY or GENERATE).
      5. Save the final global_attrs to payload.json.
    """
    # Step 1: Load the files payload for this project
    files_payload = load_files_payload(FILES_PAYLOAD_TEMPLATE_PATH, global_attrs)

    # Step 2: Resolve placeholders in the loaded payload
    resolved_payload = resolve_placeholders(files_payload, global_attrs)

    # Step 3: Perform a topological sort of the resolved payload
    ordered_entries = topological_sort(resolved_payload)

    # Debug: Print the sorted order
    print("\n[INFO] Sorted Payload Entries:")
    pprint([e["RENDERED_FILE_NAME"] for e in ordered_entries])

    # Step 4: Prepare a Jinja2 environment for standard COPY templates
    copy_env = Environment(
        loader=FileSystemLoader([
            COPY_TEMPLATES_DIR,       # Where your .j2 templates live
            BASE_DIR,                 # Where the newly created code will live
            SWARMAURI_PACKAGE_PATH    # To import swarmauri modules
        ]),
        autoescape=False
    )

    # If your Generate step needs special credentials or environment,
    # define them here
    agent_env = {}

    # Step 5: Process each file in sorted order
    for entry in ordered_entries:
        process_type = entry.get("PROCESS_TYPE", "COPY").upper()
        final_filename = entry["RENDERED_FILE_NAME"]

        if process_type == "COPY":
            content = render_copy_template(entry, copy_env, global_attrs)
            if content is not None:
                save_file(content, final_filename)

        elif process_type == "GENERATE":
            content = render_generate_template(entry, agent_env, copy_env, global_attrs)
            if content is not None:
                save_file(content, final_filename)

        else:
            print(f"[WARNING] Unknown PROCESS_TYPE={process_type} for {final_filename}")

    # Step 6: Save the updated global_attrs to a local payload.json
    package_payload_filename = os.path.join(
        BASE_DIR,
        global_attrs['PROJECT_ROOT'],
        global_attrs['PACKAGE_ROOT'],
        "payload.json"
    )
    save_payload(package_payload_filename, global_attrs)


# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

# 1. LOADING PROJECTS & FILE PAYLOAD
def load_projects_list(path):
    """
    Loads a JSON file that contains an array of project payloads.

    Example structure:
    [
      { ... },  # Project 1
      { ... },  # Project 2
      ...
    ]
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            projects = json.load(f)
            if not isinstance(projects, list):
                raise ValueError("projects_payloads.json must contain a list of project payloads.")
            return projects
    except FileNotFoundError:
        print(f"[ERROR] The file {path} does not exist.")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse JSON from {path}: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while loading projects: {e}")
        return []


def load_files_payload(path, global_attrs):
    """
    Loads a Jinja2-based JSON template (payload.json.j2), renders it
    with `global_attrs`, and then parses the result as JSON.
    """
    try:
        # 1) Read the file as a string
        with open(path, "r", encoding="utf-8") as f:
            template_str = f.read()

        # 2) Render via Jinja2
        env = Environment(autoescape=False)
        template = env.from_string(template_str)
        rendered_str = template.render(**global_attrs)  # Ensure global_attrs is a dict

        # 3) Parse the rendered string as JSON
        return json.loads(rendered_str)
    except FileNotFoundError:
        print(f"[ERROR] The file {path} does not exist.")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse rendered JSON from {path}: {e}")
        return []
    except TypeError as e:
        print(f"[ERROR] TypeError during template rendering: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while loading files payload: {e}")
        return []


# 2. PLACEHOLDER RESOLUTION
def resolve_placeholders(files_payload, global_attrs):
    """
    For each record in files_payload:
      - Keep 'FILE_NAME' unmodified (placeholders intact).
      - Create 'RENDERED_FILE_NAME' by expanding placeholders.
      - Create 'RENDERED_DEPENDENCIES' by expanding each dependency.
      - Render placeholders in all other fields in place.

    Returns a new list of fully resolved entries.
    """
    env = Environment(autoescape=False)
    resolved_entries = []

    for record in files_payload:
        # Merge context: global_attrs + record
        context = {**global_attrs, **record}
        new_record = {}

        # 1) Handle FILE_NAME => RENDERED_FILE_NAME
        unrendered_name = record["FILE_NAME"] + '.j2'  # Temporarily append .j2
        new_record["FILE_NAME"] = unrendered_name  # Keep placeholders intact
        try:
            rendered_template = env.from_string(unrendered_name)
            rendered_name = rendered_template.render(**context)
            new_record["RENDERED_FILE_NAME"] = rendered_name.replace('.j2', '')
        except Exception as e:
            print(f"[ERROR] Failed to render FILE_NAME '{unrendered_name}': {e}")
            new_record["RENDERED_FILE_NAME"] = rendered_name if 'rendered_name' in locals() else unrendered_name.replace('.j2', '')

        # 2) Render placeholders in DEPENDENCIES => RENDERED_DEPENDENCIES
        rendered_deps = []
        for dep in record.get("DEPENDENCIES", []):
            try:
                rendered_dep = env.from_string(dep).render(**context)
                rendered_deps.append(rendered_dep)
            except Exception as e:
                print(f"[ERROR] Failed to render DEPENDENCY '{dep}': {e}")
                rendered_deps.append(dep)  # Keep original if rendering fails
        new_record["RENDERED_DEPENDENCIES"] = rendered_deps

        # 3) Render placeholders in all other fields
        for key, val in record.items():
            if key in ["FILE_NAME", "DEPENDENCIES"]:
                continue  # Already handled

            if isinstance(val, str):
                try:
                    new_record[key] = env.from_string(val).render(**context)
                except Exception as e:
                    print(f"[ERROR] Failed to render field '{key}' with value '{val}': {e}")
                    new_record[key] = val  # Keep original if rendering fails

            elif isinstance(val, list):
                rendered_list = []
                for item in val:
                    if isinstance(item, str):
                        try:
                            rendered_item = env.from_string(item).render(**context)
                            rendered_list.append(rendered_item)
                        except Exception as e:
                            print(f"[ERROR] Failed to render list item '{item}' in field '{key}': {e}")
                            rendered_list.append(item)  # Keep original
                    else:
                        rendered_list.append(item)  # Non-string items are kept as-is
                new_record[key] = rendered_list
            else:
                new_record[key] = val  # Non-string/non-list fields are copied as-is

        resolved_entries.append(new_record)

    return resolved_entries


# 3. TOPOLOGICAL SORT
def topological_sort(payload):
    """
    Returns a list of entries in an order that respects dependencies, i.e.,
    if file A depends on file B, B must appear before A.

    Uses RENDERED_FILE_NAME for node ID and RENDERED_DEPENDENCIES for edges.
    """
    graph, in_degree = build_forward_graph(payload)

    # Kahn’s Algorithm
    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    sorted_entries = []

    # For quick lookup from node -> payload entry
    entry_map = {e["RENDERED_FILE_NAME"]: e for e in payload}

    while queue:
        current = queue.popleft()
        if current in entry_map:
            sorted_entries.append(entry_map[current])

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Warn if not all were sorted => cycle or missing dependency
    if len(sorted_entries) < len(entry_map):
        print("[WARNING] Some dependencies may be cyclical or missing.")

    return sorted_entries


def build_forward_graph(payload):
    """
    Create adjacency list + in_degree map:
      - node = RENDERED_FILE_NAME
      - edges from each dependency to the dependent file.

    If X depends on Y, add edge Y -> X.
    """
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    # Gather all node IDs
    all_nodes = set(entry["RENDERED_FILE_NAME"] for entry in payload)
    for node in all_nodes:
        in_degree[node] = 0

    # Build edges
    for entry in payload:
        file_node = entry["RENDERED_FILE_NAME"]
        for dep in entry.get("RENDERED_DEPENDENCIES", []):
            if dep in all_nodes:
                graph[dep].append(file_node)
                in_degree[file_node] += 1
            else:
                print(f"[WARNING] Dependency '{dep}' for file '{file_node}' not found among all nodes.")

    # Ensure every node is in the graph
    for node in all_nodes:
        if node not in graph:
            graph[node] = []

    return graph, in_degree


# 4. PROCESSING (COPY / GENERATE)
def render_copy_template(entry, copy_env, global_attrs):
    """
    Renders a file template from the local filesystem.

    Parameters:
      - entry: The resolved payload entry.
      - copy_env: Jinja2 Environment for COPY templates.
      - global_attrs: Global attributes dictionary.

    Returns:
      - Rendered content as a string.
    """
    template_path = entry["FILE_NAME"]  # e.g., "subfolder/my_file.py.j2"
    context = {**global_attrs, **entry}

    try:
        template = copy_env.get_template(template_path)
        return template.render(**context)
    except Exception as e:
        print(f"[ERROR] Failed to render COPY template '{template_path}': {e}")
        return None


def render_generate_template(entry, agent_env, copy_env, global_attrs):
    """
    For 'GENERATE' process type:
      1. Build an agent prompt from 'agent.j2' template.
      2. Call an external LLM/Agent to get final content.

    Parameters:
      - entry: The resolved payload entry.
      - agent_env: Environment or credentials for the agent.
      - copy_env: Jinja2 Environment for COPY templates.
      - global_attrs: Global attributes dictionary.

    Returns:
      - Generated content as a string.
    """
    try:
        # 1) Load the agent prompt template
        with open(AGENT_PROMPT_TEMPLATE, "r", encoding="utf-8") as f:
            agent_prompt_str = f.read()

        # 2) Merge contexts
        context = {**global_attrs, **entry}
        agent_prompt_template = copy_env.from_string(agent_prompt_str)
        agent_prompt = agent_prompt_template.render(**context)

        # 3) Call your external agent to get the content
        content = call_external_agent(agent_prompt, agent_env)
        print(f"[INFO] Generated content length: {len(content)} characters")
        return content
    except Exception as e:
        print(f"[ERROR] Failed to generate content for '{entry['RENDERED_FILE_NAME']}': {e}")
        return None


def call_external_agent(prompt, agent_env):
    """
    Placeholder function to integrate with an LLM (e.g. OpenAI, Hugging Face).
    """
    print("[INFO] Prompt sent to agent (truncated):")
    print(prompt, '\n\n')  # Show partial prompt
    # print(prompt[:250], "...\n")  # Show partial prompt
    # Return a dummy code snippet for demonstration
    #from swarmauri.llms.DeepInfraModel import DeepInfraModel
    from swarmauri.agents.RagAgent import RagAgent
    from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
    #llm = DeepInfraModel(api_key="***", name="meta-llama/Meta-Llama-3.1-405B-Instruct")
    #llm.allowed_models.append('deepseek-ai/DeepSeek-R1')
    #llm.name = 'deepseek-ai/DeepSeek-R1'
    llm = O1Model(api_key="***", name="o1")
    #llm = TogetherModel(api_key="***")
    #system_context= "You are a python developer. You responsibility for the development and documentation of python packages."
    system_context = "You are a helpful assistant."
    agent = RagAgent(llm=llm, vector_store=TfidfVectorStore(), system_context=system_context)
    #result = agent.exec(prompt, top_k=0, llm_kwargs={"max_tokens": 30000})
    result = agent.exec(prompt, top_k=0)
    chunk = chunk_content(result)
    del agent
    return chunk


def chunk_content(full_content: str) -> str:
    """
    Splits the content into chunks using a chunker.

    Parameters:
      - full_content: The complete content string.

    Returns:
      - A single chunk or the entire content if chunking is not applicable.
    """
    try:
        from swarmauri.chunkers.MdSnippetChunker import MdSnippetChunker
        import re
        pattern = r"<think>[\s\S]*?</think>"
        cleaned_text = re.sub(pattern, "", full_content).strip()
        chunker = MdSnippetChunker()
        split = chunker.chunk_text(cleaned_text)
        if len(split) > 1:
            return cleaned_text
        try:
            return split[0][2]
        except IndexError:
            return cleaned_text
    except ImportError:
        print("[WARNING] MdSnippetChunker not found. Returning full content without chunking.")
        return cleaned_text
    except Exception as e:
        print(f"[ERROR] Failed to chunk content: {e}")
        return cleaned_text


# 5. FILE SAVING / UTILITY
def save_file(content, filepath):
    """
    Creates directories as needed and saves the given content to 'filepath'.

    Parameters:
      - content: The content to write to the file.
      - filepath: The path where the file should be saved.
    """
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[INFO] Wrote file: {filepath}")
    except Exception as e:
        print(f"[ERROR] Failed to save file '{filepath}': {e}")


def save_payload(package_payload_filename, global_attrs):
    """
    Saves the final global_attrs to a local payload.json for reference.

    Parameters:
      - package_payload_filename: The path where payload.json should be saved.
      - global_attrs: The global attributes dictionary.
    """
    try:
        os.makedirs(os.path.dirname(package_payload_filename), exist_ok=True)
        with open(package_payload_filename, "w", encoding='utf-8') as f:
            json.dump(global_attrs, f, indent=4)
        print(f"[INFO] Saved payload: {package_payload_filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save payload '{package_payload_filename}': {e}")


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
