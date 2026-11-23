from pathlib import Path

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

templates_dir = Path("templates")
templates_dir.mkdir(parents=True, exist_ok=True)

template_path = templates_dir / "greeting.j2"
template_path.write_text("Hello, {{ animal|make_plural }}!", encoding="utf-8")

prompt = J2PromptTemplate(templates_dir=str(templates_dir))
prompt.set_template(template_path)

print(prompt({"animal": "fox"}))  # Hello, foxes!
