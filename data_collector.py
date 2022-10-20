import click
import pathlib
import requests
import pandas as pd
import io
import typing as T
from enum import Enum, auto
import json

import lib.query_generator
from lib.rhea.config import RheaSearchConfig
from lib.rhea.query_generator import RheaQueryBuilder
from lib.sparql_query import SelectQuery
import lib.uniprot.config as UC
from lib.uniprot.query_generator import UniprotQueryBuilder


class Repository(Enum):
    RHEA = auto()
    UNIPROT = auto()


def cb_validate_path(
    ctx: click.Context, command: click.Command, path: T.Optional[pathlib.Path]
) -> T.Optional[pathlib.Path]:
    if not path:
        return None
    extension = path.suffix
    if extension not in [".csv", ".xlsx"]:
        raise click.BadParameter("Only xlsx and csv output files are supported.")
    return path


def collect_data(query: SelectQuery, url: str) -> pd.DataFrame:
    response = requests.get(
        url, params={"query": query.get_pretty_text(), "format": "csv"}
    )
    response.raise_for_status()
    if response.ok:
        data_frame = pd.read_csv(io.StringIO(response.text), sep=",", header=0)
    return data_frame


TConfig = T.TypeVar("TConfig")


def get_query(
    config: TConfig,
    query_builder_ctor: T.Callable[
        [TConfig], lib.query_generator.SparqlQueryBuilder[TConfig]
    ],
) -> SelectQuery:
    builder = query_builder_ctor(config)
    return builder.get_query()


def save_data(data: pd.DataFrame, path: pathlib.Path) -> None:
    with open(path, mode="bw") as writer:
        if path.suffix == ".xlsx":
            data.to_excel(writer, index=False, engine="openpyxl")
        if path.suffix == ".csv":
            data.to_csv(writer, index=False)


@click.command(help="Generate query based on config saved in config_path")
@click.option(
    "--print-query",
    "-q",
    is_flag=True,
    default=False,
    help="Toggle to show generated query",
)
@click.argument(
    "config_path",
    type=click.Path(exists=True, file_okay=True),
)
@click.argument(
    "repository", type=click.Choice(["uniprot", "rhea"], case_sensitive=False)
)
@click.option(
    "--out-path",
    type=click.Path(path_type=pathlib.Path),
    callback=cb_validate_path,
    help="Path where to save result of the query, must have either csv or xlsx extension",
)
def run(
    config_path: pathlib.Path,
    repository: str,
    out_path: T.Optional[pathlib.Path],
    print_query: bool,
) -> None:
    if repository == "uniprot":
        with open(config_path, encoding="utf-8") as config_file:
            json_config = json.load(config_file)
        config = UC.UniprotSearchConfig.schema().load(json_config)
        query = get_query(config, UniprotQueryBuilder)
    if repository == "rhea":
        with open(config_path, encoding="utf-8") as config_file:
            json_config = json.load(config_file)
        config = RheaSearchConfig.schema().load(json_config)
        query = get_query(config, RheaQueryBuilder)

    if print_query:
        print(query.get_pretty_text())
    if out_path:
        data = collect_data(query, UC.URL)
        save_data(data, out_path)


if __name__ == "__main__":
    run()
