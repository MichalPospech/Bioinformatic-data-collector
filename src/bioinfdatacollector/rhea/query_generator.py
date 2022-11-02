from ..query_generator import SparqlQueryBuilder
from . import config as C
import typing as T
from ..common import SparqlEntity, Recipe, Repository
from .entities import RheaEntity
from ..rhea.entities import RheaEntity
from .representation import RheaFilters


class RheaQueryBuilder(SparqlQueryBuilder[C.RheaSearchConfig]):
    entity_mappings = {
        C.Feature.REACTION: RheaEntity.REACTION,
        C.Feature.REACTION_PARTICIPANT: RheaEntity.COMPOUND,
        C.Feature.REACTION_SIDE: RheaEntity.REACTION_SIDE_ORDER,
        C.Feature.CHEBI: RheaEntity.CHEBI,
        C.Feature.SMILES: RheaEntity.SMILES,
    }

    entity_type = RheaEntity
    root_entity = RheaEntity.START
    repository = Repository.RHEA

    def __init__(self, config: C.RheaSearchConfig) -> None:
        super().__init__(config, True)

    def _get_entities(self) -> T.List[SparqlEntity]:
        features = self.config.data_selector.columns
        entities = [self.entity_mappings[feature] for feature in features]
        return entities

    def _get_filtering_recipes(self) -> T.List[Recipe]:
        filters: T.List[Recipe] = []
        if self.config.data_filter.reactions:
            filters.append(
                RheaFilters.reaction_filter(self.config.data_filter.reactions)
            )
        return filters
