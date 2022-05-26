from ..query_generator import SparqlQueryBuilder, SingleRecipe
from . import config as UC
from .. import sparql_query as SQ
from enum import Enum
import typing as T


class Entity(Enum):

    def __str__(self) -> str:
        return str(self.value)

    PROTEIN = "protein"
    FULL_NAME = "full_name"
    RECOMMENDED_NAME = "recommended_name"
    PROTEIN_ID = "protein_id"
    PFAM = "pfam"
    SEQUENCE_OBJECT = "sequence_object"
    SEQUENCE = "sequence"
    ORGANISM = "organism"
    TAXON_FILTERING = "taxon_filtering"
    SUPFAM = "supfam"
    CATALYTIC_ACTIVITY = "catalytic_activity"
    CATALYZED_REACTION = "catalyzed_reaction"


def single_recipe_triplet(source: Entity,
                          predicate: str) -> SingleRecipe[Entity]:
    return SingleRecipe(
        source,
        lambda source_ent, target: SQ.Triplet(source_ent, predicate, target))


class UniprotQueryBuilder(SparqlQueryBuilder[Entity, UC.UniprotSearchConfig]):
    recipes = {
        Entity.FULL_NAME:
        single_recipe_triplet(Entity.RECOMMENDED_NAME, "up:fullName"),
        Entity.PFAM:
        single_recipe_triplet(Entity.PROTEIN, "rdfs:seeAlso"),
        Entity.RECOMMENDED_NAME:
        single_recipe_triplet(Entity.PROTEIN, "up:recommendedName"),
        Entity.PROTEIN_ID:
        SingleRecipe(
            Entity.PROTEIN, lambda source, target: SQ.BindExpression(
                target, [source], "substr(str({}), 33)")),
        Entity.SEQUENCE_OBJECT:
        SingleRecipe(
            Entity.PROTEIN, lambda source, target: SQ.SimpleGraphPattern([
                SQ.Triplet(source, "up:sequence", target),
                SQ.Triplet(target, "a", "up:Simple_Sequence")
            ])),
        Entity.SEQUENCE:
        single_recipe_triplet(Entity.SEQUENCE_OBJECT, "rdf:value"),
        Entity.ORGANISM:
        single_recipe_triplet(Entity.PROTEIN, "up:organism"),
        Entity.TAXON_FILTERING:
        single_recipe_triplet(Entity.ORGANISM, "^skos:narrowerTransitive+"),
        Entity.SUPFAM:
        single_recipe_triplet(Entity.PROTEIN, "rdfs:seeAlso"),
        Entity.CATALYTIC_ACTIVITY:
        single_recipe_triplet(Entity.PROTEIN,
                              "up:annotation/up:catalyticActivity"),
        Entity.CATALYZED_REACTION:
        single_recipe_triplet(Entity.CATALYTIC_ACTIVITY,
                              "up:catalyzedReaction"),
    }
    entity_mappings = {
        UC.Feature.NAME: Entity.FULL_NAME,
        UC.Feature.PROTEIN: Entity.PROTEIN,
        UC.Feature.PROTEIN_ID: Entity.PROTEIN_ID,
        UC.Feature.SEQUENCE: Entity.SEQUENCE,
        UC.Feature.REACTION: Entity.CATALYZED_REACTION
    }

    root_entity = Entity.PROTEIN

    prefixes = [
        SQ.Prefix("up", "<http://purl.uniprot.org/core/>"),
        SQ.Prefix("rdfs", "<http://www.w3.org/2000/01/rdf-schema#>"),
        SQ.Prefix("rdf", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>"),
        SQ.Prefix("skos", "<http://www.w3.org/2004/02/skos/core#>"),
        SQ.Prefix("chebi", "<http://purl.obolibrary.org/obo/chebi/>"),
        SQ.Prefix("rh", "<http://rdf.rhea-db.org/>")
    ]

    def __init__(self, config: UC.UniprotSearchConfig) -> None:
        super().__init__(config, True)

    def _get_entities(self) -> T.List[Entity]:
        features = self.config.data_selector.columns
        entities = [self.entity_mappings[feature] for feature in features]
        return entities

    def _get_filter_entities(self) -> T.List[Entity]:
        entities = [Entity.PROTEIN]
        if self.config.data_filter.pfams is not None:
            entities.append(Entity.PFAM)
        if self.config.data_filter.taxa is not None:
            entities.append(Entity.TAXON_FILTERING)
        if self.config.data_filter.supfams:
            entities.append(Entity.SUPFAM)
        return entities

    def _get_necessary_entities(self) -> T.List[Entity]:
        visible = self._get_entities()
        invisible = self._get_filter_entities()
        return list(set(visible + invisible))

    def _get_filtering_patterns(
        self, mappings: T.Dict[Entity, SQ.Variable]
    ) -> T.List[SQ.GraphPattern | SQ.Triplet]:
        patterns: T.List[SQ.GraphPattern | SQ.Triplet] = [
            SQ.Triplet(mappings[Entity.PROTEIN], "a", "up:Protein")
        ]
        if self.config.data_filter.pfams:
            patterns.append(
                SQ.InlineData(mappings[Entity.PFAM], [
                    f"<http://purl.uniprot.org/pfam/{pfam}>"
                    for pfam in self.config.data_filter.pfams
                ]))
        if self.config.data_filter.reviewed:
            patterns.append(
                SQ.Triplet(mappings[Entity.PROTEIN], "up:reviewed", "true"))
        if self.config.data_filter.taxa:
            patterns.append(
                SQ.InlineData(mappings[Entity.TAXON_FILTERING], [
                    f"<http://purl.uniprot.org/taxonomy/{taxon}>"
                    for taxon in self.config.data_filter.taxa
                ]))
        if self.config.data_filter.supfams:
            patterns.append(
                SQ.InlineData(mappings[Entity.SUPFAM], [
                    f"<http://purl.uniprot.org/SUPFAM/{supfam}>"
                    for supfam in self.config.data_filter.supfams
                ]))
        return patterns
