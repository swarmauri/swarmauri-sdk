from swarmauri.tools.MatplotlibTool import MatplotlibTool

# Create a tool instance
tool = MatplotlibTool()

# Generate a line plot
result = tool(
    plot_type="line",
    x_data=[1, 2, 3],
    y_data=[4, 5, 6],
    title="Line Plot",
    x_label="X-axis",
    y_label="Y-axis",
    save_path="plot.png",
)
