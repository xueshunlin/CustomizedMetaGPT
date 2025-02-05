from metagpt.actions import Action

class Score(Action):

    # Prompt template for calculating final score based on evaluation standards
    # Takes context parameter containing evaluation results
    PROMPT_TEMPLATE: str = """
    ## CONTEXT
    {context}

    ## ACTION
    According to the final evaluation, sum up the score in every evaluation standards and calculate the total score of the modularization work, responding the final value of score at the end of your answer.

    ## FORMAT
    Please give your final answer in this format: 'The total score of the modularization work is: xx'
    """

    # Run method to execute the scoring action
    # Takes evaluation context as input and returns final score
    async def run(self, context: str):
        # Format the prompt template with provided context
        prompt = self.PROMPT_TEMPLATE.format(context=context)

        # Send prompt to LLM and get response containing final score
        rsp = await self._aask(prompt)

        # Return the response containing total score
        return rsp