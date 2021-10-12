'''This module accesses the system context model from querying and updates to analyze context values, producing inferred
states, and getting the appropriate message from the application model.
'''

import json
import time as sys_time
import os
from neo4j import GraphDatabase


def get_values(session, program_name, cur_time):
    query = """MATCH (n:n4sch__Instance{mode:$program})-
    [:HAS_AVERAGE_VALUE]-(v) 
    WHERE v.time = datetime($time) AND v.checked = 0
    SET v.checked = 1 
    RETURN DISTINCT n.n4sch__name, v.value, v.phase, v.unit"""
    value_result = session.run(query, program=program_name, time=cur_time)

    res = dict()
    for res_item in value_result:
        if res_item[0] not in res:
            res[res_item[0]] = {res_item[2]: res_item[1], "unit": res_item[3]}
        else:
            res[res_item[0]].update({res_item[2]: res_item[1], "unit": res_item[3]})
    return res


def get_time(session, program_name):
    query = """
            MATCH (d:n4sch__Instance)-[:HAS_AVERAGE_VALUE]-(v:n4sch__Value)
            WHERE d.mode = $program and v.checked = 0
            RETURN DISTINCT toString(v.time)
            """
    time_result = session.run(query, program=program_name)

    return time_result


def get_latest_time(session, program_name):
    query = """
            MATCH (d:n4sch__Instance)-[:HAS_AVERAGE_VALUE]-(v:n4sch__Value)
            WHERE d.mode = $program
            RETURN DISTINCT toString(max(v.time))
            """
    time_result = session.run(query, program=program_name)

    return time_result


def check_anomaly(session, states):
    # Format list of dictionaries to match the Cypher query format
    defect = session.run("""
        WITH $states as nodes
        UNWIND nodes as node
        MATCH (st:n4sch__Instance{n4sch__name:node.name, source:node.source}) - [:HAS_COMBINATION] - (co) - [:CAUSES_ANOMALY] - (a)
        WITH a, co, size(nodes) as inputCnt, count(DISTINCT st) as cnt
        WHERE cnt = inputCnt
        RETURN a.n4sch__name, co.combo_id
    """, states=states)
    return defect


def check_suggestion(session, states):
    suggestions = session.run("""
        WITH $states as nodes
        UNWIND nodes as node
        MATCH (st:n4sch__Instance{n4sch__name:node.name, source:node.source}) - [:HAS_COMBINATION] - (co) - [:SUGGESTS] - (a)
        WITH a, co, size(nodes) as inputCnt, count(DISTINCT st) as cnt
        WHERE cnt = inputCnt
        RETURN a.n4sch__name
    """, states=states)
    return suggestions


def get_anomaly_message(session, program, message_cause, message_type):
    if message_type.lower() == "error":
        if "actuator" in message_cause.lower():
            component = "Actuator"
        elif "sensor" in message_cause.lower():
            component = "Sensor"
        else:
            component = ""
        message = session.run("""MATCH (e:n4sch__Instance{mode: $program})-[:IS_TYPE]-(:n4sch__Class{n4sch__name:$component})
            WITH collect(e.n4sch__name) as components
            MATCH (m) - [:IS_TYPE] - (:n4sch__Class{n4sch__name:"Message"})
            WHERE $message_cause in m.cause
            RETURN replace(m.message, "-foo-", apoc.text.join(components, ', '))""",
                    component=component, program=program,
                    message_cause=message_cause)
    elif message_type.lower() == "normal":
        message = session.run("""WITH ["Actuator", "Sensor"] as components
            UNWIND components as component
            MATCH (e:n4sch__Instance{mode:$program})-[:IS_TYPE]-(:n4sch__Class{n4sch__name:component})
            WITH collect(e.n4sch__name) as components
            MATCH (m:n4sch__Instance{n4sch__name:"Normal message"}) - [:IS_TYPE] - (:n4sch__Class{n4sch__name:"Message"})
            RETURN replace(m.message, "-foo-", apoc.text.join(components, ', '))""",
                    program=program)
    else:
        print("Message type needs to be either 'error' or  'normal'.")
    return message


def get_suggestion_message(session, context, message_cause, message_type):
    if message_type.lower() == "optimal":
        message = session.run("""WITH $context as context
                    MATCH (m:n4sch__Instance{n4sch__name:"Optimal message"}) - [:IS_TYPE] - (:n4sch__Class{n4sch__name:"Message"})
                    RETURN replace(m.message, "-foo-", apoc.text.join(context, ', '))""", context=context)
    elif message_type.lower() == "suggestion":
        message = session.run("""WITH $message_cause as cause
                    UNWIND cause as cs
                    MATCH (m) - [:IS_TYPE] - (:n4sch__Class{n4sch__name:"Message"})
                    WHERE cs in m.cause
                    RETURN m.message""", message_cause=message_cause)
    else:
        print("Message type needs to be either 'optimal' or 'suggestion'.")
    return message


def update_time_property(session, combo_id, message_cause, program, time):
    if "actuator" in message_cause.lower():
        component = "Actuator"
    elif "sensor" in message_cause.lower():
        component = "Sensor"
    else:
        component = ""
    session.run("""MATCH (e:n4sch__Instance{mode: $program})-[:IS_TYPE]-(:n4sch__Class{n4sch__name:$component})
            MATCH (cs:n4sch__Instance{n4sch__name:$message_cause})
            MERGE (e) - [r:HAS_DEFECT] -> (cs)
            ON CREATE SET r.time = []
            ON MATCH SET r.time = CASE WHEN NOT datetime($time) IN r.time THEN r.time + datetime($time) END
            """, program=program, component=component,
                message_cause=message_cause, time=time)

    session.run("""MATCH (co:n4sch__Combination{combo_id:$id}) - [r:CAUSES_ANOMALY{mode:$program}] - (a)
            FOREACH(x in CASE WHEN datetime($time) in r.time THEN [] ELSE [1] END | 
                SET r.time = r.time + datetime($time));        
        """, id=combo_id, program=program, time=time)

    return


def update_state_time(session, program, current_state, time):
    for item in current_state:
        session.run("""MATCH (n:n4sch__Instance{n4sch__name:$source})-[r:YIELDS_STATE]-(m:n4sch__Instance{n4sch__name:$state})
        WHERE n.mode = $program
        SET r.time = CASE WHEN NOT datetime($time) IN r.time THEN r.time + datetime($time) ELSE r.time END""",
                    source=item['source'], state=item['name'], program=program, time=time)
    return


def update_value_ranges(session):
    session.run("""MATCH (n:n4sch__Instance)-[:HAS_AVERAGE_VALUE]-(v:n4sch__Value) 
        MATCH (n)-[r:YIELDS_STATE]-(m)
        WHERE v.time in r.time
        WITH n.mode as program, n.n4sch__name as context_element, v.phase as phase, "range_phase_" + v.phase as phase_range, m as m, MIN(v.value) AS min_value, MAX(v.value) as max_value
        CALL apoc.create.setProperty(m, phase_range, [min_value, max_value]) YIELD node RETURN node""")
    return


def check_real_value_range(session, context, value, state, program):
    print("Checking: ", context, value)
    print("Current state: ", state)
    query_result = session.run("""MATCH (m:n4sch__Instance{mode:$program})-[:YIELDS_STATE]-(n) 
            WHERE ANY(x IN KEYS(n) WHERE x =~"range_phase.*") AND n.source = $context_element 
            WITH n, [x IN KEYS(n) WHERE x =~"range_phase.*" | x] AS nKeys
            RETURN n.n4sch__name as state, apoc.map.submap(n, nKeys) as submap
            """, context_element=context, program=program)

    if query_result.peek() is not None:
        state_range = dict()
        for item in query_result:
            state_range[item[0]] = item[1]

        print("Possible state ranges: ", state_range[state])

        if state in state_range:
            for ranges in state_range[state]:
                flag_warn = False
                if '1' in ranges and '1' in value:
                    if state_range[state][ranges][0] <= value['1'] <= state_range[state][ranges][1]:
                        print("Value of phase 1 is in the expected range.")
                    else:
                        flag_warn = True
                elif '2' in ranges and '2' in value:
                    if state_range[state][ranges][0] <= value['2'] <= state_range[state][ranges][1]:
                        print("Value of phase 2 is in the expected range.")
                    else:
                        flag_warn = True
                elif '3' in ranges and '3' in value:
                    if state_range[state][ranges][0] <= value['3'] <= state_range[state][ranges][1]:
                        print("Value of phase 3 is in the expected range.")
                    else:
                        flag_warn = True
                else:
                    print("Phase does not exist.")
            if flag_warn:
                print("Warning: value is outside of the normally outputted range. Check the data and components "
                      "for possible underlying cause of concern.")
            else:
                update_value_ranges(session)
        else:
            print("No range per phase is recorded yet for this context element.")

    return


def analyze_context(uri, username, password, db_name):
    # Connect to graph database
    graph_driver = GraphDatabase.driver(uri, auth=(username, password))
    graph_session = graph_driver.session(database=db_name)
    print("Connected.")

    # Get program names
    query_res = graph_session.run("""MATCH (:n4sch__Class{n4sch__name:"Context"})<-[:n4sch__SCO]-(m)-[:IS_TYPE]-(n:n4sch__Instance) WHERE size(n.mode) > 2 
            RETURN DISTINCT n.mode""")
    programs = list()
    for item in query_res:
        programs.append(item[0])

    # Query the graph database for latest measurements of each program
    result_program = dict()
    count_incomplete = 0 # If context data are incomplete, count them

    # Get results of all previously run programs, if exist
    if os.path.exists("result_program.json"):
        with open('result_program.json', 'r') as fb:
            all_results = json.load(fb)
    else:
        all_results = dict((el, []) for el in programs)

    # Start counting execution time
    t0 = sys_time.process_time()
    for selected_program in programs:

        # Get only the un-analyzed values of the selected program
        query_time = get_time(graph_session, selected_program)
        time_list = list()

        for item in query_time:
            time_list.append(item[0])

        if len(time_list) > 0:
            program_results = list()

            # Creating states based on values, with conditions depending on each program
            if selected_program == "Pump Out Program":
                for time in time_list:
                    subresult = dict()
                    values = get_values(graph_session, selected_program, time)
                    current_state = list()

                    if len(values) < 2:
                        count_incomplete += 1
                    else:
                        for key, value in values.items():
                            if key == 'Water_Level':
                                if value['1'] - value['3'] <= 30:
                                    subresult[key] = 'High'
                                else:
                                    subresult[key] = 'Low'
                            else:
                                if value['2'] == 0:
                                    subresult[key] = 'No Flow'
                                else:
                                    subresult[key] = 'Flow OK'
                            check_real_value_range(session=graph_session, context=key,
                                                   value=value, state=subresult[key], program=selected_program)
                            current_state.append({'name': subresult[key], 'source': key})

                        # Update state time for the YIELDS_STATE relationship
                        update_state_time(session=graph_session, program=selected_program, current_state=current_state, time=time)

                        # Check for anomaly based on current states
                        defect = check_anomaly(session=graph_session, states=current_state)
                        if defect.peek() is not None:
                            # Get anomaly message
                            msg_list = list()
                            for item in defect:
                                subresult["Anomaly"] = item[0]
                                combo_id = item[1]

                            msg = get_anomaly_message(session=graph_session, program=selected_program, message_cause=subresult["Anomaly"], message_type="Error")
                            for item in msg:
                                msg_list.append(item[0])

                            # Update the time property in the anomaly relationship with the current time
                            update_time_property(session=graph_session, message_cause=subresult["Anomaly"],
                                                 combo_id=combo_id, program=selected_program, time=time)
                        else:
                            # Get normal message
                            subresult["Anomaly"] = None
                            msg_list = list()
                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                message_cause="", message_type="Normal")
                            for item in msg:
                                msg_list.append(item[0])

                        subresult["Time"] = time
                        subresult["Message"] = msg_list
                        program_results.append(subresult)
            elif selected_program == "Door Lock Program":
                for time in time_list:
                    subresult = dict()
                    values = get_values(graph_session, selected_program, time)
                    current_state = list()

                    # Generate states based on average values
                    if len(values) < 2:
                        count_incomplete += 1
                    else:
                        for key, value in values.items():
                            if key == "Pressure":
                                if ((value['2'] - value['1'])/value['1']) >= 0.2:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "Low"
                            elif key == "Lock":
                                if value['2'] == 1:
                                    subresult[key] = "Locked"
                                else:
                                    subresult[key] = "Unlocked"
                            check_real_value_range(session=graph_session, context=key,
                                                   value=value, state=subresult[key], program=selected_program)
                            current_state.append({'name': subresult[key], 'source': key})

                        # Update state time for the YIELDS_STATE relationship
                        update_state_time(session=graph_session, program=selected_program,
                                              current_state=current_state, time=time)

                        # Check for anomaly based on current states
                        defect = check_anomaly(session=graph_session, states=current_state)
                        if defect.peek() is not None:
                            # Get anomaly message
                            msg_list = list()
                            for item in defect:
                                subresult["Anomaly"] = item[0]
                                combo_id = item[1]

                            msg = get_anomaly_message(session=graph_session, program=selected_program, message_cause=subresult["Anomaly"], message_type="Error")
                            for item in msg:
                                msg_list.append(item[0])

                            # Update the time property in the anomaly relationship with the current time
                            update_time_property(session=graph_session, message_cause=subresult["Anomaly"],
                                                 combo_id=combo_id, program=selected_program, time=time)
                        else:
                            # Get normal message
                            subresult["Anomaly"] = None
                            msg_list = list()
                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                message_cause="", message_type="Normal")
                            for item in msg:
                                msg_list.append(item[0])

                        subresult["Time"] = time
                        subresult["Message"] = msg_list
                        program_results.append(subresult)
            elif selected_program == "Fan Program":
                for time in time_list:
                    subresult = dict()
                    values = get_values(graph_session, selected_program, time)
                    current_state = list()

                    # Generate states based on average values
                    if len(values) < 3:
                        count_incomplete += 1
                    else:
                        for key, value in values.items():
                            if key == "Vibration":
                                if value['2'] <= 25:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "High"
                            elif key == "Loudness":
                                if ((value['2'] - value['1']) / value['1']) <= 0.75:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "High"
                            elif key == "Mass_Air_Flow":
                                if value['2'] >= 50:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "Low"
                            check_real_value_range(session=graph_session, context=key,
                                                   value=value, state=subresult[key], program=selected_program)
                            current_state.append({'name': subresult[key], 'source': key})

                        # Update state time for the YIELDS_STATE relationship
                        update_state_time(session=graph_session, program=selected_program,
                                              current_state=current_state, time=time)

                        # Check for anomaly based on current states
                        defect = check_anomaly(session=graph_session, states=current_state)
                        if defect.peek() is not None:
                            # Get anomaly message
                            msg_list = list()
                            for item in defect:
                                subresult["Anomaly"] = item[0]
                                combo_id = item[1]

                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause=subresult["Anomaly"], message_type="Error")
                            for item in msg:
                                msg_list.append(item[0])

                            # Update the time property in the anomaly relationship with the current time
                            update_time_property(session=graph_session, message_cause=subresult["Anomaly"],
                                                 combo_id=combo_id, program=selected_program, time=time)
                        else:
                            # Get normal message
                            subresult["Anomaly"] = None
                            msg_list = list()
                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause="", message_type="Normal")
                            for item in msg:
                                msg_list.append(item[0])

                        subresult["Time"] = time
                        subresult["Message"] = msg_list
                        program_results.append(subresult)
            elif selected_program == "Drum Motor Program":
                for time in time_list:
                    subresult = dict()
                    values = get_values(graph_session, selected_program, time)
                    current_state = list()

                    # Generate states based on average values
                    if len(values) < 2:
                        count_incomplete += 1
                    else:
                        for key, value in values.items():
                            if key == "Loudness":
                                if ((value['2'] - value['1']) / value['1']) <= 0.75:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "High"
                            elif key == "Vibration":
                                if value['2'] <= 25:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "High"
                            elif key == "Rotation_Speed":
                                if 50 <= value['2'] <= 60:
                                    subresult[key] = "Normal"
                                elif value['2'] < 50:
                                    subresult[key] = "Low"
                                else:
                                    subresult[key] = "High"
                            check_real_value_range(session=graph_session, context=key,
                                                   value=value, state=subresult[key], program=selected_program)
                            current_state.append({'name': subresult[key], 'source': key})

                        # Update state time for the YIELDS_STATE relationship
                        update_state_time(session=graph_session, program=selected_program,
                                              current_state=current_state, time=time)
                        # Check for anomaly based on current states
                        defect = check_anomaly(session=graph_session, states=current_state)
                        if defect.peek() is not None:
                            # Get anomaly message
                            msg_list = list()
                            for item in defect:
                                subresult["Anomaly"] = item[0]
                                combo_id = item[1]

                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause=subresult["Anomaly"], message_type="Error")
                            for item in msg:
                                msg_list.append(item[0])

                            # Update the time property in the anomaly relationship with the current time
                            update_time_property(session=graph_session, message_cause=subresult["Anomaly"],
                                                 combo_id=combo_id, program=selected_program, time=time)
                        else:
                            # Get normal message
                            subresult["Anomaly"] = None
                            msg_list = list()
                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause="", message_type="Normal")
                            for item in msg:
                                msg_list.append(item[0])

                        subresult["Time"] = time
                        subresult["Message"] = msg_list
                        program_results.append(subresult)
            elif selected_program == "Water Inlet Program":
                for time in time_list:
                    subresult = dict()
                    values = get_values(graph_session, selected_program, time)
                    current_state = list()

                    # Generate states based on average values
                    if len(values) < 2:
                        count_incomplete += 1
                    else:
                        for key, value in values.items():
                            if key == "Water_Level":
                                if value['3'] - value['1'] >= 20:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "Low"
                            elif key == "Entrance_Water_Flow":
                                if value['3'] == 0.:
                                    subresult[key] = "No Flow"
                                else:
                                    subresult[key] = "Flow OK"
                            elif key == "Water_Hardness":
                                if value['3'] <= 14:
                                    subresult[key] = "Normal"
                                else:
                                    subresult[key] = "Hard"
                            check_real_value_range(session=graph_session, context=key,
                                                   value=value, state=subresult[key], program=selected_program)
                            current_state.append({'name': subresult[key], 'source': key})

                        # Update state time for the YIELDS_STATE relationship
                        update_state_time(session=graph_session, program=selected_program,
                                              current_state=current_state, time=time)

                        # Check for anomaly based on current states
                        defect = check_anomaly(session=graph_session, states=current_state)
                        if defect.peek() is not None:
                            # Get anomaly message
                            msg_list = list()
                            for item in defect:
                                subresult["Anomaly"] = item[0]
                                combo_id = item[1]

                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause=subresult["Anomaly"], message_type="Error")
                            for item in msg:
                                msg_list.append(item[0])

                            # Update the time property in the anomaly relationship with the current time
                            update_time_property(session=graph_session, message_cause=subresult["Anomaly"],
                                                 combo_id=combo_id, program=selected_program, time=time)
                        else:
                            # Get normal message
                            subresult["Anomaly"] = None
                            msg_list = list()
                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause="", message_type="Normal")
                            for item in msg:
                                msg_list.append(item[0])


                        subresult["Time"] = time
                        subresult["Message"] = msg_list
                        program_results.append(subresult)
            elif selected_program == "Long Time Check":
                for time in time_list:
                    subresult = dict()
                    values = get_values(graph_session, selected_program, time)
                    current_state_detergent = list()
                    current_state_modes = list()
                    current_state_laundry = list()
                    current_state_frequency = list()
                    # Generate states based on average values
                    if len(values) < 8:
                        count_incomplete += 1
                    else:
                        for key, value in values.items():
                            if key == "Laundry_Fill_Level":
                                if value['1'] > 75:
                                    subresult[key] = ["High", str(value['1']) + value['unit']]
                                elif value['1'] < 35:
                                    subresult[key] = ["Low", str(value['1']) + value['unit']]
                                else:
                                    subresult[key] = ["Normal", str(value['1']) + value['unit']]
                                current_state_laundry.append({'name': subresult[key][0], 'source': key})
                            elif key == "Laundry_Weight":
                                if value['1'] > 10:
                                    subresult[key] = ["High", str(value['1']) + ' ' + value['unit']]
                                else:
                                    subresult[key] = ["Low", str(value['1']) + ' ' + value['unit']]
                                current_state_laundry.append({'name': subresult[key][0], 'source': key})
                            elif key == "Washing_Powder_Fill_Level":
                                if value['1'] > 75:
                                    subresult[key] = ["High", str(value['1']) + value['unit']]
                                elif value['1'] < 35:
                                    subresult[key] = ["Low", str(value['1']) + value['unit']]
                                else:
                                    subresult[key] = ["Normal", str(value['1']) + value['unit']]
                                current_state_detergent.append({'name': subresult[key][0], 'source': key})
                            elif key == "Washing_Powder":
                                if value['1'] == 0.:
                                    subresult[key] = ["Weak", "-"]
                                elif value['1'] == 1.:
                                    subresult[key] = ["Normal", "-"]
                                else:
                                    subresult[key] = ["Strong", "-"]
                                current_state_detergent.append({'name': subresult[key][0], 'source': key})
                            elif key == "Used_Modes":
                                if value['1'] == 0.:
                                    subresult[key] = ["Delicate", "-"]
                                if value['1'] == 2.:
                                    subresult[key] = ["Deep Clean", "-"]
                                else:
                                    subresult[key] = ["Normal", "-"]
                                current_state_modes.append({'name': subresult[key][0], 'source': key})
                            elif key == "Usage_Frequency":
                                if value['1'] < 4:
                                    subresult[key] = ["Low", str(value['1']) + " times/week"]
                                elif value['1'] > 9:
                                    subresult[key] = ["High", str(value['1']) + " times/week"]
                                else:
                                    subresult[key] = ["Normal", str(value['1']) + " times/week"]
                                current_state_frequency.append({'name': subresult[key][0], 'source': key})
                            elif key == "Water_Hardness":
                                if value['1'] < 7.3:
                                    subresult[key] = ["Soft", str(value['1']) + value['unit']]
                                elif value['1'] > 14:
                                    subresult[key] = ["Hard", str(value['1']) + value['unit']]
                                else:
                                    subresult[key] = ["Normal", str(value['1']) + value['unit']]
                                current_state_detergent.append({'name': subresult[key][0], 'source': key})
                            elif key == "Temperature":
                                if value['1'] < 30:
                                    subresult[key] = ["Low", str(value['1']) + value['unit'] + 'C']
                                elif value['1'] > 70:
                                    subresult[key] = ["High", str(value['1']) + value['unit'] + 'C']
                                else:
                                    subresult[key] = ["Normal", str(value['1']) + value['unit'] + 'C']
                                current_state_modes.append({'name': subresult[key][0], 'source': key})
                            check_real_value_range(session=graph_session, context=key,
                                                   value=value, state=subresult[key][0], program=selected_program)

                        # Update state time for the YIELDS_STATE relationship
                        update_state_time(session=graph_session, program=selected_program,
                                          current_state=current_state_modes, time=time)
                        update_state_time(session=graph_session, program=selected_program,
                                          current_state=current_state_laundry, time=time)
                        update_state_time(session=graph_session, program=selected_program,
                                          current_state=current_state_detergent, time=time)
                        update_state_time(session=graph_session, program=selected_program,
                                          current_state=current_state_frequency, time=time)

                        # Check for anomaly based on current states
                        defect = check_anomaly(session=graph_session, states=current_state_modes)
                        if defect.peek() is not None:
                            # Get anomaly message
                            msg_list = list()
                            for item in defect:
                                subresult["Anomaly"] = item[0]
                                combo_id = item[1]

                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause=subresult["Anomaly"], message_type="Error")
                            for item in msg:
                                msg_list.append(item[0])

                            # Update the time property in the anomaly relationship with the current time
                            update_time_property(session=graph_session, message_cause=subresult["Anomaly"],
                                                 combo_id=combo_id, program=selected_program, time=time)
                        else:
                            # Get normal message
                            subresult["Anomaly"] = None
                            msg_list = list()
                            msg = get_anomaly_message(session=graph_session, program=selected_program,
                                                      message_cause="", message_type="Normal")
                            for item in msg:
                                msg_list.append(item[0])

                        # Check for suggestions
                        checked_suggestion_states = [current_state_detergent, current_state_laundry, current_state_frequency]
                        suggestion_list = list()
                        for state in checked_suggestion_states:
                            cause_list = list()
                            suggestion = check_suggestion(session=graph_session, states=state)
                            if suggestion.peek() is not None:
                                # Get suggestion message
                                for item in suggestion:
                                    cause_list.append(item[0])
                                context = list()
                                for j in range(len(state)):
                                    context.append(state[j]['source'])
                                msg = get_suggestion_message(session=graph_session, context=context,
                                                              message_cause=cause_list, message_type="suggestion")
                                for item in msg:
                                    msg_list.append(item[0])
                                suggestion_list.append(cause_list)
                            else:
                                # Get optimal message
                                context = list()
                                for j in range(len(state)):
                                    context.append(state[j]['source'])

                                msg = get_suggestion_message(session=graph_session, context=context,
                                                          message_cause="", message_type="optimal")
                                for item in msg:
                                    msg_list.append(item[0])
                        subresult["Suggestion"] = [y for x in suggestion_list for y in x]
                        subresult["Time"] = time
                        subresult["Message"] = msg_list

                        program_results.append(subresult)
            else:
                pass
            result_program[selected_program] = program_results
            for i in program_results:
                all_results[selected_program].append(i)

        else:
            print("No new data is found for program", selected_program, ".")

    t1 = sys_time.process_time() - t0

    # Update graph with the anomaly weights
    graph_session.run('''MATCH (n:n4sch__Instance)-[r:HAS_DEFECT]->(m:n4sch__Instance)
    WITH n, size(r.time) as count_defects
    SET n.anomaly_weight = count_defects''')

    # Overwrite old json file with newly appended data
    with open('result_program.json', 'w') as f:
        json.dump(all_results, f)

    # Get latest results only
    result_latest = dict()
    for program, program_result in all_results.items():
        query_latest = get_latest_time(graph_session, program)
        for item in query_latest:
            latest_program_time = item[0]
        for i in program_result:
            if latest_program_time in i["Time"]:
                result_latest[program] = [i]
    print("Analysis done in ", t1, " seconds.")
    graph_session.close()
    return result_latest