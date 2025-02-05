from metagpt.actions import Action

# Action class for summarizing evaluation discussions and providing final scores
# This is part of the evaluation workflow in the CustomizedMetaGPT project
class Summarize(Action):
    """Action: Summarize evaluation discussions and provide final scoring decisions"""

    # Template for generating the summary prompt
    # The prompt instructs an AI agent to review scoring discussions between team members
    # and provide final scores for each evaluation criterion
    PROMPT_TEMPLATE: str = """
    ## BACKGROUND
    Suppose you are {name}, you are review the modularization work scoring discussion of your team mate, "Bob" and "Alice".

    ## CONTEXT
    {context}

    ## YOUR TURN
    Now it's your turn, please summarize the discussion and give each scoring standard your final answer.

    according to the level of satisfication of each scoring standard, giving the score of 0 or 1.
    """

    async def run(self, context: str, name: str):
        """
        Execute the summarization action
        
        Args:
            context (str): The discussion content between evaluators to be summarized
            name (str): The name of the AI agent doing the summarization
        
        Returns:
            str: A summary of the discussion with final scores for each criterion
        """
        # Format the prompt with the provided context and name
        prompt = self.PROMPT_TEMPLATE.format(context=context, name=name)
        
        # Use the LLM to generate a summary and scoring response
        rsp = await self._aask(prompt)

        return rsp