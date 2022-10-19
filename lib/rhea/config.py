from dataclasses import dataclass
import typing as T
import dataclasses_json as DJ
from enum import Enum

URL = "https://sparql.rhea.org"


class Feature(Enum):
    REACTION = "Reaction"
    REACTION_PARTICIPANT = "ReactionParticipant"
    CHEBI = "Chebi"
    SMILES = "Smiles"


@DJ.dataclass_json(letter_case=DJ.LetterCase.CAMEL)
@dataclass
class RheaSearchFilter(DJ.DataClassJsonMixin):
    reactions: T.Optional[T.List[str]] = None


@DJ.dataclass_json(letter_case=DJ.LetterCase.CAMEL)
@dataclass
class RheaSelection(DJ.DataClassJsonMixin):
    columns: T.List[Feature]


@DJ.dataclass_json(letter_case=DJ.LetterCase.CAMEL)
@dataclass
class RheaSearchConfig(DJ.DataClassJsonMixin):
    data_selector: RheaSelection
    data_filter: RheaSearchFilter = RheaSearchFilter()
