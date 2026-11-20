import unittest

from app.assistants.registry import list_assistants


class AssistantRegistryTests(unittest.TestCase):
    def test_v1_has_two_available_and_two_planned_assistants(self):
        assistants = list_assistants()
        self.assertEqual(
            [assistant.id for assistant in assistants],
            ["general", "coding", "research", "document"],
        )
        self.assertEqual(
            [assistant.id for assistant in assistants if assistant.available],
            ["general", "coding"],
        )

    def test_available_assistants_have_distinct_instructions(self):
        assistants = {assistant.id: assistant for assistant in list_assistants()}
        self.assertNotEqual(
            assistants["general"].instructions,
            assistants["coding"].instructions,
        )
        self.assertTrue(assistants["general"].capabilities)
        self.assertTrue(assistants["coding"].capabilities)


if __name__ == "__main__":
    unittest.main()
