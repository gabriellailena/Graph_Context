// Load CSV
LOAD CSV WITH HEADERS FROM 'file:///contextdata.csv' AS row

// Create nodes
MERGE (d:`Data Source` {name: row.datasource, class: "Sensor"})
MERGE (v:Value {id: toInteger(row.idsensordata), value: toFloat(row.observed_value), class: "Measurement"})
    ON CREATE SET
    v.time = datetime(REPLACE(row.time, ' ', 'T')),
    v.phase = row.phase,
    v.unit = row.unit
MERGE (dm:`Diagnosis Mode` {name: row.diagnosisMode, class: "Function"})

// Create relationships
MERGE (d)-[:HAS_FUNCTION]->(dm)
MERGE (d)-[:MEASURES]->(v)
MERGE (dm)-[:HAS_INPUT]->(v)