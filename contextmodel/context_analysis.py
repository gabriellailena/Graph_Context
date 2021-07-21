import os
import json
from neo4j import GraphDatabase

# Function declarations
def get_instances_names(session, program_name, class_name):
    query = """MATCH (e)-[:IS_TYPE]-(:n4sch__Class{n4sch__name:$class_name})
            WHERE exists(e.mode) AND $program in e.mode
            RETURN DISTINCT e.n4sch__name"""
    result = session.run(query, program=program_name, class_name=class_name)
    return result

def get_average_value(session, program_name, context_name, phase):
    query = """MATCH (d:n4sch__Instance)-[:HAS_VALUE]-(v:n4sch__Value)
            WHERE d.mode = $program AND d.n4sch__name = $context AND v.phase = $phase
            RETURN AVG(v.value)"""
    result = session.run(query, program=program_name, context=context_name, phase=phase)
    return result.single()[0]


# Configure Neo4j db
uri = "bolt://localhost:7687"
username = "admin"
password = "admin"
db_name = "rdfmodel"

# Connect to graph database
graph_driver = GraphDatabase.driver(uri, auth=(username, password))
try:
    graph_session = graph_driver.session(database=db_name)
except Exception as e:
    print(str(e))
    print("Cannot establish connection to graph database!")

# Get program names
with open('programs.json') as file:
    programs_json = json.load(file)
programs = list()
for key in programs_json:
    programs.append(key)

# Get the related context data, sensors, and actuators to the program
program_instances = dict((el, {"sensors": None, "actuators": None, "context": None}) for el in programs)
for program in programs:
    sensor_list = list()
    actuator_list = list()
    context_dict = dict((el, []) for el in ["internal", "inferred", "external"])
    sensors = get_instances_names(graph_session, program, "Sensor")
    actuators = get_instances_names(graph_session, program, "Actuator")
    internal = get_instances_names(graph_session, program, "Internal")
    inferred = get_instances_names(graph_session, program, "Inferred")
    external = get_instances_names(graph_session, program, "External")
    for item in sensors:
        sensor_list.append(item[0])
    for item in actuators:
        actuator_list.append(item[0])
    for item in internal:
        context_dict["internal"].append(item[0])
    for item in inferred:
        context_dict["inferred"].append(item[0])
    for item in external:
        context_dict["external"].append(item[0])
    program_instances[program]["sensors"] = sensor_list
    program_instances[program]["actuators"] = actuator_list
    program_instances[program]["context"] = context_dict

# ------ ANOMALY DETECTION ------ #
# Query the graph database for latest measurements of each program
# TODO: key (program name) should be an input from the GUI. Remember to relate this to the front-end.
selected_program = "Door Lock Program"
context_names = list()
subresult = dict()
result_program = dict()
if selected_program in program_instances:
    context = program_instances[selected_program]["context"]
    for key in context:
        if len(context[key]) > 0:
            for i in range(len(context[key])):
                context_names.append(context[key][i])

    # Get average values of each context data
    if selected_program == "Pump Out Program":
        for name in context_names:
            avg = list()  # index 0 for phase 1, index 1 for phase 2, index 2 for phase 3
            avg.append(get_average_value(graph_session, selected_program, name, "1"))
            avg.append(get_average_value(graph_session, selected_program, name, "2"))
            avg.append(get_average_value(graph_session, selected_program, name, "3"))

            if name == "Water_Level":
                if avg[0] - avg[2] <= 30:
                    subresult[name] = "High"
                else:
                    subresult[name] = "Low"
            elif name == "Exit_Water_Flow":
                if avg[1] == 0:
                    subresult[name] = "No Flow"
                else:
                    subresult[name] = "Flow OK"
        result_program[selected_program] = subresult
    elif selected_program == "Door Lock Program":
        for name in context_names:
            avg = list()  # index 0 for phase 1, index 1 for phase 2, index 2 for phase 3
            avg.append(get_average_value(graph_session, selected_program, name, "1"))
            avg.append(get_average_value(graph_session, selected_program, name, "2"))
            avg.append(get_average_value(graph_session, selected_program, name, "3"))

            if name == "Pressure":
                if ((avg[1] - avg[0])/avg[0]) >= 0.2:
                    subresult[name] = "Normal"
                else:
                    subresult[name] = "Low"
            elif name == "Lock":
                if avg[1] == 1:
                    subresult[name] = "Locked"
                else:
                    subresult[name] = "Unlocked"
        result_program[selected_program] = subresult
    elif selected_program == "Fan Program":
        for name in context_names:
            avg = list()
            avg.append(get_average_value(graph_session, selected_program, name, "1"))
            avg.append(get_average_value(graph_session, selected_program, name, "2"))
            print(name, ":", avg)

            if name == "Vibration":
                if avg[1] <= 25:
                    subresult[name] = "Normal"
                else:
                    subresult[name] = "High"
            elif name == "Loudness":
                if ((avg[1]-avg[0])/avg[0]) <= 0.75:
                    subresult[name] = "Normal"
                else:
                    subresult[name] = "High"
            elif name == "Mass_Air_Flow":
                if avg[1] >= 50:
                    subresult[name] = "Normal"
                else:
                    subresult[name] = "Low"
        result_program[selected_program] = subresult
# TODO: do other programs and find out how to show the results on the front-end
print(result_program)


