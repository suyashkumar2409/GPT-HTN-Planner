''' This file contains the code for the LLM Planner Assistant. It is responsible for a variety of high level functions 
like decomposing high level tasks into subtasks, and low level functions like classifying tasks into one of many known tasks. 
It will be interfacing with the ChatGPT model using simpleaichat to do these functions. 
The purpose of this assistant is to help the HTN Planner find a logically reasonable plan from start to goal, 
using known and primitive actions as often as possible.
'''
from pretender.assistants import PlannerAssistant
import orjson



#########
### Test Planner Assistant
#########

bot = PlannerAssistant()

### Classify example
## example categories
classify_categories = """
{Play with my friends, Attack with my sword, Find a weapon}
"""

## example examples
classify_examples = """
[Query] 'After school I will '
[Category] Play with my friends

[Query] 'To slay a dragon I need to'
[Category] Attack with my sword

[Query] 'Once my sword is lost I must'
[Category] Find a weapon
"""

classify_query_text = "Now that I have eaten dinner I will"
context = dict(examples=classify_examples, categories=classify_categories)
predicted_category = bot.classify_text(text=classify_query_text, 
                                       examples=classify_examples,
                                       categories=classify_categories)
print("Predicted Category:", predicted_category)


### Test decompose
## example primitive tasks
decompose_primitive_tasks = """
{"Go to", "Look at", "Turn On", "Turn Off", "Pick Up","Wait for"}
"""

decompose_objects = {'Cup', 'Bear',  'Sink', 'Coffee grounds', 'Fridge1', 'Coffee Machine'}

## example examples
decompose_examples = None
decompose_query_text = "Make Coffee"
context = dict(primitive_tasks=decompose_primitive_tasks, 
               objects=decompose_objects)
decomp = bot.decompose(task=decompose_query_text, 
                       primitive_tasks=decompose_primitive_tasks, 
                       objects=decompose_objects)
print("Decomposition:", decomp)

