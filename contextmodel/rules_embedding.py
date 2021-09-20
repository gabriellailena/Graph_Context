import sys
import random
from neo4j import GraphDatabase
from itertools import product


def create_anomaly_rels(session, defect_name, program_name, state, context, combo_id):
    session.run("""
        WITH $defect as dnames
        UNWIND dnames as dname
        MATCH (ai:n4sch__Instance{n4sch__name: dname})
        MERGE (co:n4sch__Combination{n4sch__name:'State Combination', combo_id:$combo_id, mode: $program})
        MERGE (st:n4sch__Instance{n4sch__name:$state, source: $context})
        MERGE (st) - [:HAS_COMBINATION] - (co)
        MERGE (co) - [:CAUSES_ANOMALY{mode: $program, time: []}] -> (ai)
        """, state=state, defect=defect_name, program=program_name, context=context, combo_id=combo_id)
    return


def create_suggestion_rels(session, node_name, program_name, state, context, combo_id):
    if combo_id != 0:
        session.run("""
            WITH $node as nnames
            UNWIND nnames as nname
            MATCH (ai:n4sch__Instance{n4sch__name: nname})
            MERGE (co:n4sch__Combination{n4sch__name:'State Combination', combo_id:$combo_id, mode: $program})
            MERGE (st:n4sch__Instance{n4sch__name:$state, source: $context})
            MERGE (st) - [:HAS_COMBINATION] - (co)
            MERGE (co) - [:SUGGESTS{mode: $program}] -> (ai)
            """, state=state, node=node_name, program=program_name, context=context, combo_id=combo_id)
    return


def rules_to_graph(uri, username, password, db_name):

    # Connect to graph database
    try:
        graph_driver = GraphDatabase.driver(uri, auth=(username, password))
        graph_session = graph_driver.session(database=db_name)

        # Get program names
        query_res = graph_session.run("""MATCH (:n4sch__Class{n4sch__name:"Context"})<-[:n4sch__SCO]-(m)-[:IS_TYPE]-(n:n4sch__Instance) WHERE size(n.mode) > 2 
                    RETURN DISTINCT n.mode""")
        programs = list()
        for item in query_res:
            programs.append(item[0])

        random.seed(0)
        for program in programs:
            print(program)
            if program == "Pump Out Program":
                state1 = ['High', 'Low']
                state2 = ['No Flow', 'Flow OK']
                state_combinations = list(product(state1, state2))
                for item in state_combinations:
                    flags_anomaly = {'actuator': False, 'sensor': False}
                    current_state = {'Water_Level': item[0], 'Exit_Water_Flow': item[1]}
                    id = "ca" + str(random.randint(0, 1000))
                    if current_state['Water_Level'] == 'High':
                        if current_state['Exit_Water_Flow'] == 'No Flow':
                            flags_anomaly['actuator'] = True
                        else:
                            flags_anomaly['sensor'] = True
                    else:
                        if current_state['Exit_Water_Flow'] == 'No Flow':
                            flags_anomaly['sensor'] = True
                        else:
                            pass
                    # Create relationships between state and current context data

                    if flags_anomaly["actuator"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Actuator Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["sensor"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Sensor Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    else:
                        pass
            elif program == "Door Lock Program":
                state1 = ['Normal', 'Low']
                state2 = ['Locked', 'Unlocked']
                state_combinations = list(product(state1, state2))
                for item in state_combinations:
                    id = "ca" + str(random.randint(0, 1000))
                    current_state = {'Pressure': item[0], 'Lock': item[1]}
                    flags_anomaly = {'actuator': False, 'sensor': False}
                    if current_state['Pressure'] == 'Normal':
                        if current_state['Lock'] == 'Locked':
                            # normal: do nothing
                            pass
                        else:
                            flags_anomaly['sensor'] = True
                    else:
                        if current_state['Lock'] == 'Locked':
                            flags_anomaly['sensor'] = True
                        else:
                            flags_anomaly['actuator'] = True

                    if flags_anomaly["actuator"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Actuator Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["sensor"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Sensor Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    else:
                        pass
            elif program == "Fan Program":
                state1 = ['Normal', 'High']
                state2 = ['Normal', 'High']
                state3 = ['Normal', 'Low']
                state_combinations = list(product(state1, state2, state3))
                for item in state_combinations:
                    id = "ca" + str(random.randint(0, 1000))
                    current_state = {'Loudness': item[0], 'Vibration': item[1], 'Mass_Air_Flow': item[2]}
                    flags_anomaly = {"actuator": False, "position": False, "object": False}
                    if all(i == 'Normal' for i in current_state.values()):
                        # normal: do nothing
                        pass
                    elif ('Normal', 'High', 'Normal') == item:
                        flags_anomaly['position'] = True
                    elif ('High', 'High', 'Normal') == item:
                        flags_anomaly['object'] = True
                    else:
                        flags_anomaly['actuator'] = True

                    if flags_anomaly["actuator"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Actuator Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["position"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Position",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["object"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Foreign Object",
                                                program_name=program, context=key, state=value, combo_id=id)
                    else:
                        pass
            elif program == "Drum Motor Program":
                state1 = ['Normal', 'High']
                state2 = ['Normal', 'High']
                state3 = ['Normal', 'Low', 'High']
                state_combinations = list(product(state1, state2, state3))
                for item in state_combinations:
                    id = "ca" + str(random.randint(0, 1000))
                    current_state = {'Loudness': item[0], 'Vibration': item[1], 'Rotation_Speed': item[2]}
                    flags_anomaly = {"actuator": False, "position": False, "object": False, "undefined": False, "power_supply": False}
                    
                    if current_state['Loudness'] == 'Normal':
                        if current_state['Vibration'] == 'Normal':
                            if current_state['Rotation_Speed'] == 'Normal':
                                # normal: do nothing
                                pass
                            else:
                                flags_anomaly['actuator'] = True
                        elif current_state['Vibration'] == 'High':
                            if current_state['Rotation_Speed'] == 'High':
                                flags_anomaly['actuator'] = True
                            else:
                                flags_anomaly['position'] = True
                    elif current_state['Loudness'] == 'High':
                        if current_state['Vibration'] == 'Normal':
                            if current_state['Rotation_Speed'] == 'Normal':
                                flags_anomaly['undefined'] = True
                            else:
                                flags_anomaly['actuator'] = True
                        elif current_state['Vibration'] == 'High':
                            if current_state['Rotation_Speed'] == 'Low':
                                flags_anomaly['object'] = True
                            else:
                                flags_anomaly['power_supply'] = True

                    if flags_anomaly["actuator"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Actuator Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["position"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Position",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["object"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Foreign Object",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["power_supply"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Power Supply",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly['undefined']:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Undefined",
                                                program_name=program, context=key, state=value, combo_id=id)
                    else:
                        pass
            elif program == "Water Inlet Program":
                state1 = ['Normal', 'Low']
                state2 = ['No Flow', 'Flow OK']
                state3 = ['Normal', 'High']
                state_combinations = list(product(state1, state2, state3))
                for item in state_combinations:
                    id = "ca" + str(random.randint(0, 1000))
                    flags_anomaly = {'actuator': False, 'sensor': False, 'hard_water': False}
                    current_state = {'Water_Level': item[0], 'Entrance_Water_Flow': item[1], 'Water_Hardness': item[2]}
                    if current_state['Water_Level'] == 'Normal':
                        if current_state['Entrance_Water_Flow'] == 'Flow OK':
                            # normal: do nothing
                            pass
                        else:
                            flags_anomaly['sensor'] = True
                    else:
                        if current_state['Entrance_Water_Flow'] == 'Flow OK':
                            flags_anomaly['sensor'] = True
                        else:
                            flags_anomaly['actuator'] = True

                    if flags_anomaly["actuator"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Actuator Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["sensor"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Sensor Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly["hard_water"]:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Hard Water",
                                                program_name=program, context=key, state=value, combo_id=id)
                    else:
                        pass
            elif program == "Long Time Check":
                # Detergent fill level, detergent type, and water hardness
                detergent_fill = ['Normal', 'Low', 'High']
                detergent_type = ['Weak', 'Normal', 'Strong']
                water_hardness = ['Normal', 'Soft', 'Hard']
                state_combinations = list(product(detergent_fill,"Washing_Powder", water_hardness))
                for item in state_combinations:
                    id = "cs" + str(random.randint(0, 1000))
                    flags_suggestion = {'reduce_detergent': False, 'stronger_more_detergent': False}
                    current_state = {'Washing_Powder_Fill_Level': item[0], "Washing_Powder": item[1], 'Water_Hardness': item[2]}
                    if current_state["Washing_Powder_Fill_Level"] == "High":
                        if current_state["Water_Hardness"] == "Soft":
                            flags_suggestion['reduce_detergent'] = True
                        elif current_state["Water_Hardness"] == "Normal":
                            if current_state["Washing_Powder"] == "Weak":
                                # optimal: do nothing
                                pass
                            else:
                                flags_suggestion['reduce_detergent'] = True
                        else:
                            if current_state["Washing_Powder"] == "Weak":
                                flags_suggestion['stronger_more_detergent'] = True
                            elif current_state["Washing_Powder"] == "Normal":
                                # optimal: do nothing
                                pass
                            else:
                                flags_suggestion['reduce_detergent'] = True
                    elif current_state["Washing_Powder_Fill_Level"] == "Low":
                        if current_state["Water_Hardness"] == "Soft":
                            if current_state["Washing_Powder"] == "Strong" or current_state["Washing_Powder"] == "Normal":
                                # optimal: do nothing
                                pass
                            else:
                                flags_suggestion['stronger_more_detergent'] = True
                        elif current_state["Water_Hardness"] == "Normal":
                            if current_state["Washing_Powder"] == "Weak" or current_state["Washing_Powder"] == "Normal":
                                flags_suggestion['stronger_more_detergent'] = True
                            else:
                                # optimal: do nothing
                                pass
                        else:
                            flags_suggestion['stronger_more_detergent'] = True
                    else:
                        if current_state["Water_Hardness"] == "Normal":
                            if current_state["Washing_Powder"] == "Weak":
                                flags_suggestion['stronger_more_detergent'] = True
                            elif current_state["Washing_Powder"] == "Normal":
                                # optimal: do nothing
                                pass
                            else:
                                flags_suggestion['reduce_detergent'] = True
                        elif current_state["Water_Hardness"] == "Soft":
                            if current_state["Washing_Powder"] == "Weak":
                                # optimal: do nothing
                                pass
                            else:
                                flags_suggestion['reduce_detergent'] = True
                        else:
                            if current_state["Washing_Powder"] == "Strong":
                                # optimal: do nothing
                                pass
                            else:
                                flags_suggestion['stronger_more_detergent'] = True

                    if flags_suggestion['reduce_detergent']:
                        for key, value in current_state.items():
                            create_suggestion_rels(session=graph_session, node_name="Reduce Detergent",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_suggestion['stronger_more_detergent']:
                        for key, value in current_state.items():
                            create_suggestion_rels(session=graph_session, node_name="Stronger/More Detergent",
                                                   program_name=program, context=key, state=value, combo_id=id)
                    else:
                        pass

                # Temperature and used modes
                temperature = ['Normal', 'Low', 'High']
                modes = ['Delicate', 'Normal', 'Deep Clean']
                state_combinations = list(product(temperature, modes))
                for item in state_combinations:
                    id = "ca" + str(random.randint(0, 1000))
                    current_state = {'Temperature': item[0], 'Used_Modes': item[1]}
                    flags_anomaly = {'actuator': False, 'sensor': False}
                    if current_state["Temperature"] == "Normal":
                        if current_state["Used_Modes"] == "Delicate":
                            flags_anomaly['actuator'] = True
                            flags_anomaly['sensor'] = True
                        elif current_state["Used_Modes"] == "Normal":
                            # normal: do nothing
                            pass
                        else:
                            flags_anomaly['actuator'] = True
                            flags_anomaly['sensor'] = True
                    elif current_state["Temperature"] == "Low":
                        if current_state["Used_Modes"] == "Delicate":
                            # normal: do nothing
                            pass
                        elif current_state["Used_Modes"] == "Normal":
                            flags_anomaly['actuator'] = True
                            flags_anomaly['sensor'] = True
                        else:
                            flags_anomaly['actuator'] = True
                            flags_anomaly['sensor'] = True
                    else:
                        if current_state["Used_Modes"] == "Delicate":
                            flags_anomaly['actuator'] = True
                            flags_anomaly['sensor'] = True
                        elif current_state["Used_Modes"] == "Normal":
                            flags_anomaly['actuator'] = True
                            flags_anomaly['sensor'] = True
                        else:
                            # normal: do nothing
                            pass

                    if flags_anomaly['actuator']:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Actuator Defect",
                                                program_name=program, context=key, state=value, combo_id=id)
                    elif flags_anomaly['sensor']:
                        for key, value in current_state.items():
                            create_anomaly_rels(session=graph_session, defect_name="Sensor Defect",
                                                program_name=program, context=key, state=value, combo_id=id)

                # Laundry Fill
                laundry_fill = ['Normal', 'Low', 'High']
                laundry_weight = ['Low', 'High']
                state_combinations = list(product(laundry_fill, laundry_weight))
                for item in state_combinations:
                    id = "cs" + str(random.randint(0, 1000))
                    current_state = {'Laundry_Fill_Level': item[0], 'Laundry_Weight': item[1]}
                    if current_state["Laundry_Weight"] == "Low":
                        if current_state["Laundry_Fill_Level"] == "High":
                            # normal: do nothing
                            pass
                        else:
                            for key, value in current_state.items():
                                create_suggestion_rels(session=graph_session, node_name="Increase Laundry",
                                                       program_name=program,
                                                       state=value, context=key, combo_id=id)
                    else:
                        for key, value in current_state.items():
                            create_suggestion_rels(session=graph_session, node_name="Reduce Laundry", program_name=program,
                                                   state=value, context=key, combo_id=id)

                # Usage Frequency
                frequency = ['Normal', 'Low', 'High']
                for i in frequency:
                    id = "cs" + str(random.randint(0, 1000))
                    current_state = {'Usage_Frequency': i}
                    if current_state["Usage_Frequency"] == "Normal":
                        # optimal: do nothing
                        pass
                    elif current_state["Usage_Frequency"] == "Low":
                        create_suggestion_rels(session=graph_session, node_name="Run Diagnosis Programs", program_name=program,
                                               state=i, context='Usage_Frequency', combo_id=id)
                    else:
                        create_suggestion_rels(session=graph_session, node_name="Reduce Usage Frequency", program_name=program,
                                               state=i, context='Usage_Frequency', combo_id=id)
            ''' 
            -------------------------
            ADD NEW RULES HERE
            -------------------------
            elif program == "<program_name>":
                # Declare states of each source
                source1_state = [...]
                source2_state = [...]
                
                # Create combinations of states that will be checked for conditions
                state_combinations = list(product(source1_state, source2_state, ...))
                
                # For each combination, create the corresponding relationship to anomaly and/or suggestions (if any)
                for item in state_combinations:
                ...
                
            '''
        # Merge the created states with the State class
        graph_session.run('''MATCH (m:n4sch__Class{n4sch__name: "State"})
        MATCH (n:n4sch__Instance) WHERE exists(n.source)
        MERGE (n) - [:IS_TYPE] - (m)''')

        # Creates relationships between states to the context sources
        graph_session.run('''MATCH (n:n4sch__Instance)-[:IS_TYPE]-(:n4sch__Class{n4sch__name: "State"})
        MATCH (m:n4sch__Instance)-[:IS_TYPE]-(:n4sch__Class)-[:n4sch__SCO]-(:n4sch__Class{n4sch__name:"Context"})
        FOREACH(x in CASE WHEN n.source=m.n4sch__name THEN [1] ELSE [] END |    MERGE (m)-[:YIELDS_STATE{time:[]}]-(n))''')

        print("Rules embedding to the anomaly knowledge graph complete.")
    except:
        print("Cannot establish connection to graph database!")
        print(sys.exc_info()[0])
        raise
    finally:
        graph_session.close()
    return
