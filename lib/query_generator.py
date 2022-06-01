import abc
import lib.sparql_query as SQ
import typing as T
from enum import Enum
from dataclasses import dataclass
from .common import SparqlEntity, Recipe
from .knowledge_graph import graph as knowledge_graph
from networkx.algorithms import shortest_path
import networkx

TEntity = T.TypeVar("TEntity", bound=Enum)
TConfig = T.TypeVar("TConfig")


@dataclass
class SingleRecipe(T.Generic[TEntity]):
    source: TEntity
    query_builder: T.Callable[[SQ.Variable, SQ.Variable], SQ.GraphPattern | SQ.Triplet]


class SparqlQueryBuilder(abc.ABC, T.Generic[TConfig]):

    root_entity: SparqlEntity
    prefixes: [
        SQ.Prefix("up", "<http://purl.uniprot.org/core/>"),
        SQ.Prefix("rdfs", "<http://www.w3.org/2000/01/rdf-schema#>"),
        SQ.Prefix("rdf", "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>"),
        SQ.Prefix("skos", "<http://www.w3.org/2004/02/skos/core#>"),
        SQ.Prefix("chebi", "<http://purl.obolibrary.org/obo/chebi/>"),
        SQ.Prefix("rh", "<http://rdf.rhea-db.org/>"),
    ]

    def __init__(self, config: TConfig, distinct: bool):
        self.config = config
        self.distinct = distinct

    @abc.abstractmethod
    def _get_filtering_recipes(self) -> T.List[Recipe]:
        pass

    def _get_variable_mappings(self) -> T.Dict[TEntity, SQ.Variable]:
        pass

    @abc.abstractmethod
    def _get_entities(self) -> T.List[TEntity]:
        pass

    def get_query(self) -> SQ.SelectQuery:
        filters = self._get_filtering_recipes()
        filtering_entities = [e for f in filters for e in f.required_entities]
        projected_entities = self._get_entities()
        shortest_paths = shortest_path(knowledge_graph, source=self.root_entity)
        important_paths = {
            v: shortest_paths[v] for v in filtering_entities + projected_entities
        }
        edges = [
            (source, target, knowledge_graph.get_edge_data(source, target, key=0))
            for path in important_paths.values()
            for (source, target) in zip(path, path[1:])
        ]
        graph = networkx.DiGraph()
        graph.add_edges_from(edges)

        print(graph)
