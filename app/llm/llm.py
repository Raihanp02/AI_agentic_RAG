from langchain_openai import ChatOpenAI
from core.config import settings

class LangchainLLM:
    def __init__(self, model_name="gpt-4o-mini", temperature=0.7):
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        
    def invoke(self, prompt):
        return self.llm.invoke(prompt)
        
class OpenRouterLLM:
    def __init__(
            self, 
            model_name=settings.OPENROUTER_MODEL, 
            api_key=settings.OPENROUTER_API_KEY, 
            base_url=settings.OPENROUTER_BASE_URL
    ):
        self.llm = ChatOpenAI(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
        )

    def invoke(self, prompt):
        return self.llm.invoke(prompt)
