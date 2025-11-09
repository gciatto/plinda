import unittest
import re
from plinda import RegexTemplate, TextTuple, JsonTuple, RegexMatch, Tuple


class TestRegexTemplate(unittest.TestCase):
    value = re.compile(r'hello (\w+)')
    template = RegexTemplate(value)
    matching_tuple = TextTuple("hello world")
    non_matching_tuple = TextTuple("goodbye world")
    json_tuple = JsonTuple({"key": "hello kitty"})

    def test_getting_pattern(self):
        self.assertEqual(self.template.pattern, self.value)

    def test_can_match_with_type(self):
        self.assertTrue(RegexTemplate.can_match(TextTuple))
        self.assertTrue(RegexTemplate.can_match(JsonTuple))
        self.assertFalse(RegexTemplate.can_match(Tuple))
        self.assertFalse(RegexTemplate.can_match(str))

    def test_can_match_with_instance(self):
        self.assertTrue(RegexTemplate.can_match(self.matching_tuple))
        self.assertTrue(RegexTemplate.can_match(self.non_matching_tuple))
        self.assertTrue(RegexTemplate.can_match(self.json_tuple))

    def test_pattern_equality(self):
        self.assertEqual(self.template, RegexTemplate(self.value))

    def test_hashing(self):
        s = set()
        s.add(self.template)
        s.add(RegexTemplate(self.value))
        self.assertEqual(len(s), 1)  # Both should be considered the same in the set

    def test_successful_match(self):
        match = self.template.matches(self.matching_tuple)
        self.assertIsNotNone(match)
        self.assertIsInstance(match, RegexMatch)
        self.assertEqual(match.tuple, self.matching_tuple)
        self.assertEqual(match.template, self.template)
        self.assertEqual(match[0], "hello world")
        self.assertEqual(match[1], "world")

    def test_unsuccessful_match(self):
        match = self.template.matches(self.non_matching_tuple)
        self.assertIsNone(match)

    def test_json_match(self):
        match = self.template.matches(self.json_tuple)
        self.assertIsNotNone(match)
        self.assertIsInstance(match, RegexMatch)
        self.assertEqual(match.tuple, self.json_tuple)
        self.assertEqual(match.template, self.template)
        self.assertEqual(match[0], "hello kitty")
        self.assertEqual(match[1], "kitty")


if __name__ == '__main__':
    unittest.main()
