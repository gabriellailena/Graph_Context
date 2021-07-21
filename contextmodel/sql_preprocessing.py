"""
This module is meant to pre-process export the SQL data into a .csv file, ready to be imported to
Neo4j database. The .csv file is then transformed into a context model, stored in a Neo4j graph database.
"""

import pandas as pd
import sqlalchemy
from neo4j import GraphDatabase


def sql_to_csv(connection, out_file_path):
    # Get all the latest data, for all diagnosis modes, from the table 'contextdata' and store them as Pandas dataframe
    context_df = pd.read_sql(sql="""SELECT * FROM contextmodeldata.contextdata c1
                                    WHERE time = (SELECT MAX(time) FROM contextdata c2 
                                    WHERE c1.diagnosisMode = c2.diagnosisMode)
                                    ORDER BY diagnosisMode, time;""",
                             con=connection,
                             parse_dates=["time"],
                             columns=["idsensordata", "diagnosisMode", "phase",
                                      "datasource", "observed_value", "time", "unit"])

    # Delete rows that contain null values in any of its columns
    context_df = context_df.dropna()

    # Create .csv file in the Import folder of Neo4j -> files are named with creation timestamp
    print("Writing data to .csv...")
    context_df.to_csv(out_file_path, header=True, index=False)
    print("Write successful, data written to " + out_file_path)


def csv_to_graph(uri, username, password, db_name):
    # Connect to Neo4j graph database
    graph_driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        graph_session = graph_driver.session(database=db_name)
    except Exception as e:
        print(str(e))
        print("Cannot establish connection to graph database!")

    # Deletes existing instances to be replaced with new ones
    graph_session.run("""MATCH(d:n4sch__Instance)
                    MATCH(n:n4sch__Instance)-[]-(v:n4sch__Value) 
                    DETACH DELETE d, n, v""")

    # Cypher query to load the CSV
    print("Exporting .csv data to graph...")
    query_load = """LOAD CSV WITH HEADERS FROM 'file:///contextdata.csv' AS row 
                    MATCH (ex:n4sch__Class{n4sch__name:'External'}) 
                    MATCH (inf:n4sch__Class{n4sch__name:'Inferred'})
                    MATCH (int:n4sch__Class{n4sch__name:'Internal'})
                    WITH ex, inf, int, row
                    FOREACH (i in CASE WHEN row.datasource = "Water_Hardness" THEN [1] ELSE [] END |
                      MERGE (d:n4sch__Instance {n4sch__name: row.datasource, mode: row.diagnosisMode})
                      MERGE (d)-[:IS_TYPE]->(ex)
                      MERGE (d)-[:HAS_VALUE]->(v:n4sch__Value {phase: row.phase, value: toFloat(row.observed_value), unit: row.unit, time:datetime(REPLACE(row.time, ' ', 'T'))})
                    )
                    
                    FOREACH (i in CASE WHEN row.datasource = "Usage_Frequency" OR row.datasource = "Washing_Powder" OR row.datasource = "Used_Modes" THEN [1] ELSE [] END |
                      MERGE (d:n4sch__Instance {n4sch__name: row.datasource, mode: row.diagnosisMode})
                      MERGE (d)-[:IS_TYPE]->(inf)
                      MERGE (d)-[:HAS_VALUE]->(v:n4sch__Value {phase: row.phase, value: toFloat(row.observed_value), unit: row.unit, time:datetime(REPLACE(row.time, ' ', 'T'))})
                    )
                    
                    FOREACH (i in CASE WHEN row.datasource <> "Water_Hardness" AND row.datasource <> "Usage_Frequency" AND row.datasource <> "Washing_Powder" AND row.datasource <> "Used_Modes" THEN [1] ELSE [] END |
                      MERGE (d:n4sch__Instance {n4sch__name: row.datasource, mode: row.diagnosisMode})
                      MERGE (d)-[:IS_TYPE]->(int)
                      MERGE (d)-[:HAS_VALUE]->(v:n4sch__Value {phase: row.phase, value: toFloat(row.observed_value), unit: row.unit, time:datetime(REPLACE(row.time, ' ', 'T'))})
                    )
                """
    
    try:
        graph_session.run(query_load)
        print("Graph export successful.")
    except Exception as e:
        print(str(e))
        print("Unable to run graph query!")
    finally:
        graph_session.close()

def sql_to_graph(uri, username, password, connection, file_path, db_name):
    # Exports the SQL database to CSV and directly merge the nodes and relationships with Neo4j database
    print("Starting export of MySQL data to .csv...")
    sql_to_csv(connection, file_path)
    print("Starting export of .csv to Neo4j...")
    csv_to_graph(uri, username, password, db_name)