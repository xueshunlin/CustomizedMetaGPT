from metagpt.tools.tool_registry import register_tool

@register_tool(tags=["notebook_python_converter"], include_functions=["conversion"])
class NotebookPythonConverter:
   
    def conversion(self, notebook_path: str) -> list:
        """
        Convert a Jupyter notebook to Python script, the output is ready to use.

        Args:
            notebook_path (str): Path to the Jupyter notebook file.

        Returns:
            list: The content of the Python script.
        """

        import nbformat
        from nbconvert import PythonExporter

        # Read the notebook file
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)

        # Convert the notebook to Python script
        exporter = PythonExporter()
        script, _ = exporter.from_notebook_node(nb)
        
        return script

if __name__ == "__main__":
    notebook_path = "/Users/xueshunlin/Desktop/GitHub/CustomizedMetaGPT/notebook_workspace_2/example-data-analysis.ipynb"
    converter = NotebookPythonConverter()
    content = converter.read_notebook(notebook_path)
    print(content)