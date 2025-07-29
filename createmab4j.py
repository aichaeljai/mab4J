from utils import *
from tqdm import tqdm


q = construct_general_query()
logger.info("Query data on KG")
df_mAb = sdf.get(endpoint=endpoint, query=q, post=True)
df_mAb=df_mAb.dropna()
logger.success("Query data on KG OK")
driver = driver_creation(mdp="12345678", database_name="imgt-mab4j")


test_gdb_connection(driver, database_name="imgt-mab4j")

logger.info("Adding data to gdb")
for index, row in tqdm(df_mAb.iterrows()):
    subject = row["subject"]
    object_ = row["object"]
    relation = row["relation"]

    if relation == "https://www.wikidata.org/wiki/Property:P1542":
        relation = "https://www.wikidata.org/wiki/Property/P1542"

    try:
        add_entity(driver, subject, object_, relation)
    except Exception as e:
        logger.error(
            f"Could not add {replace_uri_with_nspace_string(subject)} "
            f"--{replace_uri_with_nspace_string(relation)}--> "
            f"{replace_uri_with_nspace_string(object_)}"
        )
        logger.error(e)

logger.success("Adding data to gdb OK")