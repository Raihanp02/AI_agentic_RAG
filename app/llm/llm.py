from langchain_openai import ChatOpenAI

class LangchainLLM:
    def __init__(self, model_name="gpt-4o-mini", temperature=0.7):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        def invoke(self, prompt):
            return self.llm.invoke(prompt)
