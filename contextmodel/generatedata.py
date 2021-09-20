import random
import pickle
import yaml
import os
from MySQLdb.times import Timestamp
from _datetime import datetime
 
def random_data(size, start_value, min_delta, max_delta, precision):
    value_range = max_delta - min_delta
    half_range = value_range / 2
    data_list = []
    for _ in range(size):
        delta = random.random() * value_range - half_range
        data_list.append(round(start_value + delta, precision))
    return data_list


def generate_all_data():

    
    try:
        #generated_data = random_data(size, start_value, min_delta, max_delta, precision)
        config = yaml.load(open('contextmodel\\genconfig.yaml'))
        c = "contextdata"
        
        #################
        #Pump Out Program
        #################
        
        #Water_Level
        #generating Data dependent on the configuration file
        value_config =  config[c]["Pump Out Program"]["Water_Level"]
        if(value_config == "normal"):
            Pump_Out_Water_Level_Ph1 = random_data(5, 50, -2, 2, 1)
            Pump_Out_Water_Level_Ph3 = random_data(5, 2, -2, 2, 1)
        elif(value_config == "toohigh"):
            Pump_Out_Water_Level_Ph1 = random_data(5, 2, -2, 2, 1)
            Pump_Out_Water_Level_Ph3 = random_data(5, 2, -2, 2, 1)
        now = datetime.now()
        Pump_Out_Water_Level_Ph1_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Pump_Out_Water_Level_Ph3_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Pump_Out_Water_Level_Unit = "%"
        
	#stores the generated data into file
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Pump Out Program" +"\\" + "Water_Level" + "\\" + "Water_Level_Ph1" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Pump_Out_Water_Level_Ph1, fp)
            pickle.dump(Pump_Out_Water_Level_Unit, fp)
            pickle.dump(Pump_Out_Water_Level_Ph1_Time, fp)
            
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Pump Out Program" +"\\"  + "Water_Level" + "\\" + "Water_Level_Ph3" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Pump_Out_Water_Level_Ph3, fp)
            pickle.dump(Pump_Out_Water_Level_Unit, fp)
            pickle.dump(Pump_Out_Water_Level_Ph3_Time, fp)
            
        value_config =  config[c]["Pump Out Program"]["Exit_Water_Flow"]
        Pump_Out_Exit_Water_Flow_Ph2 = []
        if(value_config == True):
            Pump_Out_Exit_Water_Flow_Ph2.append(1)
        elif(value_config == False):  
            Pump_Out_Exit_Water_Flow_Ph2.append(0)
        Pump_Out_Exit_Water_Flow_Unit = "true/false"
        Pump_Out_Exit_Water_Flow_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
            
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Pump Out Program" +"\\" + "Exit_Water_Flow" + "\\" + "Exit_Water_Flow_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Pump_Out_Exit_Water_Flow_Ph2, fp)
            pickle.dump(Pump_Out_Exit_Water_Flow_Unit, fp)
            pickle.dump(Pump_Out_Exit_Water_Flow_Ph2_Time, fp)
        
         
        #################
        #Fan  Program
        #################
        value_config =  config[c]["Fan Program"]["Loudness"]
        if(value_config == "normal"):
            Fan_Program_Loudness_Ph1 = random_data(10, 5, -1, 1, 1)
            Fan_Program_Loudness_Ph2 = random_data(10, 7, -1, 1, 1)
        elif(value_config == "toohigh"):
            Fan_Program_Loudness_Ph1 = random_data(10, 5, -2, 2, 1)
            Fan_Program_Loudness_Ph2 = random_data(10, 15, -2, 2, 1)
        
        Fan_Program_Loudness_Ph1_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Fan_Program_Loudness_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Fan_Program_Loudness_Unit = "dB"
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Fan Program" +"\\" + "Loudness" + "\\" + "Loudness_Ph1" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Fan_Program_Loudness_Ph1, fp)
            pickle.dump(Fan_Program_Loudness_Unit, fp)
            pickle.dump(Fan_Program_Loudness_Ph1_Time, fp)
            
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Fan Program" +"\\"  + "Loudness" + "\\" + "Loudness_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Fan_Program_Loudness_Ph2, fp)
            pickle.dump(Fan_Program_Loudness_Unit, fp)
            pickle.dump(Fan_Program_Loudness_Ph2_Time, fp)
        
        value_config =  config[c]["Fan Program"]["Vibration"]
        if(value_config == "normal"):
            Fan_Program_Vibration_Ph2 = random_data(10, 10, -2, 2, 1)
        elif(value_config == "toohigh"):
            Fan_Program_Vibration_Ph2 = random_data(10, 50, -2, 2, 1)
        
        Fan_Program_Vibration_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Fan_Program_Vibration_Unit = "%"
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Fan Program" +"\\" + "Vibration" + "\\" + "Vibration_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Fan_Program_Vibration_Ph2, fp)
            pickle.dump(Fan_Program_Vibration_Unit, fp)
            pickle.dump(Fan_Program_Vibration_Ph2_Time, fp)
            
        value_config =  config[c]["Fan Program"]["Mass_Air_Flow"]
        if(value_config == "normal"):
            Fan_Program_Mass_Air_Flow_Ph2 = random_data(10, 60, -2, 2, 1)
        elif(value_config == "toolow"):
            Fan_Program_Mass_Air_Flow_Ph2 = random_data(10, 2, -2, 2, 1)  
        Fan_Program_Mass_Air_Flow_Unit = "l/min"
        Fan_Program_Mass_Air_Flow_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Fan Program" +"\\" + "Mass_Air_Flow" + "\\" + "Mass_Air_Flow_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump( Fan_Program_Mass_Air_Flow_Ph2, fp)
            pickle.dump( Fan_Program_Mass_Air_Flow_Unit, fp)
            pickle.dump( Fan_Program_Mass_Air_Flow_Ph2_Time, fp)
         
        #################
        #Door Lock Program
        #################
        
        value_config =  config[c]["Door Lock Program"]["Pressure"]
        if(value_config == "normal"):
            Door_Lock_Program_Pressure_Ph1 = random_data(10, 1000, -2, 2, 1)
            Door_Lock_Program_Pressure_Ph2 = random_data(10, 1300, -2, 2, 1)
        elif(value_config == "toolow"):
            Door_Lock_Program_Pressure_Ph1 = random_data(10, 1000, -2, 2, 1)
            Door_Lock_Program_Pressure_Ph2 = random_data(10, 1100, -2, 2, 1)
        Door_Lock_Program_Pressure_Unit = "Pa"
        Door_Lock_Program_Pressure_Ph1_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Door_Lock_Program_Pressure_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Door Lock Program" +"\\" + "Pressure" + "\\" + "Pressure_Ph1" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Door_Lock_Program_Pressure_Ph1, fp)
            pickle.dump(Door_Lock_Program_Pressure_Unit, fp)
            pickle.dump(Door_Lock_Program_Pressure_Ph1_Time, fp)
            
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Door Lock Program" +"\\" + "Pressure" + "\\" + "Pressure_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Door_Lock_Program_Pressure_Ph2, fp)
            pickle.dump(Door_Lock_Program_Pressure_Unit, fp)
            pickle.dump(Door_Lock_Program_Pressure_Ph2_Time, fp)
            
        value_config =  config[c]["Door Lock Program"]["Lock"]
        Door_Lock_Program_Lock_Ph2 = []
        if(value_config == True):
            Door_Lock_Program_Lock_Ph2.append(1)
        elif(value_config == False):
            Door_Lock_Program_Lock_Ph2.append(0)
        Door_Lock_Program_Lock_Unit  =  "true/false"
        Door_Lock_Program_Lock_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Door Lock Program" +"\\" + "Lock" + "\\" + "Lock_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Door_Lock_Program_Lock_Ph2, fp)
            pickle.dump(Door_Lock_Program_Lock_Unit, fp)
            pickle.dump(Door_Lock_Program_Lock_Ph2_Time, fp)
            
        #################
        #Drum Motor Program
        #################
        value_config =  config[c]["Drum Motor Program"]["Loudness"]
        if(value_config == "normal"):
            Drum_Motor_Program_Loudness_Ph1 = random_data(10, 5, -2, 2, 1)
            Drum_Motor_Program_Loudness_Ph2 = random_data(10, 8, -2, 2, 1)
        elif(value_config == "toohigh"):
            Drum_Motor_Program_Loudness_Ph1 = random_data(10, 5, -2, 2, 1)
            Drum_Motor_Program_Loudness_Ph2 = random_data(10, 15, -2, 2, 1)
        Drum_Motor_Program_Loudness_Unit =  "dB"
        Drum_Motor_Program_Loudness_Ph1_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Drum_Motor_Program_Loudness_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Drum Motor Program" +"\\" + "Loudness" + "\\" + "Loudness_Ph1" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Drum_Motor_Program_Loudness_Ph1, fp)
            pickle.dump(Drum_Motor_Program_Loudness_Unit, fp)
            pickle.dump(Drum_Motor_Program_Loudness_Ph1_Time, fp)
            
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Drum Motor Program" +"\\" + "Loudness" + "\\" + "Loudness_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Drum_Motor_Program_Loudness_Ph2, fp)
            pickle.dump(Drum_Motor_Program_Loudness_Unit, fp)
            pickle.dump(Drum_Motor_Program_Loudness_Ph2_Time, fp)
        
        value_config =  config[c]["Drum Motor Program"]["Vibration"]
        if(value_config == "normal"):
            Drum_Motor_Program_Vibration_Ph2 = random_data(10, 10, -2, 2, 1)
        elif(value_config == "toohigh"):
            Drum_Motor_Program_Vibration_Ph2 = random_data(10, 50, -2, 2, 1)
        Drum_Motor_Program_Vibration_Unit  = "%"
        Drum_Motor_Program_Vibration_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Drum Motor Program" +"\\" + "Vibration" + "\\" + "Vibration_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Drum_Motor_Program_Vibration_Ph2, fp)
            pickle.dump(Drum_Motor_Program_Vibration_Unit, fp)
            pickle.dump(Drum_Motor_Program_Vibration_Ph2_Time, fp)
        
        value_config =  config[c]["Drum Motor Program"]["Rotation_Speed"]
        if(value_config == "normal"):
            Drum_Motor_Program_Rotation_Speed_Ph2 = random_data(10, 55, -2, 2, 1)
        elif(value_config == "toohigh"):
            Drum_Motor_Program_Rotation_Speed_Ph2 = random_data(10, 100, -2, 2, 1)
        elif(value_config == "toolow"):
            Drum_Motor_Program_Rotation_Speed_Ph2 = random_data(10, 10, -2, 2, 1)
        Drum_Motor_Program_Rotation_Speed_Unit  =  "rpm"
        Drum_Motor_Program_Rotation_Speed_Ph2_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Drum Motor Program" +"\\" + "Rotation_Speed" + "\\" + "Rotation_Speed_Ph2" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Drum_Motor_Program_Rotation_Speed_Ph2, fp)
            pickle.dump(Drum_Motor_Program_Rotation_Speed_Unit, fp)
            pickle.dump(Drum_Motor_Program_Rotation_Speed_Ph2_Time, fp)
            
        #################
        #Water Inlet Program
        #################
        
        value_config =  config[c]["Water Inlet Program"]["Water_Level"]
        if(value_config == "normal"):
            Water_Inlet_Program_Water_Level_Ph1 = random_data(10, 2, -2, 2, 1)
            Water_Inlet_Program_Water_Level_Ph3 = random_data(10, 30, -2, 2, 1)
        elif(value_config == "toolow"):
            Water_Inlet_Program_Water_Level_Ph1 = random_data(10, 2, -2, 2, 1)
            Water_Inlet_Program_Water_Level_Ph3 = random_data(10, 10, -2, 2, 1)
        Water_Inlet_Program_Water_Level_Unit  = "%"
        Water_Inlet_Program_Water_Level_Ph1_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        Water_Inlet_Program_Water_Level_Ph3_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Water Inlet Program" +"\\" + "Water_Level" + "\\" + "Water_Level_Ph1" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Water_Inlet_Program_Water_Level_Ph1, fp)
            pickle.dump(Water_Inlet_Program_Water_Level_Unit, fp)
            pickle.dump(Water_Inlet_Program_Water_Level_Ph1_Time, fp)
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Water Inlet Program" +"\\" + "Water_Level" + "\\" + "Water_Level_Ph3" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Water_Inlet_Program_Water_Level_Ph3, fp)
            pickle.dump(Water_Inlet_Program_Water_Level_Unit, fp)
            pickle.dump(Water_Inlet_Program_Water_Level_Ph3_Time, fp)
        
        value_config =  config[c]["Water Inlet Program"]["Entrance_Water_Flow"]
        Water_Inlet_Program_Entrance_Water_Flow_Ph3 = []
        if(value_config == True):
            Water_Inlet_Program_Entrance_Water_Flow_Ph3.append(1)
        elif(value_config == False):
            Water_Inlet_Program_Entrance_Water_Flow_Ph3.append(0)
        Water_Inlet_Program_Entrance_Water_Flow_Unit  = "true/false"
        Water_Inlet_Program_Entrance_Water_Flow_Ph3_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Water Inlet Program" +"\\" + "Entrance_Water_Flow" + "\\" + "Entrance_Water_Flow_Ph3" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Water_Inlet_Program_Entrance_Water_Flow_Ph3, fp)
            pickle.dump(Water_Inlet_Program_Entrance_Water_Flow_Unit, fp)
            pickle.dump(Water_Inlet_Program_Entrance_Water_Flow_Ph3_Time, fp)
            
        value_config =  config[c]["Water Inlet Program"]["Water_Hardness"]
        if(value_config == "normal"):
            Water_Inlet_Program_Water_Hardness_Ph3 = random_data(10, 6, -0.5, 0.5, 1)
        elif(value_config == "toohigh"):
            Water_Inlet_Program_Water_Hardness_Ph3 = random_data(10, 19, -0.5, 0.5, 1)
        Water_Inlet_Program_Water_Hardness_Unit  = u"\N{DEGREE SIGN}"  + "dH"
        Water_Inlet_Program_Water_Hardness_Ph3_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Water Inlet Program" +"\\" + "Water_Hardness" + "\\" + "Water_Hardness_Ph3" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Water_Inlet_Program_Water_Hardness_Ph3, fp)
            pickle.dump(Water_Inlet_Program_Water_Hardness_Unit, fp)
            pickle.dump(Water_Inlet_Program_Water_Hardness_Ph3_Time, fp)
         
        #################
        #Long Time Check
        #################
        
        value_config =  config[c]["Long Time Check"]["Laundry_Fill_Level"]
        if(value_config == "normal"):
            Long_Time_Check_Laundry_Fill_Level = random_data(10, 50, -2, 2, 1)
        elif(value_config == "toohigh"):
            Long_Time_Check_Laundry_Fill_Level = random_data(10, 90, -2, 2, 1)
        elif(value_config == "toolow"):
            Long_Time_Check_Laundry_Fill_Level = random_data(10, 25, -2, 2, 1)
        Long_Time_Check_Laundry_Fill_Level_Unit  = "%"
        Long_Time_Check_Laundry_Fill_Level_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Laundry_Fill_Level" + "\\" + "Laundry_Fill_Level" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Laundry_Fill_Level, fp)
            pickle.dump(Long_Time_Check_Laundry_Fill_Level_Unit, fp)
            pickle.dump(Long_Time_Check_Laundry_Fill_Level_Time, fp)            
        
        
        value_config =  config[c]["Long Time Check"]["Laundry_Weight"]
        if(value_config == "normal"):
            Long_Time_Check_Laundry_Weight = random_data(10, 5, -2, 2, 1)
        elif(value_config == "toohigh"):
            Long_Time_Check_Laundry_Weight = random_data(10, 20, -2, 2, 1)
        Long_Time_Check_Laundry_Weight_Unit  = "kg"
        Long_Time_Check_Laundry_Weight_Time = now.strftime("%m/%d/%Y, %H:%M:%S") 
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Laundry_Weight" + "\\" + "Laundry_Weight" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Laundry_Weight, fp)
            pickle.dump(Long_Time_Check_Laundry_Weight_Unit, fp)
            pickle.dump(Long_Time_Check_Laundry_Weight_Time, fp)  
        
        value_config =  config[c]["Long Time Check"]["Washing_Powder_Fill_Level"]
        if(value_config == "normal"):
            Long_Time_Check_Washing_Powder_Fill_Level = random_data(10, 50, -2, 2, 1)
        if(value_config == "low"):
            Long_Time_Check_Washing_Powder_Fill_Level = random_data(10, 20, -2, 2, 1)
        if(value_config == "high"):
            Long_Time_Check_Washing_Powder_Fill_Level = random_data(10, 80, -2, 2, 1)
        Long_Time_Check_Washing_Powder_Fill_Level_Unit  = "%"
        Long_Time_Check_Washing_Powder_Fill_Level_Time = now.strftime("%m/%d/%Y, %H:%M:%S")  
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Washing_Powder_Fill_Level" + "\\" + "Washing_Powder_Fill_Level" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Washing_Powder_Fill_Level, fp)
            pickle.dump(Long_Time_Check_Washing_Powder_Fill_Level_Unit, fp)
            pickle.dump(Long_Time_Check_Washing_Powder_Fill_Level_Time, fp)  
                
        value_config =  config[c]["Long Time Check"]["Water_Hardness"]
        if(value_config == "normal"):
            Long_Time_Check_Water_Hardness = random_data(10, 6, -0.5, 0.5, 1)
        if(value_config == "soft"):
            Long_Time_Check_Water_Hardness = random_data(10, 10, -0.5, 0.5, 1)            
        if(value_config == "hard"):
            Long_Time_Check_Water_Hardness = random_data(10, 19, -0.5, 0.5, 1)
        Long_Time_Check_Water_Hardness_Unit  = u"\N{DEGREE SIGN}"  + "dH"
        Long_Time_Check_Water_Hardness_Time = now.strftime("%m/%d/%Y, %H:%M:%S")   
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Water_Hardness" + "\\" + "Water_Hardness" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Water_Hardness, fp)
            pickle.dump(Long_Time_Check_Water_Hardness_Unit, fp)
            pickle.dump(Long_Time_Check_Water_Hardness_Time, fp)  
                        
        value_config =  config[c]["Long Time Check"]["Temperature"]
        if(value_config == "normal"):
            Long_Time_Check_Temperature = random_data(10, 50, -2, 2, 1)
        if(value_config == "high"):
            Long_Time_Check_Temperature = random_data(10, 70, -2, 2, 1)
        if(value_config == "low"):
            Long_Time_Check_Temperature = random_data(10, 20, -2, 2, 1)
        Long_Time_Check_Temperature_Unit  = u"\N{DEGREE SIGN}"
        Long_Time_Check_Temperature_Time = now.strftime("%m/%d/%Y, %H:%M:%S")   
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Temperature" + "\\" + "Temperature" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Temperature, fp)
            pickle.dump(Long_Time_Check_Temperature_Unit, fp)
            pickle.dump(Long_Time_Check_Temperature_Time, fp)  
                
        value_config =  config[c]["Long Time Check"]["Usage_Frequency"]
        if(value_config == "normal"):
            Long_Time_Check_Usage_Frequency = random_data(7, 1, 0, 0, 1)
        if(value_config == "toohigh"):
            Long_Time_Check_Usage_Frequency = random_data(12, 1, 0, 0, 1)
        if(value_config == "toolow"):
            Long_Time_Check_Usage_Frequency = random_data(2, 1, 0, 0, 1)
        Long_Time_Check_Usage_Frequency_Unit  = "Washing Dryer Used"
        Long_Time_Check_Usage_Frequency_Time = now.strftime("%m/%d/%Y, %H:%M:%S")  
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Usage_Frequency" + "\\" + "Usage_Frequency" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Usage_Frequency, fp)
            pickle.dump(Long_Time_Check_Usage_Frequency_Unit, fp)
            pickle.dump(Long_Time_Check_Usage_Frequency_Time, fp)  
        
        value_config =  config[c]["Long Time Check"]["Used_Modes"]
        Long_Time_Check_Used_Modes = []
        if(value_config == "normal"):
            Long_Time_Check_Used_Modes.append(1)
        if(value_config == "hightemperature"):
            Long_Time_Check_Used_Modes.append(2)
        if(value_config == "lowtemperature"):
            Long_Time_Check_Used_Modes.append(0)
        Long_Time_Check_Used_Modes_Unit  = "lowtemp/normal/hightemp"
        Long_Time_Check_Used_Modes_Time = now.strftime("%m/%d/%Y, %H:%M:%S") 
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Used_Modes" + "\\" + "Used_Modes" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Used_Modes, fp)
            pickle.dump(Long_Time_Check_Used_Modes_Unit, fp)
            pickle.dump(Long_Time_Check_Used_Modes_Time, fp)   
         
        value_config =  config[c]["Long Time Check"]["Washing_Powder"]
        Long_Time_Check_Washing_Powder = []
        if(value_config == "normal"):
            Long_Time_Check_Washing_Powder.append(1)
        if(value_config == "strong"):
            Long_Time_Check_Washing_Powder.append(2)
        if(value_config == "weak"):
            Long_Time_Check_Washing_Powder.append(0)
        Long_Time_Check_Washing_Powder_Unit  = "weak/normal/strong"
        Long_Time_Check_Washing_Powder_Time = now.strftime("%m/%d/%Y, %H:%M:%S")
        filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + "Long Time Check" +"\\" + "Washing_Powder" + "\\" + "Washing_Powder" + ".txt"
        with open(filename, "wb") as fp:   #Pickling
            pickle.dump(Long_Time_Check_Washing_Powder, fp)
            pickle.dump(Long_Time_Check_Washing_Powder_Unit, fp)
            pickle.dump(Long_Time_Check_Washing_Powder_Time, fp)        
           
    except:
        print("Generating failed, check config")