import json
from neo4j import GraphDatabase
from loguru import logger
import sparql_dataframe as sdf
# Set up the SPARQL endpoint
endpoint = "https://www.imgt.org/fuseki/MabkgKg/query"

####  Connexion stuff
# URI = "neo4j://127.0.0.1:7687"
# user = "neo4j"
# mdp ="neo4jneo4j"
# AUTH = (user, mdp)

def driver_creation(mdp, database_name, URI="neo4j://127.0.0.1:7687", user="neo4j"):
    AUTH = (user, mdp)
    driver = GraphDatabase.driver(URI, auth=AUTH, database=database_name)
    return driver


# driver = driver_creation(mdp="12345678", database_name="imgt-mab4j")


## namespaces
sio = "http://semanticscience.org/resource/"
hgnc = "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/"
obo = "http://purl.obolibrary.org/obo/"
ncit = "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#"
imgt = "http://www.imgt.org/imgt-ontology#"
imgts = "https://www.imgt.org/imgt-ontology#"
faldo = "http://biohackathon.org/resource/faldo#"
owl = "http://www.w3.org/2002/07/owl#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
protege = "http://protege.stanford.edu/plugins/owl/"
xmls = "http://www.w3.org/2001/XMLSchema#"
rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
pubmed = "https://pubmed.ncbi.nlm.nih.gov/"
bibo = "http://purl.org/ontology/bibo/"
skos = "http://www.w3.org/2004/02/skos/core#"
oboInowl = "http://www.geneontology.org/formats/oboInOwl#"
dc = "http://purl.org/dc/elements/1.1/"
foaf = "http://xmlns.com/foaf/0.1/"
vgnc = "https://vertebrate.genenames.org/data/gene-symbol-report/#!/vgnc_id/"
doid = "https://doi.org/"
pmc = "https://www.ncbi.nlm.nih.gov/pmc/articles/"
ncbi_gene = "https://www.ncbi.nlm.nih.gov/gene/"
wiki = "https://www.wikidata.org/wiki/Property:"
protege = "http://protege.stanford.edu/plugins/owl/protege#"
ocre = "http://purl.org/net/OCRe/study_design.owl#"
pharmgkb = "https://www.pharmgkb.org/"
bao = "http://www.bioassayontology.org/bao#"


link_mabdb = "https://www.imgt.org/mAb-DB/mAbcard?AbId="

## replace uri with space name
def replace_uri_with_nspace_string(string):
    string = (
        string.replace(sio, "sio:")
        .replace(hgnc, "hgnc:")
        .replace(obo, "obo:")
        .replace(ncit, "ncit:")
        .replace(imgt, "imgt:")
        .replace(imgts, "imgt:")
        .replace(faldo, "faldo:")
        .replace(owl, "owl:")
        .replace(rdfs, "rdfs:")
        .replace(xmls, "xmls:")
        .replace(skos, "skos:")
        .replace(oboInowl, "oboinowl:")
        .replace(rdf, "rdf:")
        .replace(dc, "dc:")
        .replace(pubmed, "PM")
        .replace(bibo, "bibo:")
        .replace(foaf, "foaf:")
        .replace(vgnc, "")
        .replace(doid, "doid:")
        .replace(pmc, "pmc:")
        .replace(ncbi_gene, "ncbi_gene:")
        .replace(wiki, "wiki:")
        .replace(protege, "protege:")
        .replace(ocre, "ocre:")
        .replace(pharmgkb, "pharmgkb:")
        .replace(bao, "bao:")
        .replace("%5B", "[")
        .replace("%5D", "]")
        .replace("%20", " ")
        .replace("%5", "-")
    )
    return string


## Load typing dicionary
def read_json_file(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

dico_subject = read_json_file("data/Type_subject.json")
dico_object = read_json_file("data/Type_object.json")

## test neo4j db connexion
def test_gdb_connection(driver, database_name):
    with driver.session(database=database_name) as session:
        result = session.run("RETURN 'connected' AS status")
        logger.success(result.single()["status"])


### general query template
def construct_general_query():
    query_template = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix bao: <http://www.bioassayontology.org/bao#>

    Select ?subject ?relation ?object {
    ?subject ?relation ?object
    FILTER (!REGEX(str(?object), "www.w3.org/2002/07/owl"))
    FILTER (!REGEX(str(?relation), "range"))
    FILTER (!REGEX(str(?relation), "domain"))
    }
    """
    return query_template

# Requête SPARQL pour récupérer tous les labels :
q = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?subject ?object WHERE {{
  ?subject rdfs:label ?object .
}}
"""
df_label = sdf.get(endpoint, q)
# Fonction d'extraction des labels (extract_label_from_iri_v2) :
def extract_label_from_iri_v2(iri, df=df_label):
    """
    Extrait le label d'un IRI en gérant différents types d'entrée.
    """
    # Gestion des types non-string (float, int, etc.)
    if not isinstance(iri, str):
        return str(iri)

    # Gestion des identifiants HGNC
    if isinstance(iri, str) and "genenames.org" in iri:
        hgnc_id = iri.split("HGNC:")[-1]
        if hgnc_id.isdigit():
            return f"HGNC:{hgnc_id}"

    # Recherche du label dans le DataFrame
    object = df[df.subject == iri]["object"].values
    if len(object) > 0:
        return object[0]
    else:
        return iri.split("#")[-1].split("/")[-1]



## inference type based relation
def infer_type_from_uri_v2(uri):
    """
    Détermine le type d'une entité ou les types d'une relation.
    """
    prefixed_uri = replace_uri_with_nspace_string(uri)

    # Si c'est une relation, retourner les types sujet/objet
    if prefixed_uri in dico_subject and prefixed_uri in dico_object:
        subject_type = dico_subject[prefixed_uri]
        object_type = dico_object[prefixed_uri]

        if isinstance(subject_type, list):
            subject_type = subject_type[0].split(":")[-1]
        else:
            subject_type = subject_type.split(":")[-1]

        object_type = object_type.split(":")[-1]
        return subject_type, object_type
    return "Entity", "Entity"


# Fonction de détection des relations d'annotation
def is_annotation(relation):
    """Vérifie si une relation est une annotation."""
    if (
        "BFO" not in relation
        and "RO" not in relation
        and "BAO" not in relation
        and "SIO" not in relation
        and (
            "_" in relation
            or "hasStatut" in relation
            or "depict" in relation
            or "isLinkedToStructureAccessNumb" in relation
            or "date" in relation
            or "label" in relation
            or "altLabel" in relation
            or "type" in relation
            or "definition" in relation
            or "comment" in relation
            or "inverseOf" in relation
            or "subClassOf" in relation
            or "disjointWith" in relation
            or "example" in relation
            or "sameAs" in relation
            or "title" in relation
            or "isDescribedBy" in relation
            or "hasDesignation" in relation
            or "isDecidedBy" in relation
        )   

    ):
        return True
    return False


## add entitiies and relation in the graph
def add_entity(driver, subject, object_, relation):
    """
    Crée les entités et les relations dans Neo4j en préservant les propriétés.
    """
    # Préfixer les URIs
    prefixed_relation = replace_uri_with_nspace_string(relation)

    # Extraire les labels
    subject_label = extract_label_from_iri_v2(subject)
    object_label = extract_label_from_iri_v2(object_)
    relation_label = extract_label_from_iri_v2(relation)

    
    with driver.session() as session:
        if is_annotation(relation_label):
            # Pour les annotations
           
            session.run(
                f"""
                MERGE (n {{iri: $subject}})
                REMOVE n:Entity
                SET n.label = $subject_label
                SET n.{relation_label} = $object_label
                """,
                {
                    "subject": subject,
                    "subject_label": subject_label,
                    "object_label": object_label,
                },
            )
        else:
            # Determine subject_type and object_type based on relation
            if "hasClinicalDomain" in relation_label:
                if "MOA_" in subject:
                    subject_type = "MOA"
                    object_type = "ClinicalDomain"
                else:
                    subject_type = "ClinicalIndication"
                    object_type = "ClinicalDomain"
            elif "hasClinicalIndication" in relation_label:
                if "StudyProduct_" in subject:
                    subject_type = "StudyProduct"
                    object_type = "ClinicalIndication"
                else:
                    subject_type = "PharmaSubstance"
                    object_type = "ClinicalIndication"
            elif "isClinicalIndicationOf" in relation_label:
                if "StudyProduct_" in object_:
                    object_type = "StudyProduct"
                    subject_type = "ClinicalIndication"
                else:
                    subject_type = "ClinicalIndication"
                    object_type = "PharmaSubstance"
        
            elif "hasBibliographicReference" in relation_label:
                if "MOA_" in subject:
                    subject_type = "MOA"
                    object_type = "BibliographicReference"
                else:
                    subject_type = "PharmaSubstance"
                    object_type = "BibliographicReference"

            elif "inTaxon" in relation_label:
                if "Clone_" in subject:
                    subject_type = "Clone"
                    object_type = "Taxon"
                elif "Segment_" in subject:
                    subject_type = "Segment"
                    object_type = "Taxon"
                else:
                    subject_type = "Target"
                    object_type = "Taxon"

            elif "Construct_" in subject and "isConstructOf" in relation_label: 
                subject_type = "Construct"
                if "Fused_" in object_:
                    object_type = "Fused"
                elif "mAb_" in object_:
                    object_type = "PharmaSubstance"
                elif "Conjugate_" in object_:
                    object_type = "Conjugate"
                elif "Radiolabelled_" in object_:
                    object_type = "Radiolabelled"

            elif "Construct_" in object_ and "hasConstruct" in relation_label: 
                object_type = "Construct"
                if "Fused_" in subject:
                    subject_type = "Fused"
                elif "mAb_" in subject:
                    subject_type = "PharmaSubstance"
                elif "Conjugate_" in subject:
                    subject_type = "Conjugate"
                elif "Radiolabelled_" in subject:
                    subject_type = "Radiolabelled"    

            else:
                # Pour les relations spécifiques - fallback case
                subject_type, object_type = infer_type_from_uri_v2(relation)

            # Créer ou mettre à jour les nœuds et la relation
            session.run(
                f"""
                MERGE (a {{iri: $subject}})
                SET a:{subject_type}
                REMOVE a:Entity
                SET a.label = $subject_label

                WITH a
                MERGE (b {{iri: $object_}})
                SET b:{object_type}
                REMOVE b:Entity
                SET b.label = $object_label

                WITH a, b
                MERGE (a)-[r:{relation_label}]->(b)
                SET r.iri = $relation
                SET r.label = $relation_label
                """,
                {
                    "subject": subject,
                    "object_": object_,
                    "subject_label": subject_label,
                    "object_label": object_label,
                    "relation": relation,
                    "relation_label": relation_label or "Unknown",
                }
            )
            
