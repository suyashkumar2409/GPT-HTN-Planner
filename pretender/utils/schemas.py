from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field

## Schema Classes
class schema_player_character(BaseModel):
    name: str = Field(description="Character name")
    race: str = Field(description="Character race")
    job: str = Field(description="Character class/job")
    story: str = Field(description="Three-sentence character history")
    feats: List[str] = Field(description="Character feats")
    equipment: List[str] = Field(description="Character equipment")


class schema_tasks(BaseModel):
    name: str = Field(description="Action name")
    preconditions: str = Field(description="List of facts that must be true to execute the action")
    effect: str = Field(description="Effects of taking the action")


class schema_write_ttrpg_setting(BaseModel):
    """Write a fun and innovative live-action role playing scenario"""
    description: str = Field(
        description="Detailed description of the setting"
    )
    primitive_tasks: List[schema_tasks] = Field(description="The list of basic action types that players can do in the imaginary world.")
    quest: str = Field(description="The challenge that the players are trying to overcome.")
    success_metric: str = Field(description="A concise, one-sentence explanation of how the players will know they have succeeded at their quest.")
    init: str = Field(description="Where does the adventure begin?")  ####### This should be determined by the real world
    name: str = Field(description="Name of the setting")
    pcs: List[schema_player_character] = Field(description="Player characters of the game")
