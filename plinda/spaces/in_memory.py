from plinda.log import logger
from plinda.spaces import *
from threading import RLock
from builtins import tuple as pytuple


class InMemoryTupleRepository(TupleRepository):
    def __init__(self, *tuples: Tuple):
        self.__tuples = set(tuples)
        self.__lock = RLock()

    def all_tuples(self) -> Iterable[Tuple]:
        with self.__lock:
            tuples = pytuple(self.__tuples)
        return tuples

    def add(self, tuple: Tuple):
        with self.__lock:
            self.__tuples.add(tuple)

    def find(self, template: Template, limit: int | None = None) -> Iterable[Tuple]:
        result = []
        with self.__lock:
            if limit is None or limit <= 0:
                limit = len(self.__tuples)
            for tuple in self.__tuples:
                match = template.matches(tuple)
                if match:
                    result.append(tuple)
        return result

    def remove(self, template: Template, limit: int | None = 1) -> Iterable[Tuple]:
        to_remove = []
        with self.__lock:
            for tuple in self.find(template, limit):
                to_remove.append(tuple)
            for tuple in to_remove:
                self.__tuples.remove(tuple)
        return to_remove

    def clear(self):
        with self.__lock:
            self.__tuples.clear()

    def __len__(self):
        with self.__lock:
            return len(self.__tuples)

    def __str__(self):
        return f"{InMemoryTupleRepository.__name__}({', '.join(str(t) for t in self.__tuples)})"


class InMemoryRequestRepository(RequestRepository):
    def __init__(self, *requests: Request):
        self.__requests = list(requests)
        self.__lock = RLock()

    def all_requests(self) -> Iterable[Request]:
        with self.__lock:
            requests = pytuple(self.__requests)
        return requests

    def all_requests_for_tuple(self, tuple: Tuple) -> RequestMatch:
        matches = []
        with self.__lock:
            for request in self.__requests:
                match = request.template.matches(tuple)
                if match:
                    matches.append(request)
        return RequestMatch(matches)

    def add(self, request: Request):
        with self.__lock:
            self.__requests.append(request)

    def remove(self, request: Request):
        with self.__lock:
            self.__requests.remove(request)

    def remove_all(self, request: Iterable[Request]):
        with self.__lock:
            for req in request:
                self.__requests.remove(req)

    def clear(self):
        with self.__lock:
            self.__requests.clear()

    def __contains__(self, tuple: Tuple) -> bool:
        return super().__contains__(tuple)

    def __getitem__(self, tuple: Tuple) -> RequestMatch:
        return super().__getitem__(tuple)

    def __len__(self):
        with self.__lock:
            return len(self.__requests)

    def __str__(self):
        return f"{InMemoryRequestRepository.__name__}({', '.join(str(r) for r in self.__requests)})"


class InMemoryTupleSpace(TupleSpace):
    def __init__(self, name: str, *tuples: Tuple):
        tuples = InMemoryTupleRepository(*tuples)
        requests = InMemoryRequestRepository()
        super().__init__(name, tuples, requests)


logger.info("plinda.spaces.in_memory module loaded.")
