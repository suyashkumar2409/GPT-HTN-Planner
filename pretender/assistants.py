''' This file contains the code for the LLM Base Assistant,
which planning assistant and creative assistant inherit from.
'''

from pretender.creative_assistant import extract_pos_json, schema_write_ttrpg_setting
from simpleaichat import AIChat
import orjson
from rich.console import Console
from getpass import getpass
import os

from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field

"""
2 ai:
 - LogicAI ("planner") (creative)
 - CreativeAI (real)


ai for answering "Does <this verb/precondition from the creative> correspond to anything from <this list of verb/precondition from the real>?"

tell real decomp ai that it is a robot

How to get real tree and imaginary tree to match up?
  1. Ground init suggested objects to real world objects
  2. Ask decomp ai both about imaginary

Need "Sensors" for preconditions and effects
 - need to find correspondence between Sensor (like proximity sensor) and that can "sense" a precondition/effect like "near"

For not groundable: how do you know if it is decomposable or not?

How to determine when to decompose creative? based on perceived time:
    - if LLM thinks it will take a long time (walk to cave, fight dragon), then decompose creatively
    - if LLM thinks it will take a short time (enter cave, a spell that was casted), then by rule autoassociate-with "Say" e.g. astro says "I casted a magic missile"
"""

current_dir = os.path.dirname(os.path.abspath(__file__))


class BaseAssistant(): #BaseModel):

    def __init__(self, llm=None, api_key=None, model=None, system_prompt=None, save_messages=False):
        """
        Initializes the assistant.
        :param llm: The LLM function to call. If None, will use simpleAIchat AIChat() with ChatGPT3.5.
        :param kwargs: Arguments to pass to the LLM model.
        :param api_key: The API key to use for the LLM model. If None, will prompt the user for it.
        :param model: The model to use for the LLM model. If None, will use gpt-3.5-turbo-0613.
        :param system_prompt: The system prompt to use for the LLM model. If None, will use the default.
        """
        if llm is None or isinstance(llm,AIChat):
            if api_key is None:
                file_path = os.path.join(current_dir, 'utils/api_key.txt')
                if os.path.getsize(file_path) == 0:
                    api_key = input("Please enter your API key: ")
                else:
                    with open(file_path, 'r') as f:
                        fin = f.read()  
                    api_key = fin
            if model is None:
                model='gpt-3.5-turbo-0613'
            # if system_prompt is None:
            #     system_prompt=='You are a helpful story planner'
            self.llm=AIChat(
                model=model,
                console=False,
                api_key=api_key,
                system_prompt=system_prompt,
                save_messages=save_messages)
        else:
            self.llm = llm()

    def get_prompt(self, template, query, context_dict=None):
        """
        Gets the prompt string from the template, 
        and formats that template with a query and context dictionary of other values.
        all templates use 'query' as the main question being asked the LLM
        and 'examples' for the list of examples of the LLM template.
        """
        if template[-3:] == 'txt':
            with open(template,'r') as f:
                template_str = f.read()
        else:
            template_str = template
        if context_dict is None:
            context_dict = {}
        prompt_string = self.effify(ftext=template_str,
                               query=query, 
                               context_dict=context_dict) #, **values_dict)
        return prompt_string

    def effify(self, ftext, query, context_dict=None):
        """converges a fstring and its arguments into a string. 
        query separate to require it"""
        if context_dict is None:
            context_dict = {}
        context_dict['query'] = query
        if 'examples' not in context_dict:
            context_dict['examples'] = None
        return ftext.format(**context_dict)



class CreativeAssistant(BaseAssistant):
    def __init__(self, theme, llm=None, api_key=None, model=None, system_prompt=None, save_messages=True):
        """
        Initializes the creative assistant.
        :param theme: The theme of the creative assistant.
        """
        if system_prompt is None:
            system_prompt = """You are a world-renowned game designer games including role-playing games (RPGs).
                            Your job will be to come up with a fun, kid-friendly imaginary adventure.

                            Rules you MUST follow:
                            - if asked about facts, you must be as concise as possible.
                            - if asked to be descriptive, feel free to be verbose and creative.
                            - You must be creative and unique.
                            - All names you create must be kid-friendly and easy to pronounce.
                            - You must stay on theme.
                            - remembering the creative facts it invents like locations, objects,
                              actions, tasks, characters, quest, and story, and using these facts instead
                              of creating new ones whenever possible.
                            """
        super().__init__(llm=llm,
                         api_key=api_key,
                         model=model,
                         system_prompt=system_prompt,
                         save_messages=save_messages)
        self.theme = theme

    def create_world(self):
        """
        Creates the world.
        :return: The world description.
        """
        self.response_structured = self.llm(self.theme, output_schema=schema_write_ttrpg_setting)
        self.nouns, self.verbs, self.proper_nouns = extract_pos_json(self.response_structured)
        return self.response_structured



class PlannerAssistant(BaseAssistant): #BaseModel):

    def __init__(self, llm=None, api_key=None, model=None, system_prompt=None, save_messages=False):
        if system_prompt is None:
            system_prompt='''
                You are a Planning Assistant. 
                You are going to be tasked with decomposing high level tasks into subtasks, 
                by classifying tasks from a set of known categories of tasks,
                coming up with logical preconditions and effects
                and reasoning about whether tasks can logically follow each other.
                Your purpose is to help the HTN Planner find a logically reasonable plan 
                from Start to Goal, using known and objects, tasks, and actions as often as possible,
                but being creative when it is not possible.
                '''
        super().__init__(llm=llm,
                         api_key=api_key,
                         model=model,
                         system_prompt=system_prompt,
                         save_messages=save_messages)

    def classify_text(self, text, template_override=None, **context_dict):
        if template_override is None:
            template = 'templates/choice_template.txt'
        else:
            template = template_override
        prompt = self.get_prompt(template=template,
                                 query=text,
                                 context_dict=context_dict)
        # Your code here - interact with ChatGPT to predict the category.

        predicted_category = self.llm(prompt=prompt)
        return predicted_category

    def decompose(self, task, template_override=None, **context_dict):
        if template_override is None:
            template = 'templates/decompose_template.txt'
        else:
            template = template_override
        prompt = self.get_prompt(template=template,
                                 query=task,
                                 context_dict=context_dict)
        # Your code here - interact with ChatGPT to decompose the text.
        decomposed_text = self.llm(prompt=prompt)
        return decomposed_text

