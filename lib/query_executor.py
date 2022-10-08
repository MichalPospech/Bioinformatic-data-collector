import pandas as pd
import abc
import typing as T
from dataclasses import dataclass
from common import SparqlEntity
from .query_generator import QueryContext
import lib.sparql_query as SQ


class SingleQueryExecutor(abc.ABC):

    @abc.abstractmethod
    def execute(self, query: SQ.SelectQuery, url: str) -> pd.DataFrame:
        pass


@dataclass
class QueryExecution:
    url: str
    context: QueryContext

    def execute(self, data: T.Dict[SparqlEntity, T.List[str]],
                executor: SingleQueryExecutor) -> pd.DataFrame:
        query = self._generate_query(data)
        data = executor.execute(query, self.url)
        return data

    def _generate_query(
            self, data: T.Dict[SparqlEntity, T.List[str]]) -> SQ.SelectQuery:
        return SQ.SelectQuery(self.context.prefixes, [self.context.], graph_pattern)


@dataclass
class QueryExecutor:
    query_executions: T.List[QueryExecution]
    mapping: T.Dict[str, SparqlEntity]

    def execute(self, executor: SingleQueryExecutor):
        df = pd.DataFrame()
        values_dict = {}
        for execution in self.query_executions:
            tmp_df = execution.execute(values_dict, executor)
            df = df.merge(tmp_df, on=None, how="inner", suffixes=("", None))
            for column in tmp_df:
                values_dict[self.mapping[column]] = list(
                    tmp_df[column].unique())

        return df
