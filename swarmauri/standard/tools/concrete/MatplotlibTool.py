import matplotlib.pyplot as plt
from typing import List, Literal
from pydantic import Field
from standard.tools.base.ToolBase import ToolBase, Parameter

class MatplotlibTool(ToolBase):
    version: str = "1.0.0"
    name: str = "MatplotlibTool"
    description: str = "Generates a plot using Matplotlib library based on provided configuration."
    type: Literal["MatplotlibTool"] = "MatplotlibTool"
    
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="plot_type",
            type="string",
            description="Type of plot to generate (e.g., 'line', 'bar', 'scatter').",
            required=True,
            enum=["line", "bar", "scatter"]
        ),
        Parameter(
            name="x_data",
            type="list<float>",
            description="X-axis data for the plot.",
            required=True
        ),
        Parameter(
            name="y_data",
            type="list<float>",
            description="Y-axis data for the plot.",
            required=True
        ),
        Parameter(
            name="title",
            type="string",
            description="Title of the plot.",
            required=False,
            default=""
        ),
        Parameter(
            name="x_label",
            type="string",
            description="Label for the X-axis.",
            required=False,
            default=""
        ),
        Parameter(
            name="y_label",
            type="string",
            description="Label for the Y-axis.",
            required=False,
            default=""
        ),
        Parameter(
            name="save_path",
            type="string",
            description="Path to save the generated plot image.",
            required=False,
            default="plot.png"
        )
    ])
    
    def __call__(self, plot_type: str, x_data: List[float], y_data: List[float], 
                 title: str = "", x_label: str = "", y_label: str = "", save_path: str ="plot.png"):
        """
        Generates a plot using Matplotlib based on provided configuration.

        Parameters:
            plot_type (str): The type of the plot ('line', 'bar', 'scatter').
            x_data (List[float]): X-axis data for the plot.
            y_data (List[float]): Y-axis data for the plot.
            title (str): Title of the plot.
            x_label (str): Label for the X-axis.
            y_label (str): Label for the Y-axis.
            save_path (str): Path to save the generated plot image.

        Returns:
            str: Path where the plot image is saved.
        """

        plt.figure()

        if plot_type == "line":
            plt.plot(x_data, y_data)
        elif plot_type == "bar":
            plt.bar(x_data, y_data)
        elif plot_type == "scatter":
            plt.scatter(x_data, y_data)
        else:
            raise ValueError(f"Unsupported plot type: {plot_type}")

        if title:
            plt.title(title)
        if x_label:
            plt.xlabel(x_label)
        if y_label:
            plt.ylabel(y_label)

        plt.savefig(save_path)
        plt.close()

        return save_path
