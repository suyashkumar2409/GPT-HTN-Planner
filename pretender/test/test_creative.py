import unittest
from pretender.creative_assistant import extract_basic_pos, extract_pos_and_entities  # Import the function you want to test
import json

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

# Combine all the text fields into a single string
all_text = " ".join([str(value) for value in json_data.values() if isinstance(value, str)])

class TestExtract(unittest.TestCase):
    def test_extract_nouns(self):
        nouns = extract_basic_pos(all_text, "NOUN")
        expected_nouns = {"world", "Draconia", "land", "adventure", "heart", "kingdom", "cave", "lair", "dragon", "realm", "journey"}
        self.assertEqual(nouns, expected_nouns)

    def test_extract_verbs(self):
        verbs = extract_basic_pos(all_text, "VERB")
        expected_verbs = {"Welcome", "filled", "lies", "rumored", "be", "has", "been", "terrorizing", "have", "gathered", "slay", "bring", "is", "filled", "have", "emerging", "face", "save"}
        self.assertEqual(verbs, expected_verbs)

    def test_extract_pos_and_entities(self):
        # Convert the JSON data to a JSON-formatted string
        json_text = json.dumps(json_data, ensure_ascii=False)

        # Call the extraction function
        nouns, verbs, proper_nouns = extract_pos_and_entities(json_text)

        # Define the expected results based on the JSON data
        expected_nouns = {"world", "Draconia", "land", "adventure", "heart", "kingdom", "cave", "lair", "dragon", "realm", "journey"}
        expected_verbs = {"Welcome", "filled", "lies", "rumored", "be", "has", "been", "terrorizing", "have", "gathered", "slay", "bring", "is", "filled", "have", "emerging", "face", "save"}
        expected_proper_nouns = {"Draconia", "Drakon the Terrible", "Faldir", "Grimbold Stonehammer", "Elara Nightshade"}

        # Check if the extracted sets match the expected sets
        self.assertEqual(nouns, expected_nouns)
        self.assertEqual(verbs, expected_verbs)
        self.assertEqual(proper_nouns, expected_proper_nouns)


if __name__ == "__main__":
    unittest.main()
