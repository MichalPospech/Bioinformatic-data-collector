import typing as T
import itertools as IT
import abc
import os
import functools as FT


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
    def __init__(self, subj: TripletMemeber, pred: TripletMemeber, obj: TripletMemeber):
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
    def __init__(self, patterns: T.Sequence[GraphPattern | Triplet]):
        self.patterns = patterns

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        lines = map(
            lambda l: " " * 4 + l,
            IT.chain.from_iterable(map(lambda p: p.get_lines(), self.patterns)),
        )
        yield "{"
        for l in lines:
            yield l
        yield "}"


class Union(GraphPattern):
    def __init__(self, patterns: T.Sequence[GraphPattern | Triplet]):
        self.patterns = patterns

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        return FT.reduce(
            lambda l, pattern: IT.chain(
                l, ["UNION"], [line for line in pattern.get_lines()]
            ),
            self.patterns[1:],
            self.patterns[0].get_lines(),
        )


class OptionalGraphPattern(GraphPattern):
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
    def __init__(self, variable: Variable, values: T.Sequence[str]):
        self.values = values
        self.variable = variable

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        yield "VALUES {} {{".format(self.variable.get_pretty_text())
        for v in self.values:
            yield 4 * " " + v
        yield "}"


class ServiceGraphPattern(GraphPattern):
    def __init__(self, service: str, pattern: GraphPattern):
        self.service = service
        self.graph_pattern = pattern

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        return os.linesep.join(self.get_lines())

    def get_lines(self) -> T.Iterable[str]:
        lines = list(self.graph_pattern.get_lines())
        yield f"SERVICE <{self.service}> {lines[0]}"
        for l in lines[1:]:
            yield l


class BindExpression(GraphPattern):
    def __init__(self, out_var: Variable, in_vars: T.Sequence[Variable], expr: str):
        self.out_var = out_var
        self.in_vars = in_vars
        self.expression = expr

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        substituted_expression = str.format(
            self.expression, *list(map(str, self.in_vars))
        )
        return str.format(f"BIND(({substituted_expression}) AS {str(self.out_var)})")

    def get_lines(self) -> T.Iterable[str]:
        return [self.get_pretty_text()]


class FilterExpression(GraphPattern):
    def __init__(self, in_vars: T.Sequence[Variable], expr: str):
        self.in_vars = in_vars
        self.expression = expr

    def __str__(self) -> str:
        return self.get_pretty_text()

    def get_pretty_text(self) -> str:
        substituted_expression = str.format(
            self.expression, *list(map(str, self.in_vars))
        )
        return str.format(f"FILTER( {substituted_expression} )")

    def get_lines(self) -> T.Iterable[str]:
        return [self.get_pretty_text()]


class Prefix:
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
    def __init__(
        self,
        prefixes: T.Sequence[Prefix],
        variables: T.Sequence[Variable],
        graph_pattern: GraphPattern,
        distinct: bool = True,
    ):
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
        select = "SELECT DISTINCT" if self.distinct else "SELECT"
        variables_str = " ".join(map(lambda v: v.get_pretty_text(), self.variables))
        variables = f"{select} {variables_str}"
        graph_pattern_lines = list(self.graph_pattern.get_lines())
        for prefix in prefixes:
            yield prefix
        yield variables
        yield f"WHERE {graph_pattern_lines[0]}"
        for graph_pattern_line in graph_pattern_lines[1:]:
            yield graph_pattern_line
