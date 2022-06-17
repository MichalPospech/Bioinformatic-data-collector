from .entities import UniprotEntity
from ..rhea.entities import RheaEntity
from networkx import MultiDiGraph
from ..common import Recipe, Repository, create_triplet_recipe, SparqlEntity
import lib.sparql_query as SQ
import typing as T


def create_uniprot_triplet_recipe(
    in_ent: SparqlEntity, out_ent: SparqlEntity, predicate: str
) -> Recipe:
    return create_triplet_recipe(in_ent, out_ent, predicate, Repository.UNIPROT)


def create_uniprot_triplet_edege(
    in_ent: SparqlEntity, out_ent: SparqlEntity, predicate: str
) -> T.Tuple[SparqlEntity, SparqlEntity, T.Dict[str, T.Any]]:
    return (
        in_ent,
        out_ent,
        {"recipe": create_uniprot_triplet_recipe(in_ent, out_ent, predicate)},
    )


knowledge_graph = MultiDiGraph()
knowledge_graph.add_nodes_from(UniprotEntity)
knowledge_graph.add_node(RheaEntity.REACTION)
knowledge_graph.add_edges_from(
    [
        (
            UniprotEntity.START,
            UniprotEntity.PROTEIN,
            {
                "recipe": Recipe(
                    Repository.UNIPROT,
                    [UniprotEntity.PROTEIN],
                    lambda d: SQ.Triplet(d[UniprotEntity.PROTEIN], "a", "up:Protein"),
                )
            },
        ),
        (
            UniprotEntity.PROTEIN,
            UniprotEntity.PROTEIN_ID,
            {
                "recipe": Recipe(
                    Repository.UNIPROT,
                    [UniprotEntity.PROTEIN, UniprotEntity.PROTEIN_ID],
                    lambda d: SQ.BindExpression(
                        d[UniprotEntity.PROTEIN_ID],
                        [d[UniprotEntity.PROTEIN]],
                        "substr(str({}), 33)",
                    ),
                )
            },
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.PROTEIN, UniprotEntity.ORGANISM, "up:organism"
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.ORGANISM,
            UniprotEntity.TAXON_FILTERING,
            "^skos:narrowerTransitive+",
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.PROTEIN,
            UniprotEntity.CATALYTIC_ACTIVITY,
            "up:annotation/up:catalyticActivity",
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.CATALYTIC_ACTIVITY,
            RheaEntity.REACTION,
            "up:catalyzedReaction",
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.PROTEIN, UniprotEntity.RECOMMENDED_NAME, "up:recommendedName"
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.RECOMMENDED_NAME, UniprotEntity.FULL_NAME, "up:fullName"
        ),
        (
            UniprotEntity.PROTEIN,
            UniprotEntity.SEQUENCE_OBJECT,
            {
                "recipe": Recipe(
                    Repository.UNIPROT,
                    [UniprotEntity.PROTEIN, UniprotEntity.SEQUENCE_OBJECT],
                    lambda d: SQ.SimpleGraphPattern(
                        [
                            SQ.Triplet(
                                d[UniprotEntity.PROTEIN],
                                "up:sequence",
                                d[UniprotEntity.SEQUENCE_OBJECT],
                            ),
                            SQ.Triplet(
                                d[UniprotEntity.SEQUENCE_OBJECT],
                                "a",
                                "up:Simple_Sequence",
                            ),
                        ]
                    ),
                )
            },
        ),
        create_uniprot_triplet_edege(
            UniprotEntity.SEQUENCE_OBJECT, UniprotEntity.SEQUENCE, "rdf:value"
        ),
        (
            UniprotEntity.PROTEIN,
            UniprotEntity.PFAM,
            {
                "recipe": Recipe(
                    Repository.UNIPROT,
                    [UniprotEntity.PROTEIN, UniprotEntity.PFAM],
                    lambda d: SQ.SimpleGraphPattern(
                        [
                            SQ.Triplet(
                                d[UniprotEntity.PROTEIN],
                                "rdfs:seeAlso",
                                d[UniprotEntity.PFAM],
                            ),
                            SQ.Triplet(
                                d[UniprotEntity.PFAM],
                                "up:database",
                                "<http://purl.uniprot.org/database/Pfam>",
                            ),
                        ]
                    ),
                )
            },
        ),
        (
            UniprotEntity.PROTEIN,
            UniprotEntity.SUPFAM,
            {
                "recipe": Recipe(
                    Repository.UNIPROT,
                    [UniprotEntity.PROTEIN, UniprotEntity.SUPFAM],
                    lambda d: SQ.SimpleGraphPattern(
                        [
                            SQ.Triplet(
                                d[UniprotEntity.PROTEIN],
                                "rdfs:seeAlso",
                                d[UniprotEntity.SUPFAM],
                            ),
                            SQ.Triplet(
                                d[UniprotEntity.SUPFAM],
                                "up:database",
                                "<http://purl.uniprot.org/database/SUPFAM>",
                            ),
                        ]
                    ),
                )
            },
        ),
    ]
)


class UniprotFilters:
    @classmethod
    def taxa_filter(cls, taxa: T.List[str]) -> Recipe:
        return Recipe(
            Repository.UNIPROT,
            [UniprotEntity.TAXON_FILTERING],
            lambda d: SQ.FilterExpression(
                [d[UniprotEntity.TAXON_FILTERING]] * len(taxa),
                " || ".join(
                    map(
                        lambda taxon: f"{{}} = <http://purl.uniprot.org/taxonomy/{taxon}>",
                        taxa,
                    )
                ),
            ),
        )

    @classmethod
    def pfam_filter(cls, pfams: T.List[str]) -> Recipe:
        return Recipe(
            Repository.UNIPROT,
            [UniprotEntity.PFAM],
            lambda d: SQ.FilterExpression(
                [d[UniprotEntity.PFAM]] * len(pfams),
                " || ".join(
                    map(
                        lambda pfam: f"{{}} = <http://purl.uniprot.org/pfam/{pfam}>",
                        pfams,
                    )
                ),
            ),
        )

    @classmethod
    def supfam_filter(cls, supfams: T.List[str]) -> Recipe:
        return Recipe(
            Repository.UNIPROT,
            [UniprotEntity.SUPFAM],
            lambda d: SQ.FilterExpression(
                [d[UniprotEntity.SUPFAM]] * len(supfams),
                " || ".join(
                    map(
                        lambda supfam: f"{{}} = <http://purl.uniprot.org/supfams/{supfam}>",
                        supfams,
                    )
                ),
            ),
        )

    @classmethod
    def reviewed_filter(cls, reviewed: bool) -> Recipe:
        return Recipe(
            Repository.UNIPROT,
            [UniprotEntity.PROTEIN],
            lambda d: SQ.Triplet(
                d[UniprotEntity.PROTEIN], "up:reviewed", "true" if reviewed else "false"
            ),
        )
