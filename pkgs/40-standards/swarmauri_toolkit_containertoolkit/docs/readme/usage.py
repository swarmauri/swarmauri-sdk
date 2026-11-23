from swarmauri_toolkit_containertoolkit import ContainerToolkit

toolkit = ContainerToolkit(
    container_name="my-container", image="ubuntu:latest"
)
print(toolkit.tools.keys())
