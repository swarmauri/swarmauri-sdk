import os
import json
import re
from collections import defaultdict, deque
from jinja2 import Environment, FileSystemLoader
from pprint import pprint

# ------------------------------------------------------------------------------
# GLOBAL SETUP
# ------------------------------------------------------------------------------
BASE_DIR = os.getcwd()  # Current working directory
PROJECTS_PAYLOAD_PATH = os.path.join(BASE_DIR, "projects_payloads.json")
SWARMAURI_PACKAGE_PATH = os.path.join("pkgs")


def get_template_dir_any(template_set: str) -> str:
    """
    Returns the absolute path for a template folder if it exists
    in the 'templatesv2' directory. Otherwise, raises a ValueError.
    """
    template_dir = os.path.join(BASE_DIR, "templatesv2", template_set)
    if not os.path.isdir(template_dir):
        raise ValueError(
            f"Template directory '{template_set}' does not exist in templatesv2."
        )
    return template_dir


# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
def main():
    """
    Main entry point. Loads the list of project payloads from PROJECTS_PAYLOAD_PATH.
    Then processes each payload in turn.
    """
    projects_list = load_projects_list(PROJECTS_PAYLOAD_PATH)

    for project_index, global_attrs in enumerate(projects_list, start=1):
        print(f"\n[INFO] ---- Processing Project #{project_index} ----")
        process_single_project_payload(global_attrs)


# ------------------------------------------------------------------------------
# PROCESSING A SINGLE PROJECT PAYLOAD
# ------------------------------------------------------------------------------
def process_single_project_payload(global_attrs):
    """
    Processes a single project payload by:
      1. Determining which template folder to use.
      2. Loading the files payload (JSON template) from that folder.
      3. Resolving placeholders, sorting files topologically,
         and rendering files (either via COPY or GENERATE).
      4. Saving the final global_attrs payload.
    """
    # Get the template set from the project payload (or use "default")
    template_set = global_attrs.get("TEMPLATE_SET", "default")
    try:
        template_dir = get_template_dir_any(template_set)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # Build paths for the templates from the selected template folder.
    # Note: The agent prompt template may be defined in a file entry,
    # so we won't fix a single agent_prompt_template_path here.
    files_payload_template_path = os.path.join(template_dir, "payload.json.j2")

    # Step 1: Load the files payload using the files payload template
    files_payload = load_files_payload(files_payload_template_path, global_attrs)

    # Step 2: Resolve placeholders in the loaded payload
    resolved_payload = resolve_placeholders(files_payload, global_attrs)

    # Step 3: Topologically sort the resolved payload based on dependencies
    ordered_entries = topological_sort(resolved_payload)

    print("\n[INFO] Sorted Payload Entries:")
    pprint([e["RENDERED_FILE_NAME"] for e in ordered_entries])

    # Step 4: Set up the Jinja2 environment using the selected template folder
    copy_env = Environment(
        loader=FileSystemLoader([
            template_dir,          # Use the selected template folder
            BASE_DIR,              # For additional resources if needed
            SWARMAURI_PACKAGE_PATH # To import swarmauri modules
        ]),
        autoescape=False
    )

    agent_env = {}  # Define agent-specific settings if required

    # Step 5: Process each file entry
    for entry in ordered_entries:
        process_type = entry.get("PROCESS_TYPE", "COPY").upper()
        final_filename = entry["RENDERED_FILE_NAME"]

        if process_type == "COPY":
            content = render_copy_template(entry, copy_env, global_attrs)
            if content is not None:
                save_file(content, final_filename)

        elif process_type == "GENERATE":
            # Check if the file entry defines its own agent prompt template.
            # If not, fallback to the global setting or to "agent_default.j2".
            agent_prompt_template_name = entry.get(
                "AGENT_PROMPT_TEMPLATE",
                global_attrs.get("AGENT_PROMPT_TEMPLATE", "agent_default.j2")
            )
            agent_prompt_template_path = os.path.join(template_dir, agent_prompt_template_name)
            content = render_generate_template(
                entry, agent_env, copy_env, global_attrs, agent_prompt_template_path
            )
            if content is not None:
                save_file(content, final_filename)

        else:
            print(f"[WARNING] Unknown PROCESS_TYPE={process_type} for {final_filename}")

    # Step 6: Save the final global_attrs payload to payload.json
    package_payload_filename = os.path.join(
        BASE_DIR,
        global_attrs.get('PROJECT_ROOT', ''),
        global_attrs.get('PACKAGE_ROOT', ''),
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
    
    Supports an optional top-level key "AGENT_PROMPT_TEMPLATE" in the payload.
    If the rendered JSON is a dictionary, it is expected to contain a "FILES"
    key with the list of file payloads, and optionally an "AGENT_PROMPT_TEMPLATE".
    If the rendered JSON is a list, then it is taken as the list of file payloads.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            template_str = f.read()

        env = Environment(autoescape=False)
        template = env.from_string(template_str)
        rendered_str = template.render(**global_attrs)

        payload_data = json.loads(rendered_str)
        if isinstance(payload_data, dict):
            # If an agent prompt template is defined in the payload, update global_attrs.
            if "AGENT_PROMPT_TEMPLATE" in payload_data:
                global_attrs["AGENT_PROMPT_TEMPLATE"] = payload_data["AGENT_PROMPT_TEMPLATE"]
            # Return the list of file definitions under the "FILES" key.
            return payload_data.get("FILES", [])
        else:
            # If the payload is a list, return it as is.
            return payload_data
    except FileNotFoundError:
        print(f"[ERROR] The file {path} does not exist.")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to parse rendered JSON from {path}: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred while loading files payload: {e}")
        return []


# 2. PLACEHOLDER RESOLUTION
def resolve_placeholders(files_payload, global_attrs):
    """
    Resolves placeholders in each record:
      - Keeps 'FILE_NAME' unchanged.
      - Creates 'RENDERED_FILE_NAME' by expanding placeholders.
      - Expands placeholders in 'DEPENDENCIES' to form 'RENDERED_DEPENDENCIES'.
      - Renders all other string/list fields.
    """
    env = Environment(autoescape=False)
    resolved_entries = []

    for record in files_payload:
        context = {**global_attrs, **record}
        new_record = {}

        # Render FILE_NAME -> RENDERED_FILE_NAME
        unrendered_name = record["FILE_NAME"] + '.j2'
        new_record["FILE_NAME"] = unrendered_name
        try:
            rendered_template = env.from_string(unrendered_name)
            rendered_name = rendered_template.render(**context)
            new_record["RENDERED_FILE_NAME"] = rendered_name.replace('.j2', '')
        except Exception as e:
            print(f"[ERROR] Failed to render FILE_NAME '{unrendered_name}': {e}")
            new_record["RENDERED_FILE_NAME"] = unrendered_name.replace('.j2', '')

        # Render DEPENDENCIES -> RENDERED_DEPENDENCIES
        rendered_deps = []
        for dep in record.get("DEPENDENCIES", []):
            try:
                rendered_dep = env.from_string(dep).render(**context)
                rendered_deps.append(rendered_dep)
            except Exception as e:
                print(f"[ERROR] Failed to render DEPENDENCY '{dep}': {e}")
                rendered_deps.append(dep)
        new_record["RENDERED_DEPENDENCIES"] = rendered_deps

        # Render all other fields
        for key, val in record.items():
            if key in ["FILE_NAME", "DEPENDENCIES"]:
                continue

            if isinstance(val, str):
                try:
                    new_record[key] = env.from_string(val).render(**context)
                except Exception as e:
                    print(f"[ERROR] Failed to render field '{key}' with value '{val}': {e}")
                    new_record[key] = val

            elif isinstance(val, list):
                rendered_list = []
                for item in val:
                    if isinstance(item, str):
                        try:
                            rendered_item = env.from_string(item).render(**context)
                            rendered_list.append(rendered_item)
                        except Exception as e:
                            print(f"[ERROR] Failed to render list item '{item}' in field '{key}': {e}")
                            rendered_list.append(item)
                    else:
                        rendered_list.append(item)
                new_record[key] = rendered_list
            else:
                new_record[key] = val

        resolved_entries.append(new_record)

    return resolved_entries


# 3. TOPOLOGICAL SORT
def topological_sort(payload):
    """
    Returns a list of entries sorted so that if file A depends on file B,
    then B comes before A.
    """
    graph, in_degree = build_forward_graph(payload)

    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    sorted_entries = []

    entry_map = {e["RENDERED_FILE_NAME"]: e for e in payload}

    while queue:
        current = queue.popleft()
        if current in entry_map:
            sorted_entries.append(entry_map[current])

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(sorted_entries) < len(entry_map):
        print("[WARNING] Some dependencies may be cyclical or missing.")

    return sorted_entries


def build_forward_graph(payload):
    """
    Builds a graph (adjacency list and in-degree map) where an edge from Y to X
    indicates that file X depends on file Y.
    """
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    all_nodes = set(entry["RENDERED_FILE_NAME"] for entry in payload)
    for node in all_nodes:
        in_degree[node] = 0

    for entry in payload:
        file_node = entry["RENDERED_FILE_NAME"]
        for dep in entry.get("RENDERED_DEPENDENCIES", []):
            if dep in all_nodes:
                graph[dep].append(file_node)
                in_degree[file_node] += 1
            else:
                print(f"[WARNING] Dependency '{dep}' for file '{file_node}' not found among all nodes.")

    for node in all_nodes:
        if node not in graph:
            graph[node] = []

    return graph, in_degree


# 4. PROCESSING (COPY / GENERATE)
def render_copy_template(entry, copy_env, global_attrs):
    """
    Renders a file template (for process type COPY) using the provided Jinja2 environment.
    """
    template_path = entry["FILE_NAME"]  # e.g., "subfolder/my_file.py.j2"
    context = {**global_attrs, **entry}

    try:
        template = copy_env.get_template(template_path)
        return template.render(**context)
    except Exception as e:
        print(f"[ERROR] Failed to render COPY template '{template_path}': {e}")
        return None


def render_generate_template(entry, agent_env, copy_env, global_attrs, agent_prompt_template_path):
    """
    Renders an agent prompt template (from agent_prompt_template_path) and
    calls an external agent to generate file content.
    """
    try:
        with open(agent_prompt_template_path, "r", encoding="utf-8") as f:
            agent_prompt_str = f.read()

        context = {**global_attrs, **entry}
        agent_prompt_template = copy_env.from_string(agent_prompt_str)
        agent_prompt = agent_prompt_template.render(**context)

        content = call_external_agent(agent_prompt, agent_env)
        print(f"[INFO] Generated content length: {len(content)} characters")
        return content
    except Exception as e:
        print(f"[ERROR] Failed to generate content for '{entry['RENDERED_FILE_NAME']}': {e}")
        return None


def call_external_agent(prompt, agent_env):
    """
    Placeholder function to integrate with an external LLM/Agent.
    """
    print("[INFO] Prompt sent to agent (truncated):")
    print(prompt[:250] + "...\n")  # Show a truncated version of the prompt

    # Example: Using swarmauri components (adjust as needed)
    from swarmauri.agents.RagAgent import RagAgent
    from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
    # You can swap in your desired LLM model here
    llm = O1Model(api_key="***", name="o3-mini")
    system_context = "You are a helpful assistant."
    agent = RagAgent(llm=llm, vector_store=TfidfVectorStore(), system_context=system_context)
    result = agent.exec(prompt, top_k=0)
    content = chunk_content(result)
    del agent
    return content


def chunk_content(full_content: str) -> str:
    """
    Optionally splits the content into chunks. Returns either a single chunk
    or the full content.
    """
    try:
        # Remove any unwanted <think> blocks
        pattern = r"<think>[\s\S]*?</think>"
        cleaned_text = re.sub(pattern, "", full_content).strip()

        from swarmauri.chunkers.MdSnippetChunker import MdSnippetChunker
        chunker = MdSnippetChunker()
        chunks = chunker.chunk_text(cleaned_text)
        if len(chunks) > 1:
            return cleaned_text
        try:
            return chunks[0][2]
        except IndexError:
            return cleaned_text
    except ImportError:
        print("[WARNING] MdSnippetChunker not found. Returning full content without chunking.")
        return full_content
    except Exception as e:
        print(f"[ERROR] Failed to chunk content: {e}")
        return full_content


# 5. FILE SAVING / UTILITY
def save_file(content, filepath):
    """
    Creates directories as needed and saves the given content to the specified filepath.
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
    Saves the final global_attrs payload to a local payload.json for reference.
    """
    try:
        os.makedirs(os.path.dirname(package_payload_filename), exist_ok=True)
        with open(package_payload_filename, "w", encoding='utf-8') as f:
            json.dump(global_attrs, f, indent=4)
        print(f"[INFO] Saved payload: {package_payload_filename}")
    except Exception as e:
        print(f"[ERROR] Failed to save payload '{package_payload_filename}': {e}")


# ------------------------------------------------------------------------------
# MAIN EXECUTION
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
