from .uniprot.representation import knowledge_graph as uniprot_graph
from .rhea.representation import knowledge_graph as rhea_graph
from .rhea.entities import RheaEntity
from .uniprot.entities import UniprotEntity
from .common import Repository

knowledge_graphs = {Repository.RHEA: rhea_graph, Repository.UNIPROT: uniprot_graph}

urls = {
    Repository.RHEA: "https://sparql.rhea-db.org/",
    Repository.UNIPROT: "https://sparql.uniprot.org/",
}

type_mappings = {RheaEntity: Repository.RHEA, UniprotEntity: Repository.UNIPROT}
