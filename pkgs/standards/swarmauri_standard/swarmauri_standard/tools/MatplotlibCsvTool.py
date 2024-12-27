from swarmauri_core.typing import SubclassUnion

# standard/tools/concrete/MatplotlibCsvTool.py
import pandas as pd
import matplotlib.pyplot as plt
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter
import base64


class MatplotlibCsvTool(ToolBase):
    type: Literal["MatplotlibCsvTool"] = "MatplotlibCsvTool"
    name: str = Field(
        "MatplotlibCsvTool",
        description="Tool to generate plots from CSV data using Matplotlib.",
    )
    description: str = Field(
        "This tool reads data from a CSV file and generates a plot using Matplotlib.",
        description="Description of the MatplotlibCsvTool",
    )

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="csv_file",
                type="string",
                description="The path to the CSV file containing the data.",
                required=True,
            ),
            Parameter(
                name="x_column",
                type="string",
                description="The name of the column to use for the x-axis.",
                required=True,
            ),
            Parameter(
                name="y_column",
                type="string",
                description="The name of the column to use for the y-axis.",
                required=True,
            ),
            Parameter(
                name="output_file",
                type="string",
                description="The filename where the plot will be saved.",
                required=True,
            ),
        ]
    )

    def __call__(
        self, csv_file: str, x_column: str, y_column: str, output_file: str
    ) -> Dict[str, str]:
        # Read data from CSV
        data = pd.read_csv(csv_file)

        # Check if columns exist in the DataFrame
        if x_column not in data.columns or y_column not in data.columns:
            raise ValueError(
                f"Columns {x_column} and/or {y_column} not found in the CSV file."
            )

        # Generate plot
        plt.figure(figsize=(10, 6))
        plt.plot(data[x_column], data[y_column], marker="o")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        plt.title(f"{y_column} vs {x_column}")
        plt.grid(True)
        plt.savefig(output_file)
        plt.close()
        print(f"Plot generated and saved to {output_file}")
        # Encode the plot image as base64
        with open(output_file, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        return {"img_path": output_file, "img_base64": encoded_image, "data": []}


SubclassUnion.update(
    baseclass=ToolBase, type_name="MatplotlibCsvTool", obj=MatplotlibCsvTool
)
