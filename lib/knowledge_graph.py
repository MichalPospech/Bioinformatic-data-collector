from .uniprot.representation import knowledge_graph as uniprot_graph
from networkx.algorithms.operators import compose_all


graph = compose_all([uniprot_graph])
