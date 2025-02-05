# Import the base Action class from metagpt.actions module
from metagpt.actions import Action

class Speak(Action):
    """A class that enables AI agents to evaluate and debate about modularization work.
    
    This class is used in the evaluation workflow where multiple AI agents review and discuss
    the quality of code modularization. It allows agents to analyze each other's arguments
    and provide comprehensive evaluations based on predefined standards.
    """

    PROMPT_TEMPLATE: str = """
    ## BACKGROUND
    Suppose you are {name}, you are reviewing the modularization work produced by AI with {opponent_name}, and together you should evaluate the work in few standards.

    ## CONTEXT
    {context}

    ## YOUR TURN
    Now it's your turn, you should firstly review your opponent's idea(if any), then closely state your position, defend your arguments, and attack your opponent's arguments(if any).
    
    closely look at the code and give the work a fair explicit evaluation related with each of the following standards:
    
    {evaluation_standards}

    It is better if you could include more details in your evaluation, and also please think in different perspectives against to your opponent's arguments if any, to make your evaluation more comprehensive. DO NOT copy your opponent's arguments, tryto make your evaluation more unique and more persuasive.
    """

    async def run(self, context: str, name: str, opponent_name: str, evaluation_standards: list[str]) -> str:
        """Execute the speaking action to evaluate modularization work.

        Args:
            context (str): The context containing code and previous evaluations
            name (str): Name of the current speaking agent
            opponent_name (str): Name of the opponent agent
            evaluation_standards (list[str]): List of standards to evaluate against

        Returns:
            str: The agent's evaluation and response to opponent's arguments
        """
        # Format the evaluation standards as a numbered list
        index=1
        '/n'.join([f"{index}. {standard}" for standard in evaluation_standards])
        
        # Format the prompt with provided context and parameters
        prompt = self.PROMPT_TEMPLATE.format(context=context, name=name, opponent_name=opponent_name, evaluation_standards=evaluation_standards)

        # Get response from the language model
        rsp = await self._aask(prompt)

        return rsp