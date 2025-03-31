# PTGEN SPECIFICATION 0.0.1

# Definitions

## projects_payload.yaml
## ptree.yaml.j2
## agent_default.j2
## template set

# File Schemas

## projects_payload.yaml
### project
- project_name
- project_root
- project_purpose (optional)
- project_description (optional)
- project_requirements (optional)
- template_set
- packages

### modules
- name
- authors
- purpose
- description
- requirements
- dependencies (optional)
	- elaborate how different ways to link (ie: colon notation)
- examples (optional)
- template_set_override (optional)
- extras: resource_kind, base_name, base_file (optional)

## ptree.yaml.j2
### loop levels
project, package, module
### file record schemas
- FILE_NAME
- RENDERED_FILE_NAME
- PROCESS_TYPE (COPY, GENERATE, SCRIPT)
- AGENT_PROMPT_TEMPLATE (optional)
- PROJECT_NAME
- PACKAGE_NAME
- MODULE_NAME
- FILE_CTX

### FILE_CTX:
- purpose 
- description
- requirements
- DEPENDENCIES (optional)
- EXAMPLES (optional)
- extras.base_class, extras.mixins, extras.resource_kind (optional)

## agent_default.j2
- command
- purpose
- description
- requirements
- style guide
- dependencies
- file and code preferences
- desired output (FILE_CTX.EXAMPLES)
- example output (FILE_CTX.FILE_NAME or FILE_CTX.FILE_NAME)
- dependencies (FILE_CTX.dependencies)

## template set .j2 files
can reference one of three contexts:
1. PKG_CTX
2. MOD_CTX
3. FIL_CTX