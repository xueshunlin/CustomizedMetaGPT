from metagpt.actions import Action

class Review(Action):
    """Action: Speak out aloud in a debate (quarrel)"""
    
    ### TODO: look back to the mateval codebase, check the original prompt for feedback
    PROMPT_TEMPLATE: str = """
    ## BACKGROUND
    Suppose you are {name}, you are reviewing the discussion between two people in the history about the modularization work done by AI.

    ## DEBATE HISTORY
    Previous rounds:
    {context}

    ## ACTION
    Please give your opinion on the discussion according to the conversation history, and provide some feedback to the debaters. Note that please do keep the discussion result of all evaluation standards as part of your review work.
    """

    async def run(self, context: str, name: str):

        prompt = self.PROMPT_TEMPLATE.format(context=context, name=name)

        rsp = await self._aask(prompt)

        return rsp