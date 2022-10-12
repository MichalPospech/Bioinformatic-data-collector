import pandas as pd
import abc
import typing as T
from dataclasses import dataclass
from common import SparqlEntity
from .query_generator import QueryContext, SubQueryContext
import lib.sparql_query as SQ


class SingleQueryExecutor(abc.ABC):

    @abc.abstractmethod
    def execute(self, query: SQ.SelectQuery, url: str) -> pd.DataFrame:
        pass


@dataclass
class SubQueryExecution:
    context: SubQueryContext

    def execute(self, data: T.Dict[SparqlEntity, T.List[str]],
                mapping: T.Dict[SparqlEntity,
                                SQ.Variable], prefixes: T.List[SQ.Prefix],
                executor: SingleQueryExecutor) -> pd.DataFrame:
        query = self._generate_query(data, mapping, prefixes)
        data = executor.execute(query, self.context.url)
        return data

    def _generate_query(self, data: T.Dict[SparqlEntity, T.List[str]],
                        mapping: T.Dict[SparqlEntity, SQ.Variable],
                        prefixes: T.List[SQ.Prefix]) -> SQ.SelectQuery:
        return SQ.SelectQuery(
            prefixes, [mapping[e] for e in self.context.entities],
            SQ.SimpleGraphPattern(
                [
                    SQ.InlineData(mapping[dep], data[dep])
                    for dep in self.context.inputs
                ] +
                [r.recipe_constructor(mapping) for r in self.context.recipes] +
                [f.recipe_constructor(mapping) for f in self.context.filters]))


@dataclass
class QueryExecutor:
    context: QueryContext

    def execute(self, executor: SingleQueryExecutor):
        value_mapping = {v.name: k for k, v in self.context.mapping}
        df = pd.DataFrame()
        values_dict = {}
        for execution in self.context.query_executions:
            tmp_df = execution.execute(values_dict, executor)
            df = df.merge(tmp_df, on=None, how="inner", suffixes=("", None))
            for column in tmp_df:
                values_dict[value_mapping[column]] = list(
                    tmp_df[column].unique())

        return df
