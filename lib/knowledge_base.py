from .uniprot.representation import knowledge_graph as uniprot_graph
from .rhea.representation import knowledge_graph as rhea_graph
from networkx.algorithms.operators import compose_all
from .common import Repository

graph = compose_all([uniprot_graph, rhea_graph])

urls = {
    Repository.RHEA: "https://sparql.rhea-db.org/",
    Repository.UNIPROT: "https://sparql.uniprot.org/"
}
