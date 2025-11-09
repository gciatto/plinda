import asyncio

from plinda.templates import *
from plinda.log import logger
from asyncio import Future
from typing import Iterable, Tuple as PyTuple, FrozenSet
from dataclasses import dataclass, field
from enum import Enum
import uuid


class TupleRepository:
    def all_tuples(self) -> Iterable[Tuple]:
        raise NotImplementedError

    def add(self, tuple: Tuple):
        raise NotImplementedError

    def find(self, template: Template, limit: int | None = None) -> Iterable[Tuple]:
        raise NotImplementedError

    def remove(self, template: Template, limit: int | None = 1) -> Iterable[Tuple]:
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def __len__(self):
        return sum(1 for _ in self.all_tuples())

    def __contains__(self, template: Template) -> bool:
        for _ in self.find(template, limit=1):
            return True
        return False

    def __getitem__(self, template: Template) -> Tuple:
        for tuple in self.find(template, limit=1):
            return tuple
        raise KeyError(f"No tuple matches the template: {template}")

    def __iter__(self):
        for tuple in self.all_tuples():
            yield tuple

    def __delitem__(self, template: Template):
        removed = list(self.remove(template, limit=1))
        if not removed:
            raise KeyError(f"No tuple matches the template: {template}")


class RequestKind(Enum):
    READ = "read"
    TAKE = "take"


@dataclass(frozen=True)
class Request:
    template: Template
    kind: RequestKind = field(default=RequestKind.READ)
    result: Future = field(
        default_factory=lambda: asyncio.get_event_loop().create_future(),
        hash=False,
        compare=False
    )
    id: str = field(default_factory=lambda: f"request-{uuid.uuid4()}")

    def complete(self, tuple: Tuple):
        if self.result.done():
            raise RuntimeError("Request is already completed")
        match = self.template.matches(tuple)
        if match:
            self.result.set_result(match)
        else:
            raise SystemError("The provided tuple does not match the request's template")


@dataclass(frozen=True)
class RequestMatch:
    requests: PyTuple[Request]

    def requests_of_kind(self, kind: RequestKind) -> Iterable[Request]:
        for request in self.requests:
            if request.kind == kind:
                yield request

    def __iter__(self):
        for kind in RequestKind:
            for request in self.requests_of_kind(kind):
                yield request

    def __len__(self):
        return len(self.requests)

    def __bool__(self):
        return len(self) > 0

    def __post_init__(self):
        setattr(self, "requests", tuple(self.requests))


class RequestRepository:
    def all_requests(self) -> Iterable[Request]:
        raise NotImplementedError

    def all_requests_for_tuple(self, tuple: Tuple) -> RequestMatch:
        raise NotImplementedError

    def add(self, request: Request):
        raise NotImplementedError

    def remove(self, request: Request):
        raise NotImplementedError

    def remove_all(self, request: Iterable[Request]):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def __contains__(self, tuple: Tuple) -> bool:
        for _ in self.all_requests_for_tuple(tuple):
            return True
        return False

    def __getitem__(self, tuple: Tuple) -> RequestMatch:
        return self.all_requests_for_tuple(tuple)

    def __len__(self):
        return sum(1 for _ in self.all_requests())

    def __iter__(self):
        for request in self.all_requests():
            yield request


class TupleSpace:
    def __init__(self, name: str, tuples: TupleRepository, requests: RequestRepository):
        self.__name = name
        self.__tuples = tuples
        self.__requests = requests

    def __log(self, template: str, *args, **kwargs):
        logger.info("[%s#%s] " + template, self.__class__.__name__, self.name, *args, **kwargs)

    @property
    def name(self):
        return self.__name

    async def get_all(self) -> Iterable[Tuple]:
        return self.__tuples.all_tuples()

    async def write(self, tuple: Tuple):
        self.__log("Writing: %s", tuple)
        suspended = self.__requests.all_requests_for_tuple(tuple)
        to_insert = True
        if suspended:
            to_resume = []
            for request in suspended.requests_of_kind(RequestKind.TAKE):
                if not request.result.done():
                    self.__log("Written %s is unlocking TAKE request %s", tuple, request.id)
                    request.complete(tuple)
                    to_resume.append(request)
                    to_insert = False
                    break
            if not to_resume:
                for request in suspended.requests_of_kind(RequestKind.READ):
                    if not request.result.done():
                        self.__log("Written %s is unlocking READ request %s", tuple, request.id)
                        request.complete(tuple)
                        to_resume.append(request)
            self.__requests.remove_all(to_resume)
        if to_insert:
            self.__tuples.add(tuple)
            self.__log("Actually storing in tuple space: %s", tuple)

    async def try_read(self, template: Template) -> Match | None:
        self.__log("Attempt to read something matching: %s", template)
        for tuple in self.__tuples.find(template):
            match = template.matches(tuple)
            if match:
                self.__log("Read tuple: %s", tuple)
                return match
        self.__log("No tuple matches the template: %s", template)
        return None

    async def read(self, template: Template) -> Match:
        if match := await self.try_read(template):
            return match
        request = Request(template=template, kind=RequestKind.READ)
        self.__requests.add(request)
        self.__log("Suspending: %s", request)
        return await request.result

    async def try_take(self, template: Template) -> Match | None:
        self.__log("Attempt to take something matching: %s", template)
        for tuple in self.__tuples.remove(template, limit=1):
            match = template.matches(tuple)
            assert match, "Removed tuple must match the template"
            self.__log("Took tuple: %s", tuple)
            return match
        self.__log("No tuple matches the template: %s", template)
        return None

    async def take(self, template: Template) -> Match:
        if match := await self.try_take(template):
            return match
        request = Request(template=template, kind=RequestKind.TAKE)
        self.__requests.add(request)
        self.__log("Suspending: %s", request)
        return await request.result


logger.info("plinda.spaces module loaded.")