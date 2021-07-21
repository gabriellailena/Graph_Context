"""This module creates a JSON file containing extra necessary information on the instances related to a diagnosis program"""

import json

programs = ["Pump Out Program", "Door Lock Program", "Fan Program", "Drum Motor Program", "Water Inlet Program", "Long Time Check"]
info = dict((el, {"sensors": None, "actuators": None}) for el in programs)
for d_name in programs:
    if d_name == "Door Lock Program":
        sensor_names = ["Pressure Sensor", "Door Lock Sensor"]
        sensors = dict((el, {"states":""}) for el in sensor_names)
        sensors["Pressure Sensor"]["states"] = ["Low", "Normal"]
        sensors["Door Lock Sensor"]["states"] = ["Unlocked", "Locked"]
        info[d_name]["sensors"] = sensors
        info[d_name]["actuators"] = "Door Lock"
    elif d_name == "Drum Motor Program":
        sensor_names = ["Loudness Sensor", "Vibration Sensor", "Rotation Speed Sensor"]
        sensors = dict((el, {"states": ""}) for el in sensor_names)
        sensors["Loudness Sensor"]["states"] = ["Normal", "High"]
        sensors["Vibration Sensor"]["states"] = ["Normal", "High"]
        sensors["Rotation Speed Sensor"]["states"] = ["Low", "Normal", "High"]
        info[d_name]["sensors"] = sensors
        info[d_name]["actuators"] = "Drum Motor"
    elif d_name == "Fan Program":
        sensor_names = ["Loudness Sensor", "Vibration Sensor", "Mass Air Flow Sensor"]
        sensors = dict((el, {"states": ""}) for el in sensor_names)
        sensors["Loudness Sensor"]["states"] = ["Normal", "High"]
        sensors["Vibration Sensor"]["states"] = ["Normal", "High"]
        sensors["Mass Air Flow Sensor"]["states"] = ["Low", "Normal"]
        info[d_name]["sensors"] = sensors
        info[d_name]["actuators"] = "Blower"
    elif d_name == "Pump Out Program":
        sensor_names = ["Water Flow Sensor", "Water Fill Level Sensor"]
        sensors = dict((el, {"states": ""}) for el in sensor_names)
        sensors["Water Flow Sensor"]["states"] = ["No Flow", "Flow OK"]
        sensors["Water Fill Level Sensor"]["states"] = ["Low", "High"]
        info[d_name]["sensors"] = sensors
        info[d_name]["actuators"] = "Drain Pump"
    elif d_name == "Water Inlet Program":
        sensor_names = ["Water Flow Sensor", "Water Fill Level Sensor"]
        external_names = ["Water Hardness Level"]
        sensors = dict((el, {"states": ""}) for el in sensor_names)
        external = dict((el, {"states": ""}) for el in external_names)
        sensors["Water Fill Level Sensor"]["states"] = ["Low", "Normal"]
        sensors["Water Flow Sensor"]["states"] = ["No Flow", "Flow OK"]
        external["Water Hardness Level"]["states"] = ["Soft", "Normal", "Hard"]
        info[d_name]["sensors"] = sensors
        info[d_name]["external"] = external
        info[d_name]["actuators"] = "Water Inlet Valve"
    elif d_name == "Long Time Check":
        sensor_names = ["Temperature Sensor", "Laundry Fill Level Sensor", "Laundry Weight Sensor",
                        "Washing Powder Fill Level Sensor"]
        external_names = ["Water Hardness Level", "Washing Powder Type", "Usage Frequency", "Used Modes"]
        sensors = dict((el, {"states": ""}) for el in sensor_names)
        external = dict((el, {"states": ""}) for el in external_names)
        sensors["Temperature Sensor"]["states"] = ["Low", "Normal", "High"]
        sensors["Laundry Fill Level Sensor"]["states"] = ["Low", "Normal", "High"]
        sensors["Laundry Weight Sensor"]["states"] = ["Normal", "High"]
        sensors["Washing Powder Fill Level Sensor"]["states"] = ["Low", "Normal", "High"]
        external["Water Hardness Level"]["states"] = ["Soft", "Normal", "Hard"]
        external["Washing Powder Type"]["states"] = ["Weak", "Strong"]
        external["Usage Frequency"]["states"] = ["Low", "Normal", "High"]
        external["Used Modes"]["states"] = ["Delicate", "Normal", "Deep Clean"]
        info[d_name]["sensors"] = sensors
        info[d_name]["external"] = external

with open('programs.json', 'w') as f:
    json.dump(info, f)
