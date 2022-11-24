from dataclasses import dataclass
import typing as T
import dataclasses_json as DJ
from enum import Enum

URL = "https://sparql.uniprot.org"


class Feature(Enum):
    PROTEIN = "Protein"
    PROTEIN_ID = "ProteinId"
    NAME = "Name"
    SEQUENCE = "Sequence"
    REACTION = "Reaction"
    KINGDOM = "Kingdom"
    SUPERKINGDOM = "Superkingdom"
    ORGANISM = "Organism"
    PFAM = "Pfam"


@DJ.dataclass_json(letter_case=DJ.LetterCase.CAMEL)
@dataclass
class UniprotSearchFilter(DJ.DataClassJsonMixin):
    pfams: T.Optional[T.List[str]] = None
    supfams: T.Optional[T.List[str]] = None
    reviewed: T.Optional[bool] = None
    taxa: T.Optional[T.List[str]] = None


@DJ.dataclass_json(letter_case=DJ.LetterCase.CAMEL)
@dataclass
class UniprotSelection(DJ.DataClassJsonMixin):
    columns: T.List[Feature]


@DJ.dataclass_json(letter_case=DJ.LetterCase.CAMEL)
@dataclass
class UniprotSearchConfig(DJ.DataClassJsonMixin):
    data_selector: UniprotSelection
    data_filter: UniprotSearchFilter = UniprotSearchFilter()
