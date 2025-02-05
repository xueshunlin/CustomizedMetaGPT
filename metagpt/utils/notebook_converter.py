import os
import nbformat
from nbconvert import PythonExporter

class NotebookPythonConverter:

    def __init__(self, directory: str):
        self.directory = directory
        self.notebook_files = []

    def conversion(self) -> list:
        """
        Convert a Jupyter notebook to Python script, the output is ready to use.

        Args:
            notebook_path (str): Path to the Jupyter notebook file.

        Returns:
            list: The content of the Python script.
        """

        # Walk through the directory                                                                                                           
        for root, dirs, files in os.walk(self.directory):                                                                                      
            for file in files:                                                                                                                 
                if file.endswith('.ipynb'):                                                                                                    
                    self.notebook_files.append(os.path.join(root, file)) 

        for notebook_file in self.notebook_files:
                                                                                              
            python_script_path = notebook_file.replace('.ipynb', '.py')

            with open(notebook_file, 'r') as f:
                nb = nbformat.read(f, as_version=4)

            # Convert the notebook to Python script
            exporter = PythonExporter()
            script, _ = exporter.from_notebook_node(nb)

             # Write the Python script content to a new file                                                                                    
            with open(python_script_path, 'w') as script_file:                                                                                 
                script_file.writelines(script) 
            
            
