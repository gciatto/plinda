from plinda.tuples import *
from plinda.log import logger
from typing import Callable
import re


class Match:
    def __init__(self, tuple: Tuple, template: 'Template'):
        self.__tuple = tuple
        self.__template = template

    def __getitem__(self, item):
        return getattr(self, item)

    @property
    def tuple(self):
        return self.__tuple

    @property
    def template(self):
        return self.__template

    def __eq__(self, other):
        return self.tuple == other.tuple and self.template == other.template

    def __hash__(self):
        return hash((self.tuple, self.template))

    def __str__(self):
        return f"Match(tuple={self.tuple}, template={self.template})"


class Template:
    def __init__(self, value):
        assert value is not None
        self.__value = value

    @property
    def value(self):
        return self.__value

    @classmethod
    def can_match(cls, tuple_or_type: Tuple | type) -> bool:
        return True

    def matches(self, tuple: Tuple) -> Match | None:
        return None

    def _successful_match(self, tuple: Tuple) -> Match:
        return Match(tuple, self)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __hash__(self):
        return hash((type(self), self.value))

    def __str__(self):
        return f"{type(self).__name__}(value={self.value})"


class AnyTemplate(Template):
    def __init__(self, predicate: Callable[[Tuple], bool] = lambda _: None):
        super().__init__(predicate)

    def matches(self, tuple: Tuple) -> Match | None:
        result = self.value(tuple)
        if not isinstance(result, bool):
            raise TypeError("Predicate must return a bool.")
        if result:
            return self._successful_match(tuple)
        return None


class RegexMatch(Match):
    def __init__(self, tuple: TextTuple, template: 'RegexTemplate', match: re.Match):
        assert isinstance(tuple, TextTuple)
        assert isinstance(template, RegexTemplate)
        super().__init__(tuple, template)
        self.__match = match

    def __getitem__(self, item):
        return self.__match.group(item)

    @property
    def match(self):
        return self.__match

    def __eq__(self, other):
        return super().__eq__(other) and self.match == other.match

    def __hash__(self):
        return hash((super().__hash__(), self.match))

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"RegexMatch(tuple={self.tuple.text}, template={self.template.pattern}, match={self.match})"


class RegexTemplate(Template):
    def __init__(self, pattern: re.Pattern | str):
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        super().__init__(pattern)

    @property
    def pattern(self) -> re.Pattern:
        return self.value

    @classmethod
    def can_match(cls, tuple_or_type: Tuple | type) -> bool:
        if isinstance(tuple_or_type, type):
            return issubclass(tuple_or_type, TextTuple)
        return isinstance(tuple_or_type, TextTuple)

    # noinspection PyMethodOverriding
    def _successful_match(self, tuple: TextTuple, match: re.Match) -> RegexMatch:
        return RegexMatch(tuple, self, match)

    def matches(self, tuple: Tuple) -> RegexMatch | None:
        if not self.can_match(tuple):
            return None
        text = tuple.text  # type: ignore
        for match in self.pattern.finditer(text):
            # noinspection PyTypeChecker
            return self._successful_match(tuple, match)
        return None


logger.info("plinda.templates module loaded.")