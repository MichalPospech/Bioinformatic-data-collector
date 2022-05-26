import typing as T
import itertools as IT
import abc

import os


class Variable:
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return f"?{self.name}"


TripletMemeber = Variable | str


class Triplet:
    # triplet: T.Sequence[TripletMemeber]

    def __init__(self, subj: TripletMemeber, pred: TripletMemeber,
                 obj: TripletMemeber):
        self.triplet = [subj, pred, obj]

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return " ".join(map(str, self.triplet)) + " ."

    def get_lines(self) -> T.Iterable[str]:
        return [self.get_pretty_text()]


class GraphPattern:

    @abc.abstractmethod
    def get_pretty_text(self) -> str:
        pass

    @abc.abstractmethod
    def get_lines(self) -> T.Iterable[str]:
        pass


class SimpleGraphPattern(GraphPattern):
    # patterns: T.Sequence[GraphPattern | Triplet]

    def __init__(self, patterns: T.Sequence[GraphPattern | Triplet]):
        self.patterns = patterns

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        lines = map(
            lambda l: " " * 4 + l,
            IT.chain.from_iterable(map(lambda p: p.get_lines(),
                                       self.patterns)))
        yield "{"
        for l in lines:
            yield l
        yield "}"


class OptionalGraphPattern(GraphPattern):
    # graph_pattern: GraphPattern

    def __init__(self, graph_pattern: GraphPattern):
        self.graph_pattern = graph_pattern

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        lines = list(self.graph_pattern.get_lines())
        yield f"OPTIONAL {lines[0]}"
        for l in lines[1:]:
            yield l


class InlineData(GraphPattern):
    # variable: Variable
    # values: T.Sequence[str]

    def __init__(self, variable: Variable, values: T.Sequence[str]):
        self.values = values
        self.variable = variable

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        yield f"VALUES {self.variable.get_pretty_text()} {{"
        for value in self.values:
            yield " " * 4 + value
        yield "}"


class ServiceGraphPattern(GraphPattern):
    # graph_pattern: GraphPattern
    # service: str

    def __init__(self, service: str, pattern: GraphPattern):
        self.service = service
        self.graph_pattern = pattern

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        lines = list(self.graph_pattern.get_lines())
        yield f"SERVICE {self.service} {lines[0]}"
        for l in lines[1:]:
            yield l


class BindExpression(GraphPattern):
    # out_var: Variable
    # in_vars: T.Sequence[Variable]
    # expression: str

    def __init__(self, out_var: Variable, in_vars: T.Sequence[Variable],
                 expr: str):
        self.out_var = out_var
        self.in_vars = in_vars
        self.expression = expr

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        substituted_expression = str.format(self.expression,
                                            *list(map(str, self.in_vars)))
        return str.format(
            f"BIND(({substituted_expression}) AS {str(self.out_var)})")

    def get_lines(self) -> T.Iterable[str]:
        return [self.get_pretty_text()]


class Prefix:
    # prefix: str
    # iri_ref: str

    def __init__(self, prefix: str, iri_ref: str):
        self.prefix = prefix
        self.iri_ref = iri_ref

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return f"PREFIX {self.prefix}: {self.iri_ref}"

    def get_lines(self) -> T.Iterable[str]:
        return [self.get_pretty_text()]


class SelectQuery:
    # prefixes: T.Sequence[Prefix]
    # variables: T.Sequence[Variable]
    # graph_pattern: GraphPattern

    def __init__(self,
                 prefixes: T.Sequence[Prefix],
                 variables: T.Sequence[Variable],
                 graph_pattern: GraphPattern,
                 distinct: bool = True):
        self.prefixes = prefixes
        self.variables = variables
        self.graph_pattern = graph_pattern
        self.distinct = distinct

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        prefixes = map(lambda p: p.get_pretty_text(), self.prefixes)
        variables = f"SELECT {'DISTINCT' if self.distinct else ''} {' '.join(map(lambda v: v.get_pretty_text(), self.variables))}"
        graph_pattern_lines = list(self.graph_pattern.get_lines())
        for prefix in prefixes:
            yield prefix
        yield variables
        yield f"WHERE {graph_pattern_lines[0]}"
        for graph_pattern_line in graph_pattern_lines[1:]:
            yield graph_pattern_line
