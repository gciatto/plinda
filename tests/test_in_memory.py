from unittest import IsolatedAsyncioTestCase
from plinda import *


class TestInMemoryTupleSpace(IsolatedAsyncioTestCase):
    ts_empty = InMemoryTupleSpace("test-empty")
    tuple = TextTuple("hello world")
    ts_with_initial_tuples = InMemoryTupleSpace("test-initial", tuple)
    template = RegexTemplate(r"hello (\w+)")

    def test_name(self):
        self.assertEqual(self.ts_empty.name, "test-empty")
        self.assertEqual(self.ts_with_initial_tuples.name, "test-initial")

    async def test_is_empty(self):
        for _ in await self.ts_empty.get_all():
            self.fail("TupleSpace should be empty")

    async def test_is_not_empty(self):
        initial_content = {await self.ts_with_initial_tuples.get_all()}
        self.assertEqual({self.tuple}, initial_content)

    async def test_adding_tuples(self):
        await self.ts_empty.write(self.tuple)
        all_tuples = {await self.ts_empty.get_all()}
        self.assertEqual({self.tuple}, all_tuples)

    async def test_successful_try_read(self):
        match = await self.ts_with_initial_tuples.try_read(self.template)
        self.assertIsNotNone(match)
        self.assertIsInstance(match, RegexMatch)
        self.assertEqual(match[1], "world")
        await self.test_is_not_empty()
