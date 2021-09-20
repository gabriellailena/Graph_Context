"""
This module is meant to pre-process export the SQL data into a .csv file, ready to be imported to
Neo4j database. The .csv file is then transformed into a context model, stored in a Neo4j graph database.
"""

import pandas as pd
import sys
import sqlalchemy
from datetime import datetime
from neo4j import GraphDatabase

def sql_to_csv(graph_session, connection, out_file_path):
    # Gets the latest stored timestamp of values and append only the newest data
    # that have not been stored in the graph database
    result = graph_session.run('''MATCH (v:n4sch__Value)
            RETURN DISTINCT max(v.time)
    ''')

    # Reformat timestamp
    for item in result:
        dt = item[0]
    if dt is not None:
        dt_py = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, int(dt.second))
        latest_time = dt_py.strftime('%m/%d/%Y, %H:%M:%S')
    else:
        latest_time = ''
    
    # Get all the data, for all diagnosis modes, from the table 'graphcontextdata' and store them as Pandas dataframe
    query = "SELECT *, AVG(observed_value) AS avg_val FROM graphcontextdata WHERE `time` > '" + latest_time + "' AND `phase` != 0 AND `diagnosisMode` != 'Complete Short Program' GROUP BY diagnosisMode, `phase`, datasource, `time`;"
    context_df = pd.read_sql(sql=query,
                             con=connection, parse_dates=['time'], columns=["idsensordata", "diagnosisMode", "phase",
                             "datasource", "observed_value", "time", "unit"])

    # Delete rows that contain null values in any of its columns
    context_df = context_df.dropna()
    context_df = context_df[~context_df.unit.str.contains("internal")]

    # Create .csv file in the Import folder of Neo4j -> files are named with creation timestamp
    print("Writing data to .csv...")
    context_df.to_csv(out_file_path, header=True, index=False)
    print("Write successful, data written to " + out_file_path)
    return context_df


def csv_to_graph(graph_session, dataframe):
    """# Deletes existing instances to be replaced with new ones
    graph_session.run('''
                    MATCH(d:n4sch__Instance)-[]-(v:n4sch__Value) 
                    DETACH DELETE d, v''')"""
    print(dataframe)
    if dataframe.empty: # If there is no new data coming in
        # do nothing
        print("No new data have arrived.")
        pass
    else:
        # Cypher query to load the CSV
        print("Exporting .csv data to graph...")
        query_load = '''LOAD CSV WITH HEADERS FROM 'https://www.dropbox.com/s/q07iwvoenp5nx70/context_data.csv?raw=1' AS row FIELDTERMINATOR ','
                        MATCH (ex:n4sch__Class{n4sch__name:'External'}) 
                        MATCH (inf:n4sch__Class{n4sch__name:'Inferred'})
                        MATCH (int:n4sch__Class{n4sch__name:'Internal'})
                        WITH ex, inf, int, row
                        FOREACH (i in CASE WHEN row.datasource = "Water_Hardness" OR row.datasource = "Washing_Powder" THEN [1] ELSE [] END |
                          MERGE (d:n4sch__Instance {n4sch__name: row.datasource, mode: row.diagnosisMode})
                          MERGE (d)-[:IS_TYPE]->(ex)
                          MERGE (d)-[:HAS_AVERAGE_VALUE]->(v:n4sch__Value {phase: row.phase, value: toFloat(row.observed_value), unit: row.unit, time:datetime(REPLACE(row.time, ' ', 'T')), checked:0})
                        )
                        
                        FOREACH (i in CASE WHEN row.datasource = "Usage_Frequency" OR row.datasource = "Used_Modes" THEN [1] ELSE [] END |
                          MERGE (d:n4sch__Instance {n4sch__name: row.datasource, mode: row.diagnosisMode})
                          MERGE (d)-[:IS_TYPE]->(inf)
                          MERGE (d)-[:HAS_AVERAGE_VALUE]->(v:n4sch__Value {phase: row.phase, value: toFloat(row.observed_value), unit: row.unit, time:datetime(REPLACE(row.time, ' ', 'T')), checked:0})
                        )
                        
                        FOREACH (i in CASE WHEN row.datasource <> "Water_Hardness" AND row.datasource <> "Usage_Frequency" AND row.datasource <> "Washing_Powder" AND row.datasource <> "Used_Modes" THEN [1] ELSE [] END |
                          MERGE (d:n4sch__Instance {n4sch__name: row.datasource, mode: row.diagnosisMode})
                          MERGE (d)-[:IS_TYPE]->(int)
                          MERGE (d)-[:HAS_AVERAGE_VALUE]->(v:n4sch__Value {phase: row.phase, value: toFloat(row.observed_value), unit: row.unit, time:datetime(REPLACE(row.time, ' ', 'T')), checked:0})
                        )
                    '''
        try:
            graph_session.run(query_load)
            print("Graph export successful.")
        except Exception as e:
            print(str(e))
            print("Unable to run graph query!")
        finally:
            graph_session.close()


def sql_to_graph(uri, username, password, file_path, db_name):
    try:
        # Create connection to SQLAlchemy
        # sql_uri = 'mysql://root:root@localhost:3306/contextmodeldata'
        sql_uri = 'mysql://admin:admin@localhost:3306/contextmodeldata'
        engine = sqlalchemy.create_engine(sql_uri)

        # Connect to graph database
        graph_driver = GraphDatabase.driver(uri, auth=(username, password))
        graph_session = graph_driver.session(database=db_name)

        # Exports the SQL database to CSV and directly merge the nodes and relationships with Neo4j database
        print("Starting export of MySQL data to .csv...")
        df = sql_to_csv(graph_session, engine, file_path)
        print("Starting export of .csv to Neo4j...")
        csv_to_graph(graph_session, df)
    except:
        print("Unable to connect to database.")
        print(sys.exc_info()[0])
        raise
    finally:
        graph_session.close()
