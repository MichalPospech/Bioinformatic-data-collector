from ..query_generator import SparqlQueryBuilder, SingleRecipe
from . import config as UC
from .. import sparql_query as SQ
from enum import Enum
import typing as T
from ..common import SparqlEntity, Recipe
from .entities import UniprotEntity
from ..rhea.entities import RheaEntity
from .representation import UniprotFilters

# def single_recipe_triplet(source: Entity, predicate: str) -> SingleRecipe[Entity]:
#     return SingleRecipe(
#         source, lambda source_ent, target: SQ.Triplet(source_ent, predicate, target)
#     )


class UniprotQueryBuilder(SparqlQueryBuilder[UC.UniprotSearchConfig]):
    # recipes = {
    #     Entity.FULL_NAME: single_recipe_triplet(Entity.RECOMMENDED_NAME, "up:fullName"),
    #     Entity.PFAM: single_recipe_triplet(Entity.PROTEIN, "rdfs:seeAlso"),
    #     Entity.RECOMMENDED_NAME: single_recipe_triplet(
    #         Entity.PROTEIN, "up:recommendedName"
    #     ),
    #     Entity.PROTEIN_ID: SingleRecipe(
    #         Entity.PROTEIN,
    #         lambda source, target: SQ.BindExpression(
    #             target, [source], "substr(str({}), 33)"
    #         ),
    #     ),
    #     Entity.SEQUENCE_OBJECT: SingleRecipe(
    #         Entity.PROTEIN,
    #         lambda source, target: SQ.SimpleGraphPattern(
    #             [
    #                 SQ.Triplet(source, "up:sequence", target),
    #                 SQ.Triplet(target, "a", "up:Simple_Sequence"),
    #             ]
    #         ),
    #     ),
    #     Entity.SEQUENCE: single_recipe_triplet(Entity.SEQUENCE_OBJECT, "rdf:value"),
    #     Entity.ORGANISM: single_recipe_triplet(Entity.PROTEIN, "up:organism"),
    #     Entity.TAXON_FILTERING: single_recipe_triplet(
    #         Entity.ORGANISM, "^skos:narrowerTransitive+"
    #     ),
    #     Entity.SUPFAM: single_recipe_triplet(Entity.PROTEIN, "rdfs:seeAlso"),
    #     Entity.CATALYTIC_ACTIVITY: single_recipe_triplet(
    #         Entity.PROTEIN, "up:annotation/up:catalyticActivity"
    #     ),
    #     Entity.CATALYZED_REACTION: single_recipe_triplet(
    #         Entity.CATALYTIC_ACTIVITY, "up:catalyzedReaction"
    #     ),
    # }
    entity_mappings = {
        UC.Feature.NAME: UniprotEntity.FULL_NAME,
        UC.Feature.PROTEIN: UniprotEntity.PROTEIN,
        UC.Feature.PROTEIN_ID: UniprotEntity.PROTEIN_ID,
        UC.Feature.SEQUENCE: UniprotEntity.SEQUENCE,
        UC.Feature.REACTION: RheaEntity.REACTION,
    }

    root_entity = UniprotEntity.START

    def __init__(self, config: UC.UniprotSearchConfig) -> None:
        super().__init__(config, True)

    def _get_entities(self) -> T.List[SparqlEntity]:
        features = self.config.data_selector.columns
        entities = [self.entity_mappings[feature] for feature in features]
        return entities

    def _get_filtering_recipes(self) -> T.List[Recipe]:
        filters: T.List[Recipe] = []

        # if self.config.data_filter.pfams:
        #     patterns.append(
        #         SQ.InlineData(
        #             mappings[UniprotEntity.PFAM],
        #             [
        #                 f"<http://purl.uniprot.org/pfam/{pfam}>"
        #                 for pfam in self.config.data_filter.pfams
        #             ],
        #         )
        #     )
        # if self.config.data_filter.reviewed:
        #     patterns.append(
        #         SQ.Triplet(mappings[UniprotEntity.PROTEIN], "up:reviewed", "true")
        #     )
        if self.config.data_filter.taxa:
            filters.append(UniprotFilters.taxa_filter(self.config.data_filter.taxa))
        # if self.config.data_filter.supfams:
        # patterns.append(
        #     SQ.InlineData(
        #         mappings[UniprotEntity.SUPFAM],
        #         [
        #             f"<http://purl.uniprot.org/supfam/{supfam}>"
        #             for supfam in self.config.data_filter.supfams
        #         ],
        #     )
        # )
        return filters

    # def _get_filtering_patterns(
    #     self, mappings: T.Dict[SparqlEntity, SQ.Variable]
    # ) -> T.List[SQ.GraphPattern | SQ.Triplet]:
    #     patterns: T.List[SQ.GraphPattern | SQ.Triplet] = [
    #         SQ.Triplet(mappings[UniprotEntity.PROTEIN], "a", "up:Protein")
    #     ]
    #     if self.config.data_filter.pfams:
    #         patterns.append(
    #             SQ.InlineData(
    #                 mappings[UniprotEntity.PFAM],
    #                 [
    #                     f"<http://purl.uniprot.org/pfam/{pfam}>"
    #                     for pfam in self.config.data_filter.pfams
    #                 ],
    #             )
    #         )
    #     if self.config.data_filter.reviewed:
    #         patterns.append(
    #             SQ.Triplet(mappings[UniprotEntity.PROTEIN], "up:reviewed", "true")
    #         )
    #     if self.config.data_filter.taxa:
    #         patterns.append(
    #             SQ.InlineData(
    #                 mappings[UniprotEntity.TAXON_FILTERING],
    #                 [
    #                     f"<http://purl.uniprot.org/taxonomy/{taxon}>"
    #                     for taxon in self.config.data_filter.taxa
    #                 ],
    #             )
    #         )
    #     if self.config.data_filter.supfams:
    #         patterns.append(
    #             SQ.InlineData(
    #                 mappings[UniprotEntity.SUPFAM],
    #                 [
    #                     f"<http://purl.uniprot.org/supfam/{supfam}>"
    #                     for supfam in self.config.data_filter.supfams
    #                 ],
    #             )
    #         )
    #     return patterns
