from enum import Enum, unique, auto
from dataclasses import dataclass
import typing as T
import lib.sparql_query as SQ


@unique
class SparqlEntity(Enum):
    def __str__(self) -> str:
        return str(self.value)

    pass


class Repository(Enum):
    UNIPROT = auto()
    RHEA = auto()


@dataclass
class Recipe:
    repository: Repository
    required_entities: T.List[SparqlEntity]
    recipe_constructor: T.Callable[
        [T.Dict[SparqlEntity, SQ.Variable]], T.Union[SQ.Triplet, SQ.GraphPattern]
    ]
