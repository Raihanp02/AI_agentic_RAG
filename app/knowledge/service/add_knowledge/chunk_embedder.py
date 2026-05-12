from transformers import AutoTokenizer, AutoModel
from langchain_openai import OpenAIEmbeddings
import torch

class HuggingFaceTextEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed(self, text: str):

        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Use the mean of the token embeddings as the sentence embedding
        embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()
        return embeddings.numpy()
    
class LangChainOpenAI:
    def __init__(self, model_name: str):
        self.model = OpenAIEmbeddings()