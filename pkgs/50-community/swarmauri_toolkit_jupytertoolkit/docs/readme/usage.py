from fastapi import FastAPI, BackgroundTasks
from swarmauri_toolkit_jupytertoolkit import JupyterToolkit

app = FastAPI()
toolkit = JupyterToolkit()


@app.post("/execute")
def execute(data: dict, background: BackgroundTasks):
    nb_path = data["notebook_path"]
    background.add_task(
        toolkit.tools["JupyterExecuteNotebookWithParametersTool"],
        notebook_path=nb_path,
        parameters=data.get("parameters", {}),
    )
    return {"status": "queued", "notebook": nb_path}
