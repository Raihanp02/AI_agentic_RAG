from pydantic import BaseModel

class AgentRequest(BaseModel):
    messages: str