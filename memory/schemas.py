from pydantic import BaseModel, Field


class UserMemory(BaseModel):
    category: str = Field(
        description="""
        Category of the memory.
        Examples: preference, project, skill, goal, background.
        """
    )

    content: str = Field(
        description="""
        A concise, self-contained statement about the user.
        """
    )

    importance: int = Field(
        ge=1,
        le=10,
        description="How important this memory is to retain."
    )