import unittest
import json
from plinda import Tuple, TextTuple, JsonTuple


class AbstractTupleTest(unittest.TestCase):
    def test_tuples_have_ids(self):
        ids = set()
        for t in [self.t1, self.t2, self.t3]:
            self.assertIsNotNone(t.id)
            self.assertIsInstance(t.id, str)
            self.assertTrue(t.id.startswith("tuple-"))
            ids.add(t.id)
        self.assertEqual(len(ids), 3)  # All IDs should be unique

    def test_value_property(self):
        self.assertEqual(self.t1.value, self.value1)
        self.assertEqual(self.t2.value, self.value2)
        self.assertEqual(self.t3.value, self.value3)

    def test_value_equals(self):
        self.assertTrue(self.t1.value_equals(self.t2))
        self.assertFalse(self.t1.value_equals(self.t3))

    def test_equality(self):
        self.assertNotEqual(self.t1, self.t2)  # Different IDs
        self.assertNotEqual(self.t1, self.t3)
        self.assertNotEqual(self.t2, self.t3)
        self.assertEqual(self.t1, self.t1)  # Same object

    def test_hashing(self):
        s = set()
        s.add(self.t1)
        s.add(self.t2)
        s.add(self.t3)
        self.assertEqual(len(s), 3)  # All should be unique in the set

    def tuple_to_str(self, t: Tuple) -> str:
        return str(t)

    def test_str_representation(self):
        for t in [self.t1, self.t2, self.t3]:
            s = str(t)
            self.assertIn(type(t).__name__, s)
            self.assertIn(t.id, s)
            self.assertIn(self.tuple_to_str(t), s)


class TestTextTuples(AbstractTupleTest):
    value1 = "hello"
    t1 = TextTuple(value1)
    value2 = "hello"
    t2 = TextTuple(value2)
    value3 = "world"
    t3 = TextTuple(value3)

    def test_text_property(self):
        self.assertEqual(self.t1.text, "hello")
        self.assertEqual(self.t2.text, "hello")
        self.assertEqual(self.t3.text, "world")

    def test_text_is_same_as_value(self):
        self.assertIs(self.t1.text, self.t1.value)
        self.assertIs(self.t2.text, self.t2.value)
        self.assertIs(self.t3.text, self.t3.value)


class TestJsonTuples(AbstractTupleTest):
    value1 = {"key1": "value1"}
    t1 = JsonTuple(value1)
    value2 = {"key1": "value1"}
    t2 = JsonTuple(value2)
    value3 = {"key1": "value2"}
    t3 = JsonTuple(value3)

    def test_data_property(self):
        self.assertEqual(self.t1.data, {"key1": "value1"})
        self.assertEqual(self.t2.data, {"key1": "value1"})
        self.assertEqual(self.t3.data, {"key1": "value2"})

    def test_value_is_same_as_data(self):
        self.assertIs(self.t1.value, self.t1.data)
        self.assertIs(self.t2.value, self.t2.data)
        self.assertIs(self.t3.value, self.t3.data)

    def test_text_property(self):
        self.assertEqual(self.t1.text, json.dumps({"key1": "value1"}))
        self.assertEqual(self.t2.text, json.dumps({"key1": "value1"}))
        self.assertEqual(self.t3.text, json.dumps({"key1": "value2"}))

    def test_parse_method(self):
        json_text = '{"key": "value"}'
        parsed_tuple = JsonTuple.parse(json_text)
        self.assertIsInstance(parsed_tuple, JsonTuple)
        self.assertEqual(parsed_tuple.data, {"key": "value"})
        self.assertEqual(parsed_tuple.value, {"key": "value"})

    def tuple_to_str(self, t: Tuple) -> str:
        return json.dumps(t.value, sort_keys=True)


del AbstractTupleTest


if __name__ == '__main__':
    unittest.main()
