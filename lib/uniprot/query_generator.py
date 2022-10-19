from ..query_generator import SparqlQueryBuilder
from . import config as C
import typing as T
from ..common import SparqlEntity, Recipe, Repository
from .entities import UniprotEntity
from ..rhea.entities import RheaEntity
from .representation import UniprotFilters


class UniprotQueryBuilder(SparqlQueryBuilder[C.UniprotSearchConfig]):
    entity_mappings = {
        C.Feature.NAME: UniprotEntity.FULL_NAME,
        C.Feature.PROTEIN: UniprotEntity.PROTEIN,
        C.Feature.PROTEIN_ID: UniprotEntity.PROTEIN_ID,
        C.Feature.SEQUENCE: UniprotEntity.SEQUENCE,
        C.Feature.REACTION: RheaEntity.REACTION,
    }

    entity_type = UniprotEntity
    root_entity = UniprotEntity.START
    repository = Repository.UNIPROT

    def __init__(self, config: C.UniprotSearchConfig) -> None:
        super().__init__(config, True)

    def _get_entities(self) -> T.List[SparqlEntity]:
        features = self.config.data_selector.columns
        entities = [self.entity_mappings[feature] for feature in features]
        return entities

    def _get_filtering_recipes(self) -> T.List[Recipe]:
        filters: T.List[Recipe] = []

        if self.config.data_filter.pfams:
            filters.append(UniprotFilters.pfam_filter(self.config.data_filter.pfams))
        if self.config.data_filter.reviewed:
            filters.append(
                UniprotFilters.reviewed_filter(self.config.data_filter.reviewed)
            )
        if self.config.data_filter.taxa:
            filters.append(UniprotFilters.taxa_filter(self.config.data_filter.taxa))
        if self.config.data_filter.supfams:
            filters.append(
                UniprotFilters.supfam_filter(self.config.data_filter.supfams)
            )

        return filters
