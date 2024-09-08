from pydantic import BaseModel, Field


class SimpleResultRequestSchema(BaseModel):
    task_done: bool = Field(True)
