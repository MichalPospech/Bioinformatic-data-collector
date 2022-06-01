from .entities import UniprotEntity
from ..rhea.entities import RheaEntity
from networkx import MultiDiGraph
from ..common import Recipe, Repository
import lib.sparql_query as SQ
import typing as T


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
                        d[UniprotEntity.PROTEIN],
                        [d[UniprotEntity.PROTEIN]],
                        "substr(str({}), 33)",
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
            lambda d: SQ.InlineData(
                d[UniprotEntity.TAXON_FILTERING],
                [f"<http://purl.uniprot.org/taxonomy/{taxon}>" for taxon in taxa],
            ),
        )
