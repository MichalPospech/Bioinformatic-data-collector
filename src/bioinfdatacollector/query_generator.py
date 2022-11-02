import abc
import bioinfdatacollector.sparql_query as SQ
import typing as T
from enum import Enum
from .common import SparqlEntity, Recipe, Repository
from .knowledge_base import knowledge_graphs
import networkx

TEntity = T.TypeVar("TEntity", bound=Enum)
TConfig = T.TypeVar("TConfig")


class SparqlQueryBuilder(abc.ABC, T.Generic[TConfig]):

    root_entity: SparqlEntity
    entity_type: type
    repository: Repository
    prefixes = [
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

    @abc.abstractmethod
    def _get_entities(self) -> T.List[TEntity]:
        pass

    def get_query(self) -> SQ.SelectQuery:
        filters = self._get_filtering_recipes()
        filtering_entities = [e for f in filters for e in f.required_entities]
        projected_entities = self._get_entities()
        graph = knowledge_graphs[self.repository]
        shortest_paths = networkx.algorithms.shortest_path(
            graph, source=self.root_entity
        )
        important_paths = {
            v: shortest_paths[v] for v in filtering_entities + projected_entities
        }
        edges = [
            (source, target, graph.get_edge_data(source, target, key=0))
            for path in important_paths.values()
            for (source, target) in zip(path, path[1:])
        ]
        knowledge_graph = networkx.DiGraph()
        knowledge_graph.add_edges_from(edges)

        entities = knowledge_graph.nodes()
        mapping = {e: SQ.Variable(str(e)) for e in entities}
        recipe_patterns = [
            knowledge_graph.get_edge_data(u, v)["recipe"].recipe_constructor(mapping)
            for (u, v) in networkx.algorithms.dfs_edges(
                knowledge_graph, self.root_entity
            )
        ]
        filter_patterns = [f.recipe_constructor(mapping) for f in filters]

        return SQ.SelectQuery(
            self.prefixes,
            [mapping[e] for e in projected_entities],
            SQ.SimpleGraphPattern(recipe_patterns + filter_patterns),
        )
