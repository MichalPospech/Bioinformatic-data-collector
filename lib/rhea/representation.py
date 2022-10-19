from ..rhea.entities import RheaEntity
from networkx import MultiDiGraph
from ..common import Recipe, Repository, create_triplet_recipe, SparqlEntity
import lib.sparql_query as SQ
import typing as T


def create_rhea_triplet_recipe(
    in_ent: SparqlEntity, out_ent: SparqlEntity, predicate: str
) -> Recipe:
    return create_triplet_recipe(in_ent, out_ent, predicate, Repository.RHEA)


def create_rhea_triplet_edge(
    in_ent: SparqlEntity, out_ent: SparqlEntity, predicate: str
) -> T.Tuple[SparqlEntity, SparqlEntity, T.Dict[str, T.Any]]:
    return (
        in_ent,
        out_ent,
        {"recipe": create_rhea_triplet_recipe(in_ent, out_ent, predicate)},
    )


knowledge_graph = MultiDiGraph()
knowledge_graph.add_nodes_from(RheaEntity)
knowledge_graph.add_edges_from(
    [
        (
            RheaEntity.START,
            RheaEntity.REACTION,
            {
                "recipe": Recipe(
                    Repository.RHEA,
                    [RheaEntity.REACTION],
                    lambda d: SQ.Triplet(
                        d[RheaEntity.REACTION], "rdfs:subClassOf", "rh:Reaction"
                    ),
                )
            },
        ),
        create_rhea_triplet_edge(
            RheaEntity.REACTION, RheaEntity.REACTION_SIDE, "rh:side"
        ),
        create_rhea_triplet_edge(
            RheaEntity.REACTION_SIDE, RheaEntity.PARTICIPANT, "rh:contains"
        ),
        create_rhea_triplet_edge(
            RheaEntity.PARTICIPANT, RheaEntity.COMPOUND, "rh:compound"
        ),
        create_rhea_triplet_edge(
            RheaEntity.COMPOUND,
            RheaEntity.CHEBI,
            "(rh:reactivePart?/rh:chebi)|rh:underlyingChebi",
        ),
        create_rhea_triplet_edge(RheaEntity.CHEBI, RheaEntity.SMILES, "chebi:smiles"),
    ]
)


class RheaFilters:
    @classmethod
    def reaction_filter(cls, reaction_ids: T.List[str]) -> Recipe:
        return Recipe(
            Repository.UNIPROT,
            [RheaEntity.REACTION],
            lambda d: SQ.InlineData(
                d[RheaEntity.REACTION],
                map(lambda reaction_id: f"<http://rdf.rhea-db.org/{reaction_id}>"),
            ),
        )
