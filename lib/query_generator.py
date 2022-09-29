import abc
import lib.sparql_query as SQ
import typing as T
from enum import Enum
from dataclasses import dataclass
from .common import SparqlEntity, Recipe, Repository
from .knowledge_base import graph, urls, type_mappings
from networkx.algorithms import shortest_path
import networkx
from networkx.algorithms.dag import lexicographical_topological_sort
import itertools
import functools

TEntity = T.TypeVar("TEntity", bound=Enum)
TConfig = T.TypeVar("TConfig")


@dataclass
class QueryContext:
    repository: Repository
    inputs: T.List[TEntity]
    entities: T.List[TEntity]
    filters: T.List[Recipe]


@dataclass
class SingleRecipe(T.Generic[TEntity]):
    source: TEntity
    query_builder: T.Callable[[SQ.Variable, SQ.Variable],
                              SQ.GraphPattern | SQ.Triplet]


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
        shortest_paths = shortest_path(graph, source=self.root_entity)
        filters = self._get_filtering_recipes()
        filtering_entities = [e for f in filters for e in f.required_entities]
        projected_entities = self._get_entities()
        important_paths = {
            v: shortest_paths[v]
            for v in filtering_entities + projected_entities
        }
        edges = [(source, target, graph.get_edge_data(source, target, key=0))
                 for path in important_paths.values()
                 for (source, target) in zip(path, path[1:])]

        knowledge_graph = networkx.DiGraph()
        knowledge_graph.add_edges_from(edges)
        recipes = [
            data["recipe"] for (s, t, data) in knowledge_graph.edges(data=True)
        ] + filters

        topo_order = list(
            lexicographical_topological_sort(knowledge_graph,
                                             lambda r: str(type(r))))

        def group_recipes(l, r):
            if len(l) == 0:
                return [(type(r), [r])]
            else:
                previous_t, previous_l = l[-1]
                if type(r) == previous_t:
                    l[-1] = (previous_t, previous_l + [r])
                else:
                    l.append((type(r), [r]))
                return l

        def create_context(t: T.Type, entities: T.List[TEntity]):
            entity_set = set(entities)
            context_recipes = [
                r for r in recipes if r.produced_entity in entity_set
            ]
            dependencies = [
                e for recipe in context_recipes
                for e in recipe.required_entities if e not in entity_set
            ]
            context_filters = [
                f for f in filters
                if len(entity_set.intersection(f.required_entities)) == len(
                    f.required_entities)
            ]
            return QueryContext(type_mappings[t], dependencies, entities,
                                context_filters)

        grouped_recipes = list(functools.reduce(group_recipes, topo_order, []))
        contexts = list(map(lambda x: create_context(*x), grouped_recipes))
        print(contexts)