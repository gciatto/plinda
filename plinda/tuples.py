import uuid
import json
from plinda.log import logger


class Tuple:
    def __init__(self):
        self.__id = uuid.uuid4()

    @property
    def id(self):
        return f"tuple-{self.__id}"

    def _value(self):
        raise NotImplementedError("Subclasses must implement the '_value' method.")

    @property
    def value(self):
        return self._value()

    def value_equals(self, other: 'Tuple') -> bool:
        return self.value == other.value

    def __eq__(self, other):
        if not isinstance(other, Tuple):
            return False
        return self.id == other.id and self.value == other.value

    def __hash__(self):
        return hash((self.id, self.value))

    def __str__(self):
        return f"{type(self).__name__}(id={self.id}, value={self.value})"


class TextTuple(Tuple):
    def __init__(self, text: str):
        super().__init__()
        self.__text = text

    def _value(self):
        return self.__text

    @property
    def text(self):
        return self.__text


class JsonTuple(TextTuple):
    def __init__(self, data: dict | list | str | int | float | bool | None):
        super().__init__(json.dumps(data, sort_keys=True))
        self.__data = data

    def _value(self):
        return self.__data

    @property
    def data(self):
        return self.__data

    @classmethod
    def parse(cls, text: str) -> 'JsonTuple':
        data = json.loads(text)
        return cls(data)

    def __str__(self):
        return f"{type(self).__name__}(id={self.id}, value={self.text})"

    def __hash__(self):
        return hash((self.id, self.text))


logger.debug("plinda.tuples module loaded.")