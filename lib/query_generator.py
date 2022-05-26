import abc
from . import sparql_query as SQ
import typing as T
from enum import Enum
from dataclasses import dataclass

TEntity = T.TypeVar("TEntity", bound=Enum)
TConfig = T.TypeVar("TConfig")


@dataclass
class SingleRecipe(T.Generic[TEntity]):
    source: TEntity
    query_builder: T.Callable[[SQ.Variable, SQ.Variable],
                              SQ.GraphPattern | SQ.Triplet]


class SparqlQueryBuilder(abc.ABC, T.Generic[TEntity, TConfig]):
    recipes: T.Dict[TEntity, SingleRecipe[TEntity]]
    root_entity: TEntity
    prefixes: T.List[SQ.Prefix]

    def __init__(self, config: TConfig, distinct: bool):
        self.config = config
        self.distinct = distinct

    @abc.abstractmethod
    def _get_necessary_entities(self) -> T.List[TEntity]:
        pass

    def _get_variable_mappings(self) -> T.Dict[TEntity, SQ.Variable]:
        entites = self._get_necessary_entities()
        variable_mappings = {}
        while len(entites) > 0:
            entity = entites.pop()
            variable_mappings[entity] = SQ.Variable(str(entity))
            if entity == self.root_entity:
                continue
            recipe = self.recipes[entity]
            if (recipe.source not in variable_mappings):
                entites.append(recipe.source)
        return variable_mappings

    @abc.abstractmethod
    def _get_filtering_patterns(
        self, mappings: T.Dict[TEntity, SQ.Variable]
    ) -> T.List[SQ.GraphPattern | SQ.Triplet]:
        pass

    @abc.abstractmethod
    def _get_entities(self) -> T.List[TEntity]:
        pass

    def get_query(self) -> SQ.SelectQuery:
        mappings = self._get_variable_mappings()
        select_graph_patterns = []
        for entity in mappings:
            if entity == self.root_entity:
                continue
            recipe = self.recipes[entity]
            source = recipe.source
            graph_pattern = recipe.query_builder(mappings[source],
                                                 mappings[entity])
            select_graph_patterns.append(graph_pattern)
        filtering_patterns = self._get_filtering_patterns(mappings)
        prefixes = self.prefixes
        features = [mappings[entity] for entity in self._get_entities()]
        query = SQ.SelectQuery(prefixes,
                               features,
                               SQ.SimpleGraphPattern(filtering_patterns +
                                                     select_graph_patterns),
                               distinct=self.distinct)
        return query
