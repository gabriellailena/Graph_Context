import os
import json
from neo4j import GraphDatabase
from datetime import datetime

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

def get_time_string(session, program_name):
    query = """MATCH (d:n4sch__Instance)-[:HAS_VALUE]-(v:n4sch__Value)
            WHERE d.mode = $program
            RETURN DISTINCT v.time"""
    result = session.run(query, program=program_name)

    # Format to string
    dt = result.single()[0]
    dt_py = datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, int(dt.second))
    time_formatted = dt_py.strftime('%d/%m/%y %H:%M:%S')

    return time_formatted


# Configure Neo4j db
# noinspection PyUnresolvedReferences
def analyze_context(uri, username, password, db_name):
    # Connect to graph database
    graph_driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        graph_session = graph_driver.session(database=db_name)
    except Exception as e:
        print(str(e))
        print("Cannot establish connection to graph database!")

    # Get program names
    query_res = graph_session.run("""MATCH (:n4sch__Class{n4sch__name:"Context"})-[*]-(n:n4sch__Instance) WHERE size(n.mode) > 2 
                RETURN DISTINCT n.mode""")
    programs = list()
    for item in query_res:
        programs.append(item[0])

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

    # Query the graph database for latest measurements of each program
    result_program = dict()
    for selected_program in programs:
        if selected_program in program_instances:
            context = program_instances[selected_program]["context"]
            context_names = list()

            for key in context:
                if len(context[key]) > 0:
                    for i in range(len(context[key])):
                        context_names.append(context[key][i])

            # Get average values of each context data
            subresult = dict()
            if selected_program == "Pump Out Program":
                flag_water_flow = False
                flag_water_level = False
                for name in context_names:
                    avg = list()  # index 0 for phase 1, index 1 for phase 2, index 2 for phase 3
                    avg.append(get_average_value(graph_session, selected_program, name, "1"))
                    avg.append(get_average_value(graph_session, selected_program, name, "2"))
                    avg.append(get_average_value(graph_session, selected_program, name, "3"))

                    if name == "Water_Level":
                        if avg[0] - avg[2] <= 30:
                            subresult[name] = "High"
                            flag_water_level = True
                        else:
                            subresult[name] = "Low"
                    elif name == "Exit_Water_Flow":
                        if avg[1] == 0:
                            subresult[name] = "No Flow"
                            flag_water_flow = True
                        else:
                            subresult[name] = "Flow OK"

                    if flag_water_level and flag_water_flow:
                        subresult["Message"] = "Suspected clogging! Please check " + \
                                               program_instances[selected_program]["actuators"][0] + " for possible defect or necessary maintenance!"
                    elif flag_water_level ^ flag_water_flow:
                        subresult["Message"] = "Possible sensor defect, please check the following sensors: " + \
                                                ', '.join(program_instances[selected_program]["sensors"])
                    else:
                        subresult["Message"] = ', '.join(program_instances[selected_program]["sensors"]) + " and " + \
                                               program_instances[selected_program]["actuators"][0] + " are working properly."
                subresult["Time"] = get_time_string(graph_session, selected_program)
            elif selected_program == "Door Lock Program":
                flag_pressure = False
                flag_lock = False
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
                            flag_pressure = True
                    elif name == "Lock":
                        if avg[1] == 1:
                            subresult[name] = "Locked"
                        else:
                            subresult[name] = "Unlocked"
                            flag_lock = True

                    if flag_pressure:
                        if flag_lock:
                            subresult["Message"] = "Please check " + \
                                                   program_instances[selected_program]["actuators"][0] + \
                                                   "for possible defect or necessary maintenance."
                        else:
                            subresult["Message"] = "Possible sensor defect, please check the following sensors: " + \
                                                ', '.join(program_instances[selected_program]["sensors"])
                    else:
                        if not flag_lock:
                            subresult["Message"] = ', '.join(program_instances[selected_program]["sensors"]) + " and " + \
                                                   program_instances[selected_program]["actuators"][0] + " are working properly."
                        else:
                            subresult["Message"] = subresult["Message"] = "Possible sensor defect, please check the following sensors: " + \
                                                ', '.join(program_instances[selected_program]["sensors"])

                subresult["Time"] = get_time_string(graph_session, selected_program)
            elif selected_program == "Fan Program":
                flag_vibration = False
                flag_loudness = False
                flag_air_flow = False
                for name in context_names:
                    avg = list()
                    avg.append(get_average_value(graph_session, selected_program, name, "1"))
                    avg.append(get_average_value(graph_session, selected_program, name, "2"))

                    if name == "Vibration":
                        if avg[1] <= 25:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "High"
                            flag_vibration = True
                    elif name == "Loudness":
                        if ((avg[1]-avg[0])/avg[0]) <= 0.75:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "High"
                            flag_loudness = True
                    elif name == "Mass_Air_Flow":
                        if avg[1] >= 50:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "Low"
                            flag_air_flow = True

                    if flag_loudness and flag_vibration:
                        if flag_air_flow:
                            subresult["Message"] = "Please check " + program_instances[selected_program]["actuators"][0] + " for defect or necessary maintenance!"
                        else:
                            subresult["Message"] = "Please check if foreign objects are inside the " + program_instances[selected_program]["actuators"][0]
                    elif flag_loudness and not flag_vibration:
                        subresult["Message"] = "Please check " + program_instances[selected_program]["actuators"][0] + " for defect or necessary maintenance!"
                    elif not flag_loudness and flag_vibration:
                        if flag_air_flow:
                            subresult["Message"] = "Please check " + program_instances[selected_program]["actuators"][0] + " for defect or necessary maintenance!"
                        else:
                            subresult["Message"] = "Please re-adjust the drum position."
                    else:
                        subresult["Message"] = ', '.join(program_instances[selected_program]["sensors"]) + " and " + \
                                               program_instances[selected_program]["actuators"][0] + " are working properly."

                subresult["Time"] = get_time_string(graph_session, selected_program)
            elif selected_program == "Water Inlet Program":
                flag_water_level = False
                flag_water_flow = False
                flag_water_hardness = False
                for name in context_names:
                    avg = list()
                    avg.append(get_average_value(graph_session, selected_program, name, "1"))
                    avg.append(get_average_value(graph_session, selected_program, name, "2"))
                    avg.append(get_average_value(graph_session, selected_program, name, "3"))

                    if name == "Water_Level":
                        if avg[2] - avg[0] >= 20:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "Low"
                            flag_water_level = True
                    elif name == "Entrance_Water_Flow":
                        if avg[1] == 0.:
                            subresult[name] = "No Flow"
                            flag_water_flow = True
                        else:
                            subresult[name] = "Flow OK"
                    elif name == "Water_Hardness":
                        if avg[2] <= 14:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "Hard"
                            flag_water_hardness = True

                    if flag_water_hardness:
                        msg = " High water calcium level detected; running the diagnosis app more often is recommended."
                    else:
                        msg = ""

                    if flag_water_level and flag_water_flow:
                        subresult["Message"] = "Suspected clogging! Please check " + \
                                                program_instances[selected_program]["actuators"][0] + \
                                               "for possible defect or necessary maintenance." + msg
                    elif flag_water_level ^ flag_water_flow:
                        subresult["Message"] = "Possible sensor defect, please check the following sensors: " + \
                                         ', '.join(program_instances[selected_program]["sensors"]) + msg
                    else:
                        subresult["Message"] = ', '.join(program_instances[selected_program]["sensors"]) + " and " + \
                                               program_instances[selected_program]["actuators"][0] + " are working properly." + msg
                subresult["Time"] = get_time_string(graph_session, selected_program)
            elif selected_program == "Drum Motor Program":
                flag_loudness = False
                flag_vibration = False
                flag_rotation = 1
                for name in context_names:
                    avg = list()
                    avg.append(get_average_value(graph_session, selected_program, name, "1"))
                    avg.append(get_average_value(graph_session, selected_program, name, "2"))
                    avg.append(get_average_value(graph_session, selected_program, name, "3"))

                    if name == "Loudness":
                        if ((avg[1] - avg[0]) / avg[0]) <= 0.75:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "High"
                            flag_loudness = True
                    elif name == "Vibration":
                        if avg[1] <= 25:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "High"
                            flag_vibration = True
                    elif name == "Rotation_Speed":
                        if 50 <= avg[1] <= 60:
                            subresult[name] = "Normal"
                        elif avg[1] < 50:
                            subresult[name] = "Low"
                            flag_rotation = 0
                        else:
                            subresult[name] = "High"
                            flag_rotation = 2
                if flag_loudness:
                    if flag_vibration:
                        if flag_rotation == 2:
                            subresult["Message"] = program_instances[selected_program]["actuators"][0] + " works too hard! " \
                                                   "Please check the power supply."
                        else:
                            subresult["Message"] = "Please check if foreign objects are inside the " + program_instances[selected_program]["actuators"][0]
                    else:
                        if flag_rotation == 2:
                            subresult["Message"] = program_instances[selected_program]["actuators"][0] + " is too fast " \
                                                                            "and causes loudness. Please check for repair."
                        elif flag_rotation == 1:
                            subresult["Message"] = "Cannot determine cause of loudness. Please run another diagnostic program."
                        else:
                            subresult["Message"] = "Please check the " + program_instances[selected_program]["actuators"][0] + " for necessary maintenance."
                else:
                    if flag_vibration:
                        if flag_rotation == 2:
                            subresult["Message"] = "Please check the " + program_instances[selected_program]["actuators"][0] + " for repair."
                        else:
                            subresult["Message"] = "Please re-adjust the drum position."
                    else:
                        if flag_rotation == 1:
                            subresult["Message"] = ', '.join(program_instances[selected_program]["sensors"]) + " and " + \
                                                   program_instances[selected_program]["actuators"][0] + " are working properly."
                        else:
                            subresult["Message"] = "Please check the " + program_instances[selected_program]["actuators"][0] + " for repair."
                subresult["Time"] = get_time_string(graph_session, selected_program)
            elif selected_program == "Long Time Check":
                for name in context_names:
                    avg = list()
                    avg.append(get_average_value(graph_session, selected_program, name, "1"))

                    if name == "Laundry_Fill_Level":
                        if avg[0] > 75:
                            subresult[name] = "High"
                        elif avg[0] < 35:
                            subresult[name] = "Low"
                        else:
                            subresult[name] = "Normal"
                    elif name == "Laundry_Weight":
                        if avg[0] > 10:
                            subresult[name] = "High"
                        else:
                            subresult[name] = "Normal"
                    elif name == "Washing_Powder_Fill_Level":
                        if avg[0] > 75:
                            subresult[name] = "High"
                        elif avg[0] < 35:
                            subresult[name] = "Low"
                        else:
                            subresult[name] = "Normal"
                    elif name == "Washing_Powder":
                        if avg[0] == 0.:
                            subresult[name] = "Weak"
                        elif avg[0] == 1.:
                            subresult[name] = "Normal"
                        else:
                            subresult[name] = "Strong"
                    elif name == "Used_Modes":
                        if avg[0] == 0.:
                            subresult[name] = "Delicate"
                        if avg[0] == 2.:
                            subresult[name] = "Deep Clean"
                        else:
                            subresult[name] = "Normal"
                    elif name == "Usage_Frequency":
                        if avg[0] < 4:
                            subresult[name] = "Low"
                        elif avg[0] > 9:
                            subresult[name] = "High"
                        else:
                            subresult[name] = "Normal"
                    elif name == "Water_Hardness":
                        if avg[0] < 7.3:
                            subresult[name] = "Soft"
                        elif avg[0] > 14:
                            subresult[name] = "Hard"
                        else:
                            subresult[name] = "Normal"
                    elif name == "Temperature":
                        if avg[0] < 30:
                            subresult[name] = "Low"
                        elif avg[0] > 70:
                            subresult[name] = "High"
                        else:
                            subresult[name] = "Normal"

                # Washing powder, water hardness level, and washing powder fill level
                if subresult["Washing_Powder_Fill_Level"] == "High":
                    if subresult["Water_Hardness"] == "Soft":
                        msg_powder = "The amount of washing powder can further be reduced to save detergent."
                    elif subresult["Water_Hardness"] == "Normal":
                        if subresult["Washing_Powder"] == "Weak":
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                        else:
                            msg_powder = "The amount of washing powder can further be reduced to save detergent."
                    else:
                        if subresult["Washing_Powder"] == "Weak":
                            msg_powder = "The type of washing powder is too weak against hard water. Consider buying" \
                                         "a stronger type."
                        elif subresult["Washing_Powder"] == "Normal":
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                        else:
                            msg_powder = "The amount of washing powder can further be reduced to save detergent."
                elif subresult["Washing_Powder_Fill_Level"] == "Low":
                    if subresult["Water_Hardness"] == "Soft":
                        if subresult["Washing_Powder"] == "Strong" or subresult["Washing_Powder"] == "Normal":
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                        else:
                            msg_powder = "The type of washing powder is too weak against hard water. Consider buying a stronger type" \
                                         "or adding more detergent."
                    elif subresult["Water_Hardness"] == "Normal":
                        if subresult["Washing_Powder"] == "Weak" or subresult["Washing_Powder"] == "Normal":
                            msg_powder = "Consider buying a stronger washing powder or adding more detergent."
                        else:
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                    else:
                        if subresult["Washing_Powder"] == "Weak" or subresult["Washing_Powder"] == "Normal":
                            msg_powder = "Consider buying a stronger washing powder or adding more detergent."
                        else:
                            msg_powder = "Not enough detergent, consider adding more to clean clothes optimally."
                else:
                    if subresult["Water_Hardness"] == "Normal":
                        if subresult["Washing_Powder"] == "Weak":
                            msg_powder = "Consider buying a stronger washing powder or adding more detergent."
                        elif subresult["Washing_Powder"] == "Normal":
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                        else:
                            msg_powder = "The amount of washing powder can further be reduced to save detergent."
                    elif subresult["Water_Hardness"] == "Soft":
                        if subresult["Washing_Powder"] == "Weak":
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                        else:
                            msg_powder = "The amount of washing powder can further be reduced to save detergent."
                    else:
                        if subresult["Washing_Powder"] == "Strong":
                            msg_powder = "The amount and type of washing powder is optimal for current water hardness level."
                        else:
                            msg_powder = "Consider buying a stronger washing powder or adding more detergent."

                # Temperature and used modes
                if subresult["Temperature"] == "Normal":
                    if subresult["Used_Modes"] == "Delicate":
                        msg_mode = "The most frequently used mode is Delicate mode. Measured temperature is too high: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                    " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."
                    elif subresult["Used_Modes"] == "Normal":
                        msg_mode = "The most frequently used mode is Normal mode. Temperature is correctly measured."
                    else:
                        msg_mode = "The most frequently used mode is Deep Clean mode. Measured temperature is too low: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                    " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."
                elif subresult["Temperature"] == "Low":
                    if subresult["Used_Modes"] == "Delicate":
                        msg_mode = "The most frequently used mode is Delicate mode. Temperature is correctly measured."
                    elif subresult["Used_Modes"] == "Normal":
                        msg_mode = "The most frequently used mode is Normal mode. Measured temperature is too low: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                   " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."
                    else:
                        msg_mode = "The most frequently used mode is Deep Clean mode. Measured temperature is too low: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                   " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."
                else:
                    if subresult["Used_Modes"] == "Delicate":
                        msg_mode = "The most frequently used mode is Delicate mode. Measured temperature is too high: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                   " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."
                    elif subresult["Used_Modes"] == "Normal":
                        msg_mode = "The most frequently used mode is Normal mode. Measured temperature is too high: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                   " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."
                    else:
                        msg_mode = "The most frequently used mode is Deep Clean mode. Measured temperature is too high: check the " \
                                   + program_instances[selected_program]["actuators"] + \
                                   " or " + ', '.join(program_instances[selected_program]["sensors"]) + " for possible defects."

                # Laundry Fill
                if subresult["Laundry_Fill_Level"] == "Normal":
                    msg_fill = "Amount of laundry is optimal."
                elif subresult["Laundry_Fill_Level"] == "Low":
                    msg_fill = "More laundry can be added for more efficient washing."
                else:
                    msg_fill = "Consider reducing the amount of laundry."

                # Laundry Weight
                if subresult["Laundry_Weight"] == "Normal":
                    msg_weight = "Laundry weight is under recommended limit."
                else:
                    msg_weight = "Laundry is overweight, please reduce laundry weight to preserve system lifetime."

                # Usage Frequency
                if subresult["Usage_Frequency"] == "Normal":
                    msg_freq = "Washing frequency is optimal."
                elif subresult["Usage_Frequency"] == "Low":
                    msg_freq = "Washing machine is seldom used."
                else:
                    msg_freq = "Washing machine is used too frequently, consider reducing usage to protect components from" \
                               "possible degradation."

                subresult["Message"] = "| ".join([msg_fill, msg_weight, msg_powder, msg_freq, msg_mode])
                subresult["Time"] = get_time_string(graph_session, selected_program)

            # Save all results of each program into a dictionary
            result_program[selected_program] = subresult

    print(result_program)

    # Save results as a json file
    with open('result.json', 'w') as f:
        json.dump(result_program, f)

    graph_session.close()
    return result_program


