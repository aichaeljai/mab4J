# IMGT/mAb4J Data Integration

This project extracts data from the IMGT/mAb-KG knowledge graph, processes it in Python, and loads it into a Neo4j property graph (IMGT/mAb4J).

---

## Table of Contents

* [Project Overview](#project-overview)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
* [Scripts](#scripts)
* [Neo4j Graph Structure](#neo4j-graph-structure)
* [License](#license)

---

## Project Overview

The project performs the following steps:

1. **Query the RDF knowledge graph (IMGT/mAb-KG)**
   Uses SPARQL queries to retrieve all relevant entities, relations, and labels.

2. **Data Cleaning and Transformation**
   Filters out empty entries and normalizes certain URIs for consistency.

3. **Load into Neo4j**
   Adds entities and relations into a Neo4j property graph, enabling efficient graph queries and analysis.

---

## Requirements

* Python 3.12+
* Neo4j 5.x
* Packages:

  ```text
  pandas
  sparql_dataframe
  SPARQLWrapper
  neo4j
  tqdm
  loguru
  ```
* Access to the IMGT/mAb-KG SPARQL endpoint

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Set your Neo4j credentials and SPARQL endpoint in `utils.py` or environment variables.
2. Run the main script:

```bash
python main.py
```

3. Monitor progress via console logs.
4. Once completed, you can explore the graph in the Neo4j Browser.

---

## Scripts

* `main.py` – Main script to query SPARQL endpoint, transform data, and load into Neo4j.
* `utils.py` – Utility functions for constructing queries, adding entities, and managing the Neo4j driver.
* `notebooks/data_exploration.ipynb` – Optional notebook to explore the raw SPARQL data and labels.

---

## Neo4j Graph Structure

* **Nodes**: Entities from the knowledge graph (e.g., antibodies, targets, genes)
* **Relationships**: Relations between entities (e.g., `P1542` for targets, other Wikidata properties)
* **Properties**: Labels, URIs, and other metadata

---

## License

This project is licensed under the MIT License.
