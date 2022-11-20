from ..common import SparqlEntity


class UniprotEntity(SparqlEntity):
    START = "start"
    PROTEIN = "protein"
    FULL_NAME = "full_name"
    RECOMMENDED_NAME = "recommended_name"
    PROTEIN_ID = "protein_id"
    PFAM = "pfam"
    PFAM_FILTERING = "pfam_filtering"
    SEQUENCE_OBJECT = "sequence_object"
    SEQUENCE = "sequence"
    ORGANISM = "organism"
    ORGANISM_NAME = "organism_name"
    TAXON_FILTERING = "taxon_filtering"
    KINGDOM = "kingdom"
    KINGDOM_NAME = "kingdom_name"
    SUPERKINGDOM = "superkingdom"
    SUPERKINGDOM_NAME = "superkingdom_name"
    SUPFAM = "supfam"
    CATALYTIC_ACTIVITY = "catalytic_activity"
    CATALYZED_REACTION = "catalyzed_reaction"
