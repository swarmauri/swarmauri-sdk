import os
import json
from collections import defaultdict, deque
from jinja2 import Environment, FileSystemLoader
import pkg_resources

# ------------------------------------------------------------------------------
# 1. SETUP: Adjust these paths as needed
# ------------------------------------------------------------------------------
BASE_DIR = os.getcwd()  # Use current working directory instead of __file__
# Adjust these to your actual template paths
COPY_TEMPLATES_DIR = os.path.join(BASE_DIR, "templatesv2", "component")
AGENT_PROMPT_TEMPLATE = os.path.join(BASE_DIR, "templatesv2", "component", "agent.j2")

# Paths to your payload JSON files
GLOBAL_PAYLOAD_PATH = os.path.join(BASE_DIR, "project_payload.json")
FILES_PAYLOAD_PATH = os.path.join(BASE_DIR, "templatesv2", "component", "payload.json")
SWARMAURI_PACKAGE_PATH = os.path.join("E:\\swarmauri_github\\swarmauri-sdk\\pkgs")
    
def main():
    # 1) Load the global payload (dictionary of global attributes)
    global_attrs = load_global_payload(GLOBAL_PAYLOAD_PATH)

    # 2) Load the files payload (list of file records)
    files_payload = load_files_payload(FILES_PAYLOAD_PATH)

    # 3) Resolve placeholders:
    #    - FILE_NAME remains unrendered in 'FILE_NAME'
    #    - RENDERED_FILE_NAME holds the expanded placeholders
    #    - RENDERED_DEPENDENCIES holds the expanded dependency placeholders
    #    - Other fields (DESCRIPTION, DEPENDENCIES, etc.) are rendered in-place
    resolved_payload = resolve_placeholders(files_payload, global_attrs)

    # 4) Perform a topological sort of the resolved payload
    #    We treat each file’s RENDERED_FILE_NAME as its node ID.
    #    If file A depends on file B, that means we have edge B -> A.
    ordered_entries = topological_sort(resolved_payload)

    # DEBUG: Print the sorted order
    from pprint import pprint
    print("\n[INFO] Sorted Payload Entries:")
    pprint([e["RENDERED_FILE_NAME"] for e in ordered_entries])

    # 5) Prepare a Jinja2 environment for standard COPY templates
    copy_env = Environment(
        loader=FileSystemLoader([
            COPY_TEMPLATES_DIR,  # where your .j2 templates live
            BASE_DIR, # where the newly created code will live
            SWARMAURI_PACKAGE_PATH # to import swarmauri modules
        ]),
        autoescape=False
    )


    # If you need agent credentials, pass them here
    agent_env = {}

    # 6) Process each file in sorted order
    for entry in ordered_entries:
        process_type = entry.get("PROCESS_TYPE", "COPY").upper()
        final_filename = entry["RENDERED_FILE_NAME"]
    
        # Pass global_attrs so your templates can see them
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

# ------------------------------------------------------------------------------
# 1. PAYLOAD LOADING
# ------------------------------------------------------------------------------
def load_global_payload(path):
    """
    Global attributes, e.g. {
       "PROJECT_ROOT": "/home/me/my_project",
       "RESOURCE_KIND": "robotic",
       ...
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_files_payload(path):
    """
    List of file-definitions, each is a dict with FILE_NAME, DEPENDENCIES, etc.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ------------------------------------------------------------------------------
# 2. PLACEHOLDER RESOLUTION
# ------------------------------------------------------------------------------
def resolve_placeholders(files_payload, global_attrs):
    """
    For each record:
      - Keep 'FILE_NAME' unmodified (with placeholders).
      - Create 'RENDERED_FILE_NAME' by expanding placeholders 
        using global_attrs + the record.
      - Create 'RENDERED_DEPENDENCIES' by expanding each dependency
        using the same context.
      - Render placeholders in all other string/list fields (e.g. DESCRIPTION)
        directly in-place.

    Returns a new list of fully resolved entries.
    """
    env = Environment(autoescape=False)
    resolved_entries = []

    for record in files_payload:
        # Merged context for placeholders: global + this record
        context = {**global_attrs, **record}
        new_record = {}

        # 1) Handle FILE_NAME => RENDERED_FILE_NAME
        unrendered_name = record["FILE_NAME"] + '.j2'
        new_record["FILE_NAME"] = unrendered_name  # keep placeholders
        rendered_template = env.from_string(unrendered_name)
        rendered_name = rendered_template.render(**context)
        new_record["RENDERED_FILE_NAME"] = rendered_name.replace('.j2', '')

        # 2) Render placeholders in DEPENDENCIES => RENDERED_DEPENDENCIES
        rendered_deps = []
        for dep in record.get("DEPENDENCIES", []):
            # Each dependency could be a string with placeholders
            dep_template = env.from_string(dep)
            rendered_dep = dep_template.render(**context)
            rendered_deps.append(rendered_dep)
        new_record["RENDERED_DEPENDENCIES"] = rendered_deps

        # 3) Render placeholders in all other fields
        #    (excluding FILE_NAME, DEPENDENCIES which we've handled)
        for key, val in record.items():
            if key in ["FILE_NAME", "DEPENDENCIES"]:
                continue
            if isinstance(val, str):
                new_record[key] = env.from_string(val).render(**context)
            elif isinstance(val, list):
                rendered_list = []
                for item in val:
                    if isinstance(item, str):
                        rendered_item = env.from_string(item).render(**context)
                        rendered_list.append(rendered_item)
                    else:
                        rendered_list.append(item)
                new_record[key] = rendered_list
            else:
                new_record[key] = val  # copy as-is

        resolved_entries.append(new_record)

    return resolved_entries

# ------------------------------------------------------------------------------
# 3. TOPOLOGICAL SORT (Using RENDERED_FILE_NAME)
# ------------------------------------------------------------------------------
def topological_sort(payload):
    """
    Returns a list of entries in an order that respects dependencies.
    We use RENDERED_FILE_NAME as the node ID, and each file’s
    RENDERED_DEPENDENCIES to build edges: dependency -> file.

    If file A depends on file B, then B must appear before A in the final order.
    """
    # 1) Build the forward graph based on RENDERED names
    graph, in_degree = build_forward_graph(payload)

    # 2) Traverse in topological order using Kahn’s Algorithm
    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    sorted_entries = []

    # For quick lookup from node ID -> the actual payload entry
    entry_map = { e["RENDERED_FILE_NAME"]: e for e in payload }

    while queue:
        current = queue.popleft()
        # Add the corresponding payload entry if it exists
        if current in entry_map:
            sorted_entries.append(entry_map[current])

        # Decrement in-degrees of neighbors
        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If not all nodes were sorted, there's likely a cycle
    if len(sorted_entries) < len(entry_map):
        print("[WARNING] Some dependencies may be cyclical or missing.")

    return sorted_entries

def build_forward_graph(payload):
    """
    Builds a forward adjacency list + in-degree map based on:
      - RENDERED_FILE_NAME
      - RENDERED_DEPENDENCIES

    If X depends on Y, we add edge (Y -> X).

    Returns: (graph, in_degree)
      - graph[node] = list of nodes that depend on 'node'
      - in_degree[node] = number of edges pointing into 'node'
    """
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    # Gather all node IDs (RENDERED_FILE_NAME)
    all_nodes = set(entry["RENDERED_FILE_NAME"] for entry in payload)
    for node in all_nodes:
        in_degree[node] = 0

    # Build edges from each dependency to the file
    for entry in payload:
        file_node = entry["RENDERED_FILE_NAME"]
        for dep in entry["RENDERED_DEPENDENCIES"]:
            if dep in all_nodes:
                # If file_node depends on dep, then dep -> file_node
                graph[dep].append(file_node)
                in_degree[file_node] += 1

    # Ensure all nodes appear in the graph
    for node in all_nodes:
        if node not in graph:
            graph[node] = []

    return graph, in_degree

# ------------------------------------------------------------------------------
# 4. PROCESSING (COPY / GENERATE)
# ------------------------------------------------------------------------------
def render_copy_template(entry, copy_env, global_attrs):
    """
    For 'COPY':
      - The unrendered FILE_NAME's basename determines the Jinja2 template to load.
      - We render that template using the entire entry + global_attrs as context.
    """
    unrendered_name = entry["FILE_NAME"]
    filename_basename = os.path.basename(unrendered_name)
    template_name = filename_basename + ".j2"

    # Search for the template
    template_rel_path = find_template(template_name, copy_env.loader.searchpath[0])
    if not template_rel_path:
        print(f"[ERROR] Template not found for: {template_name}")
        return None

    # Merge contexts: global + this entry
    context = {**global_attrs, **entry}
    template = copy_env.get_template(template_rel_path)
    return template.render(**context)


def render_generate_template(entry, agent_env, copy_env, global_attrs):
    """
    For 'GENERATE':
      - Render an agent prompt (agent.j2) using the entire entry + global_attrs as context.
      - Then call an external LLM or agent to produce final file content.
    """
    # Load the agent prompt template
    with open(AGENT_PROMPT_TEMPLATE, "r", encoding="utf-8") as f:
        agent_prompt_str = f.read()

    # Merge contexts: global + this entry
    context = {**global_attrs, **entry}
    
    agent_prompt_template = copy_env.from_string(agent_prompt_str)
    agent_prompt = agent_prompt_template.render(**context)

    # Now call your external agent to get the final code
    content = call_external_agent(agent_prompt, agent_env)
    print(f"[INFO]: Rendered count: {content}")
    return content

def chunk_content(full_content: str) -> str:
    """
    Splits the content into chunks using the chunker.
    """
    from swarmauri.chunkers.MdSnippetChunker import MdSnippetChunker
    chunker = MdSnippetChunker()
    split = chunker.chunk_text(full_content)
    try:
        return split[0][2]
    except IndexError:
        return full_content

def call_external_agent(prompt, agent_env):
    """
    Placeholder function to integrate with an LLM (e.g. OpenAI, Hugging Face).
    """
    print("[INFO] Prompt sent to agent (truncated):")
    # print(prompt, '\n\n')  # Show complete prompt
    print(prompt[:250], "...\n")  # Show partial prompt
    # Return a dummy code snippet for demonstration
    from swarmauri.llms.DeepInfraModel import DeepInfraModel
    from swarmauri.agents.RagAgent import RagAgent
    from swarmauri.vector_stores.TfidfVectorStore import TfidfVectorStore
    llm = DeepInfraModel(api_key="***", name="meta-llama/Meta-Llama-3.1-405B-Instruct")
    agent = RagAgent(llm=llm, vector_store=TfidfVectorStore())
    result = agent.exec(prompt, top_k=0, llm_kwargs={"max_tokens": 3000})
    chunk = chunk_content(result)
    del agent
    return chunk

def save_file(content, filepath):
    """
    Creates directories as needed and saves the given content to 'filepath'.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[INFO] Wrote file: {filepath}")

def find_template(template_name, search_root):
    """
    Recursively search for 'template_name' under 'search_root'.
    Return the relative path if found, else None.
    """
    for root, dirs, files in os.walk(search_root):
        if template_name in files:
            return os.path.relpath(os.path.join(root, template_name), search_root)
    return None

# ------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
