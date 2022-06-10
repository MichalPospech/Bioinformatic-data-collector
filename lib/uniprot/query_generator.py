from ..query_generator import SparqlQueryBuilder
from . import config as UC
import typing as T
from ..common import SparqlEntity, Recipe, Repository
from .entities import UniprotEntity
from ..rhea.entities import RheaEntity
from .representation import UniprotFilters


class UniprotQueryBuilder(SparqlQueryBuilder[UC.UniprotSearchConfig]):
    entity_mappings = {
        UC.Feature.NAME: UniprotEntity.FULL_NAME,
        UC.Feature.PROTEIN: UniprotEntity.PROTEIN,
        UC.Feature.PROTEIN_ID: UniprotEntity.PROTEIN_ID,
        UC.Feature.SEQUENCE: UniprotEntity.SEQUENCE,
        UC.Feature.REACTION: RheaEntity.REACTION,
        UC.Feature.REACTION_PARTICIPANT: RheaEntity.COMPOUND
    }

    entity_type = UniprotEntity
    root_entity = UniprotEntity.START
    repository = Repository.UNIPROT

    def __init__(self, config: UC.UniprotSearchConfig) -> None:
        super().__init__(config, True)

    def _get_entities(self) -> T.List[SparqlEntity]:
        features = self.config.data_selector.columns
        entities = [self.entity_mappings[feature] for feature in features]
        return entities

    def _get_filtering_recipes(self) -> T.List[Recipe]:
        filters: T.List[Recipe] = []

        if self.config.data_filter.pfams:
            filters.append(
                UniprotFilters.pfam_filter(self.config.data_filter.pfams))
        if self.config.data_filter.reviewed:
            filters.append(
                UniprotFilters.reviewed_filter(
                    self.config.data_filter.reviewed))
        if self.config.data_filter.taxa:
            filters.append(
                UniprotFilters.taxa_filter(self.config.data_filter.taxa))
        if self.config.data_filter.supfams:
            filters.append(
                UniprotFilters.supfam_filter(self.config.data_filter.supfams))

        return filters
