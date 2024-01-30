''' This file contains the code for the Creative Assistant. 
The purpose of this assistant is to come up with the creating the imaginary environment
in which the players can play pretend.
Given a theme, it is responsible for functions like
 * creating the world, including,
    * the locations in the world that the players can visit
    * the objects in the world that the players can interact with
    * the action that the players can take in the world
 * creating the characters 
 * coming up with a quest for the players to do
 * coming up with a story for the players to follow
It will be interfacing with the ChatGPT model using simpleaichat to do these functions, 
remembering the creative facts it invents like locations, objects, actions, characters, 
quest, and story, and using these facts instead of creating new ones whenever possible.
'''

import orjson
import spacy
import json

from pretender.assistants import CreativeAssistant






###########
### Test Creative Assistant
###########





# Your JSON data
json_data = {
  "description": "Welcome to the treacherous world of Draconia, a land filled with danger and adventure. In the heart of the kingdom lies a massive cave, rumored to be the lair of a powerful dragon. The dragon, known as Drakon the Terrible, has been terrorizing the countryside, burning villages and hoarding treasure. Brave adventurers from all corners of the realm have gathered to slay the dragon and bring peace back to the land. The cave is a labyrinth of tunnels and chambers, filled with deadly traps and fierce monsters. Only the strongest and most cunning heroes have a chance of surviving the treacherous journey and emerging victorious. Do you have what it takes to face the dragon and save Draconia?",
  "quest": "Slay the dragon Drakon the Terrible and bring peace back to the kingdom of Draconia.",
  "success_metric": "The players will know they have succeeded when they have defeated Drakon the Terrible and the land is no longer plagued by his terror.",
  "init": "The adventure begins in the bustling town of Faldir, where the players meet a group of fellow adventurers who have also set their sights on slaying the dragon.",
  "name": "Draconia",
  "pcs": [
    {
      "name": "Grimbold Stonehammer",
      "race": "Dwarf",
      "job": "Warrior",
      "story": "Grimbold comes from a long line of proud dwarven warriors. He seeks to prove himself and cement his family's legacy by slaying the dragon.",
      "feats": [
        "Master of the Axe: Grimbold wields a mighty battle axe with unmatched skill, dealing devastating blows to his enemies.",
        "Dwarven Resilience: Grimbold's dwarven heritage grants him incredible resilience, allowing him to withstand even the fiercest of dragon attacks."
      ],
      "equipment": [
        "Battle Axe",
        "Dwarven Plate Armor",
        "Shield",
        "Health Potion"
      ]
    },
    {
      "name": "Elara Nightshade",
      "race": "Elf",
      "job": "Ranger",
      "story": "Elara is an expert tracker and archer, trained in the ancient arts of the elven rangers. She has dedicated her life to protecting the realm from creatures like the dragon.",
      "feats": [
        "Deadly Aim: Elara's precise aim allows her to strike vital spots with her arrows, dealing extra damage.",
        "Nature's Blessing: Elara has a deep connection with nature, allowing her to communicate with animals and gain their assistance in battle."
      ],
      "equipment": [
        "Longbow",
        "Leather Armor",
        "Dagger",
        "Potion of Invisibility"
      ]
    }
  ]
}


# Define a function to check if a verb is active
def is_active_verb(token):
    return (
        token.pos_ == "VERB" and
        "pass" not in [child.dep_ for child in token.children]
    )

# Define functions to extract unique parts of speech from text
def extract_basic_pos(text, pos_type):
    doc = nlp(text)
    pos_set = set()

    for token in doc:
        if token.pos_ == pos_type:
            pos_set.add(token.text)

    return pos_set

# def extract_pos_and_entities(text):
#     doc = nlp(text)
#     nouns = set()
#     verbs = set()
#     proper_nouns = set()
#     multi_token_entities = set()

#     for token in doc:
#         if token.pos_ == "NOUN" and token.text not in multi_token_entities:
#             nouns.add(token.text)
#         elif is_active_verb(token) and token.text not in multi_token_entities:
#             verbs.add(token.text)
#         if token.ent_type_ == "PERSON" or token.ent_type_ == "ORG" or token.ent_type_ == "GPE":
#             proper_noun = token.text
#             # Check if the current token is part of a multi-token entity
#             while token.i + 1 < len(doc) and doc[token.i + 1].ent_iob_ == 'I':
#                 token = doc[token.i + 1]
#                 proper_noun += " " + token.text
#             proper_nouns.add(proper_noun)
#             multi_token_entities.update(proper_noun.split())  # Exclude individual words from NOUN and VERB

#     return nouns, verbs, proper_nouns

# Define a recursive function to extract unique nouns, active verbs, and named entities from text
def extract_pos_and_entities(text):
    doc = nlp(text)
    nouns = set()
    verbs = set()
    proper_nouns = set()

    for token in doc:
        if token.pos_ == "NOUN":
            nouns.add(token.text)
        elif is_active_verb(token):
            verbs.add(token.text)
        if token.ent_type_ in {"PERSON", "ORG", "GPE"}:
            proper_noun = token.text
            # Check if the current token is part of a multi-token entity
            while token.i + 1 < len(doc) and doc[token.i + 1].ent_iob_ == 'I':
                token = doc[token.i + 1]
                proper_noun += " " + token.text
            proper_nouns.add(proper_noun)

    for child in doc:
        # if child.text.lower() == "description":
        #     continue  # Skip the "description" field to avoid processing it again

        if isinstance(text, str):
            try:
                child_json = json.loads(text)
                for key, value in child_json.items():
                    if isinstance(value, str):
                        nested_nouns, nested_verbs, nested_proper_nouns = extract_pos_and_entities(value)
                        nouns.update(nested_nouns)
                        verbs.update(nested_verbs)
                        proper_nouns.update(nested_proper_nouns)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, str):
                                nested_nouns, nested_verbs, nested_proper_nouns = extract_pos_and_entities(item)
                                nouns.update(nested_nouns)
                                verbs.update(nested_verbs)
                                proper_nouns.update(nested_proper_nouns)
            except json.JSONDecodeError:
                pass

    return nouns, verbs, proper_nouns


def extract_pos_json(json_dict, pos_type=None):
    """
    :return: the nouns, verbs, and proper nouns in the JSON data
    """
    json_text = json.dumps(json_dict, ensure_ascii=False)
    # all_text = " ".join([str(value) for value in json_dict.values() if isinstance(value, str)])
    # return extract_pos_and_entities(all_text, pos_type)
    return extract_pos_and_entities(json_text)





# ### World Creation example
# theme = 'slaying a dragon in a cave'

# ## example categories
# classify_categories = """
# {Play with my friends, Attack with my sword, Find a weapon}
# """

# ## example examples
# classify_examples = """
# [Query] 'After school I will '
# [Category] Play with my friends

# [Query] 'To slay a dragon I need to'
# [Category] Attack with my sword

# [Query] 'Once my sword is lost I must'
# [Category] Find a weapon
# """


theme = 'slaying a dragon in a cave'
bot = CreativeAssistant(theme=theme)
world_structure = bot.create_world()

# context = dict(examples=classify_examples, categories=classify_categories)
# predicted_category = bot.classify_text(text=classify_query_text, 
#                                        examples=classify_examples,
#                                        categories=classify_categories)

print("world_structure: ",orjson.dumps(world_structure, option=orjson.OPT_INDENT_2).decode())
print(input())


# nouns, verbs, proper_nouns = extract_pos_json(json_data)

# # Print the unique nouns, verbs, and proper nouns
# print("Unique Nouns:")
# for noun in nouns:
#     print(noun)

# print("\nUnique Verbs:")
# for verb in verbs:
#     print(verb)

# print("\nUnique Proper Nouns:")
# for proper_noun in proper_nouns:
#     print(proper_noun)





# Extract nouns and verbs from the combined text
# nouns = extract_pos_json(json_data, "NOUN")
# verbs = extract_pos_json(json_data, "VERB")

# # Print the unique nouns and verbs
# print("Unique Nouns:")
# for noun in nouns:
#     print(noun)

# print("\nUnique Verbs:")
# for verb in verbs:
#     print(verb)
