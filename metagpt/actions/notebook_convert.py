from typing import Optional

from metagpt.actions import Action, ActionOutput
import os
import nbformat
from nbconvert import PythonExporter
from pathlib import Path
# from const import SCRIPTS_FILE_REPO


class NotebookConvert(Action):
    """Action class responsible for converting Jupyter notebooks to Python scripts.
    This is a crucial first step in the modularization process, preparing notebook code
    for further analysis and restructuring."""

    name: str = "NotebookConvert"
    i_context: Optional[str] = None  # Optional context information for the conversion

    @property
    def config(self):
        """Access the configuration from the context.
        Returns:
            Configuration object containing project settings
        """
        return self.context.config
    
    async def run(self, with_messages, **kwargs):
        """Converts all Jupyter notebooks in the project directory to Python scripts.
        
        This method:
        1. Recursively finds all .ipynb files in the project directory
        2. Converts each notebook to a Python script while preserving code content
        3. Saves the converted scripts for further processing
        
        Args:
            with_messages: Messages to process (unused in this action)
            **kwargs: Additional keyword arguments
            
        Returns:
            ActionOutput containing the conversion results
        """
        # Store paths of all found notebook files
        notebook_files = []
        project_path = self.config.project_path

        # Recursively walk through the project directory to find all .ipynb files                                                                                                           
        for root, dirs, files in os.walk(project_path):                                                                      
            for file in files:                                                                                                                 
                if file.endswith('.ipynb'):                                                                                                    
                    notebook_files.append(os.path.join(root, file)) 

        # Process each notebook file
        for notebook_file in notebook_files:
            # Create Python script filename by replacing .ipynb extension                                                                                              
            file_name = Path(notebook_file).name.replace('.ipynb', '.py')

            # Read the notebook file using nbformat
            with open(notebook_file, 'r') as f:
                nb = nbformat.read(f, as_version=4)

            # Convert notebook to Python script using nbconvert
            exporter = PythonExporter()
            script, _ = exporter.from_notebook_node(nb)

            # Save the converted script using the project's script repository
            await self.repo.scripts.save(filename=file_name, content=script)