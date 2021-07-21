import pickle
import os
from cmath import phase
from generatedata import generate_all_data

class contextmodel():

    def __init__(self, app, db, reqJson):
        self.app = app
        self.db = db
        self.reqJson = reqJson
        self.create()
        self.runContextDiagnosis()
        self.deinitialize()
        
    def create(self):
        self.diagnosisMode = self.uploadContextDatatoServer()
        self.context = self.chooseContext()
        generate_all_data()
        self.uploadSimulatedContext()
        self.fetchContextfromServer()
        
    def runContextDiagnosis(self):
        result = self.calculateResult()
        return result
    
    def deinitialize(self):
        self.setValidfalse()
        
	#chooses the context, based on the Diagnosis Mode chosen
    def chooseContext(self):
        #switch case hard coded
        if(self.diagnosisMode == "Pump Out Program"):
            context = ["Water_Level","Exit_Water_Flow","Liquid"]
        elif(self.diagnosisMode == "Complete Short Program"):
            context = [""]
        elif(self.diagnosisMode == "Fan Program"):
            context = ["Loudness", "Vibration", "Mass_Air_Flow"]
        elif(self.diagnosisMode == "Drum Motor Program"):
            context = ["Loudness", "Vibration", "Rotation_Speed"]
        elif(self.diagnosisMode == "Door Lock Program"):
            context = ["Pressure", "Lock"]    
        elif(self.diagnosisMode == "Water Inlet Program"):
            context = ["Water_Level", "Entrance_Water_Flow", "Liquid", "Water_Hardness"]
        elif(self.diagnosisMode == "Long Time Check"):  
            context = ["Laundry_Fill_Level", "Laundry_Weight", "Washing_Powder_Fill_Level", "Water_Hardness", "Temperature", "Usage_Frequency", "Used_Modes", "Washing_Powder"]
        else:
            context = [""]
        return context
    
    #returns the result
    def returnResult(self):
        return self.result
    
	#uploades the internal Sensor Data to MySQL contextdata Table
    def uploadContextDatatoServer(self):
        valid = "1"
        diagnosisMode = self.reqJson['nameValuePairs']['diagnosisMode']
        phase = self.reqJson['nameValuePairs']['phase']
        sensor = self.reqJson['nameValuePairs']['sensor']
        observedValue = self.reqJson['nameValuePairs']['observedValue']
        time = self.reqJson['nameValuePairs']['time']
        unit = self.reqJson['nameValuePairs']['unit']
        range_data = len(phase)
        print ('Request json string is: {}'.format(self.reqJson))
        session = self.db.session()
        if(diagnosisMode != "Long Time Check"):
            for item in range(range_data):
    
                session.execute("INSERT INTO contextdata (valid, diagnosisMode, phase, datasource, observed_value, time, unit) VALUES (%s,%s,%s,%s,%s,%s,%s)" ,
                           (valid, diagnosisMode, phase[item], sensor[item], observedValue[item], time[item], unit[item]))
                session.commit()
            session.close()
        return diagnosisMode
    
	#function if programer wants to handle diagnosismode by ID not name
    def chosenDiagnosisMode(self, diagnosisID):
        if(diagnosisID == "12"):
            diagnosisMode = "Door Lock Program"
            phaserange = 3
        elif(diagnosisID == "13"):
            diagnosisMode = "Fan Program"
            phaserange = 3
        elif(diagnosisID == "14"):
            diagnosisMode = "Water Inlet Program"
            phaserange = 3
        elif(diagnosisID == "16"):
            diagnosisMode = "Complete Short Program"
            phaserange = 6
        elif(diagnosisID == "18"):
            diagnosisMode = "Pump Out Program"
            phaserange = 3
        elif(diagnosisID == "19"):
            diagnosisMode = "Drum Motor Program"
            phaserange = 3
        else:
            diagnosisMode = ""
            phaserange = 0
        self.phaserange = phaserange
        return diagnosisMode
            
        
    #fetches every Context Data needed for calculating result, only uses new data
    def fetchContextfromServer(self):
        context = self.context
        session = self.db.session()
        sensordata = []
        for item in context:
            session.execute("SELECT * FROM contextmodeldata.contextdata WHERE valid = \"1\" AND datasource = %(context)s", {'context' : item} )
            sensordata.append(session.fetchall())
        self.sensordata = sensordata
        print(sensordata)
        
	#marks the data as old
    def setValidfalse(self):
        session = self.db.session()
        session.execute("UPDATE contextdata SET valid = '0'")
        session.commit()
        session.close()
        
	#uploades the simulated Context Data to MySQL contextdata Table
    def uploadSimulatedContext(self):
            valid = 1
            session = self.db.session()
            for index,item in enumerate(self.context):
                for phase in range(1, 6):
                    filename = ""
                    try:
                        if(self.diagnosisMode != "Long Time Check"): filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + self.diagnosisMode +"\\" + self.context[index] + "\\" + self.context[index] + "_Ph" + str(phase) + ".txt"
                        elif(self.diagnosisMode == "Long Time Check" and phase == 1): filename = os.path.dirname(__file__) + "\\contextdata" + "\\" + self.diagnosisMode +"\\" + self.context[index] + "\\" + self.context[index] + ".txt"
                        
                        with open(filename, "rb") as fp:
                            valuelist = pickle.load(fp)
                            unit = pickle.load(fp)
                            timelist = pickle.load(fp)
                        for i,value in enumerate(valuelist):
                            session.execute("INSERT INTO contextdata (valid, diagnosisMode, phase, datasource, observed_value, time, unit) VALUES (%s,%s,%s,%s,%s,%s,%s)" , (str(valid), self.diagnosisMode, str(phase), self.context[index], str(value), str(timelist), unit))
                            session.commit()
                    except Exception:
                        pass
            session.close()

	#decision tree and creation of the result, split into result, subresult and if the result has passed
    def calculateResult(self):
        result = []
        subresult = []
        resultpass = []
        
        #Pump Out Program

		#splits the data fetched from the MySQL table into single phases and lists
        if(self.diagnosisMode == "Pump Out Program"):
            Water_Level = self.sensordata[self.context.index("Water_Level")]
            Water_Level_Ph1 = []
            Water_Level_Ph3 = []
            for value in Water_Level:
                if value[2] == 1:
                    Water_Level_Ph1.append(value[4])
                elif value[2] == 3:
                    Water_Level_Ph3.append(value[4])
            Exit_Water_Flow = self.sensordata[self.context.index("Exit_Water_Flow")]
            Exit_Water_Flow_Ph2 = []
            for value in Exit_Water_Flow:
                if value[2] == 1:
                    Exit_Water_Flow_Ph2.append(value)

		#creates the staments used in the decision tree, is handled a bit different for the other Diagnosis Modes
            Statement_Water_Level_toohigh  =  (self.av(Water_Level_Ph1) - self.av(Water_Level_Ph3)) <= 30
            Statement_no_water_flow  =  Exit_Water_Flow_Ph2 == 0
            
		#creates the result based on the values
            partialresult = []
            if(Statement_Water_Level_toohigh):
                partialresult.append("Wasserpegel ist noch zu hoch")
                if(Statement_no_water_flow):
                    partialresult.append( "Kein Wasserdurchfluss am Abfluss gemessen" )
                    result.append( "Kein Wasserdurchfluss am Abfluss gemessen")
                    resultpass.append("false")
                else:
                    partialresult.append("Wasserdurchfluss wurde gemessen")
                    result.append( "Wasserdurchflusssensor oder Wasserpegelmesser defekt, prüfen und austauschen")
                    resultpass.append("false")
            else:
                partialresult.append("Wasserabnahme wurde erkannt")
                if(Statement_no_water_flow):
                    partialresult.append( "Kein Wasserdurchfluss am Abfluss gemessen")
                    result.append( "Wasserdurchflusssensor oder Wasserpegelmesser defekt, prüfen und austauschen")
                    resultpass.append("false")
                else:
                    partialresult.append("Wasserdurchfluss wurde gemessen")
                    result.append( "Abpumpen erfolgreich, keine Verstopfung erkannt" )
                    resultpass.append("true")
            subresult.append(partialresult)
            
        #Complete Short Program
		#recursive creation of contextmodel with the other porgrams
        elif(self.diagnosisMode == "Complete Short Program"):
            programlist = ["Pump Out Program", "Fan Program", "Drum Motor Program", "Door Lock Program", "Water Inlet Program"]
            for program in programlist:
                reqJson = {'nameValuePairs': {'mode': 'true', 'diagnosisMode': program, 'phase': [], 'sensor': [], 'desiredValueType': [], 'desiredValue': [], 'observedValue': [], 'time': [], 'unit': []}}
                c =  contextmodel(self.app, self.db, reqJson)
                recursiveresult = c.getresult()
                recursivesubresult = c.getsubresult()
                recursiveresultpass = c.getresultpass()
                result = result + recursiveresult
                subresult = subresult + recursivesubresult
                resultpass = resultpass + recursiveresultpass    
                    
        #Fan Program
        elif(self.diagnosisMode == "Fan Program"):
            Loudness = self.sensordata[self.context.index("Loudness")]
            Loudness_Ph1 = []
            Loudness_Ph2 = []
            for value in Loudness:
                if value[2] == 1:
                    Loudness_Ph1.append(value[4])
                elif value[2] == 2:
                    Loudness_Ph2.append(value[4])
            Vibration = self.sensordata[self.context.index("Vibration")]
            Vibration_Ph2 = []
            for value in Vibration:
                if value[2] == 2:
                    Vibration_Ph2.append(value[4])
            Mass_Air_Flow = self.sensordata[self.context.index("Mass_Air_Flow")]
            Mass_Air_Flow_Ph2 = []
            for value in Mass_Air_Flow:
                if value[2] == 2:
                    Mass_Air_Flow_Ph2.append(value[4])
                
            
            if((self.av(Loudness_Ph2) - self.av(Loudness_Ph1))/self.av(Loudness_Ph1) <= 0.75):
                Statement_Loudness  = "normal"
            else:
                Statement_Loudness  = "toohigh"
                
            if(self.av(Vibration_Ph2) <= 25):
                Statement_Vibration =  "normal"
            else:
                Statement_Vibration = "toohigh"
                
            if(self.av(Mass_Air_Flow_Ph2) >= 50):
                Statement_Mass_Air_Flow = "normal"
            else:
                Statement_Mass_Air_Flow = "toolow"
            
            
            partialresult = []
            if(Statement_Loudness ==  "normal"):
                partialresult.append("Kein starker Lautstärkeunterschied registriert")
                if(Statement_Vibration == "normal"):
                    partialresult.append( "Kein Vibrieren des Waschtrockners festgestellt" )
                    if(Statement_Mass_Air_Flow == "normal"):
                        partialresult.append( "Luftstrom ist im normalen Bereich, Leistung des Lüfters ausreichend" )
                        result.append( "Lüfter funktioniert einwandfrei, es konnten keine Fehler festgestellt werden")
                        resultpass.append("true")
                    else:
                        partialresult.append( "Luftstrom ist zu niedrig, Leistung des Lüfters reicht nicht aus")
                        result.append( "Lüfter prüfen und auswechseln")
                        resultpass.append("false")
                else:
                    partialresult.append( "Vibrieren des Waschtrockners festgestellt" )
                    if(Statement_Mass_Air_Flow == "normal"):
                        partialresult.append( "Luftstrom ist im normalen Bereich, Leistung des Lüfters ausreichend" )
                        result.append( "Waschtrockner vibriert, überprüfe Aufstellwinkel")
                        resultpass.append("false")
                    else:
                        partialresult.append( "Luftstrom ist zu niedrig, Leistung des Lüfters reicht nicht aus")
                        result.append( "Lüfter scheint defekt zu sein, unbedingt austauschen, um weitere Schäden am Gerät zu vermeiden")
                        resultpass.append("false")
            else:
                partialresult.append("Starker Lautstärkeunterschied registriert")
                if(Statement_Vibration == "normal"):
                    partialresult.append( "Kein Vibrieren des Waschtrockners festgestellt" )
                    if(Statement_Mass_Air_Flow == "normal"):
                        partialresult.append( "Luftstrom ist im normalen Bereich, Leistung des Lüfters ausreichend" )
                        result.append( "Lüfter viel zu laut, prüfen lassen, möglicherweise braucht er eine Wartung")
                        resultpass.append("false")
                    else:
                        partialresult.append( "Luftstrom ist zu niedrig, Leistung des Lüfters reicht nicht aus")
                        result.append( "Lüfter defekt, austauschen um nötige Leistung ernut zu erbringen")
                        resultpass.append("false")
                else:
                    partialresult.append( "Vibrieren des Waschtrockners festgestellt" )
                    if(Statement_Mass_Air_Flow == "normal"):
                        partialresult.append( "Luftstrom ist im normalen Bereich, Leistung des Lüfters ausreichend" )
                        result.append( "Möglicherweise Kleinteile im Lüfter, überprüfen, um Schäden am Lüfter zu vermeiden")
                        resultpass.append("false")
                    else:
                        partialresult.append( "Luftstrom ist zu niedrig, Leistung des Lüfters reicht nicht aus")
                        result.append( "Lüfter muss unbedingt ausgetauscht werden")
                        resultpass.append("false")
            subresult.append(partialresult)
                    
                    
        #Drum Motor Program
        elif(self.diagnosisMode == "Drum Motor Program"):
            Loudness = self.sensordata[self.context.index("Loudness")]
            Loudness_Ph1 = []
            Loudness_Ph2 = []
            for value in Loudness:
                if value[2] == 1:
                    Loudness_Ph1.append(value[4])
                elif value[2] == 2:
                    Loudness_Ph2.append(value[4])
            Vibration = self.sensordata[self.context.index("Vibration")]
            Vibration_Ph2 = []
            for value in Vibration:
                if value[2] == 2:
                    Vibration_Ph2.append(value[4])
            Rotation_Speed = self.sensordata[self.context.index("Rotation_Speed")]
            Rotation_Speed_Ph2 = []
            for value in Rotation_Speed:
                if value[2] == 2:
                    Rotation_Speed_Ph2.append(value[4])
        
                    
            if((self.av(Loudness_Ph2) - self.av(Loudness_Ph1))/self.av(Loudness_Ph1) <= 0.75):
                Statement_Loudness  = "normal"
            else:
                Statement_Loudness  = "toohigh"
                
            if(self.av(Vibration_Ph2) <= 25):
                Statement_Vibration =  "normal"
            else:
                Statement_Vibration = "toohigh"
                
            if(self.av(Rotation_Speed_Ph2) >= 50 and self.av(Rotation_Speed_Ph2) <= 60):
                Statement_Rotation_Speed = "normal"
            elif(self.av(Rotation_Speed_Ph2) < 50):
                Statement_Rotation_Speed = "toolow"
            else:
                Statement_Rotation_Speed = "toohigh"
            
            partialresult = []
            if(Statement_Loudness ==  "normal"):
                partialresult.append("Kein besonders starker Lautstärkeunterschied festgestellt")
                if(Statement_Vibration == "normal"):
                    partialresult.append("keine Vibration festgestellt")
                    if(Statement_Rotation_Speed == "normal"):
                        partialresult.append("Trommelmotor hat die richtige Geschwindigkeit erreicht")
                        result.append( "Trommelmotor intakt, keine Fehler konnten festgestellt werden")
                        resultpass.append("true")
                    elif(Statement_Rotation_Speed == 'toolow'):
                        partialresult.append("Trommelmotor ist zu langsam und erreicht die benötigte Geschwindigkeit nicht")
                        result.append( "Trommelmotorleistung ist zu niedrig, Reperatur wird empfohlen")
                        resultpass.append("false")
                    else:
                        partialresult.append("Trommelmotor ist viel zu schnell, er hat die Grenzgeschwindigkeit überschritten")
                        result.append( "Trommelmotorleistung zu hoch, Reperatur wird empfohlen")
                        resultpass.append("false")
                else:
                    partialresult.append("Waschtrockner vibriert")
                    if(Statement_Rotation_Speed == "normal"):
                        partialresult.append("Trommelmotor hat die richtige Geschwindigkeit erreicht")
                        result.append( "Aufstellwinkel des Waschtrockners prüfen, möglicherweise schief")
                        resultpass.append("false")
                    elif(Statement_Rotation_Speed == 'toolow'):
                        partialresult.append("Trommelmotor ist zu langsam und erreicht die benötigte Geschwindigkeit nicht")
                        result.append( "Aufstellwinkel des Waschtrockners prüfen, möglicherweise wird dadurch Geschwindigkeit beeinträchtigt")
                        resultpass.append("false")
                    else:
                        partialresult.append("Trommelmotor ist viel zu schnell, er hat die Grenzgeschwindigkeit überschritten")
                        result.append( "Trommelmotorleistung zu hoch, Reperatur wird empfohlen, um Schäden zu vermeiden")
                        resultpass.append("false")
            else:
                partialresult.append("Starker Lautstärkeunterschied festgestellt")
                if(Statement_Vibration == "normal"):
                    partialresult.append("keine Vibration festgestellt")
                    if(Statement_Rotation_Speed == "normal"):
                        partialresult.append("Trommelmotor hat die richtige Geschwindigkeit erreicht")
                        result.append( "Andere Diagnoseprogramme durchführen, um Lautstärkequelle zu finden")
                        resultpass.append("false")
                    elif(Statement_Rotation_Speed == 'toolow'):
                        partialresult.append("Trommelmotor ist zu langsam und erreicht die benötigte Geschwindigkeit nicht")
                        result.append( "Trommelmotor prüfen lassen und Lautstärkequelle festmachen")
                        resultpass.append("false")
                    else:
                        partialresult.append("Trommelmotor ist viel zu schnell, er hat die Grenzgeschwindigkeit überschritten")
                        result.append( "Lautstärkequelle kommt höchstwarscheinlich von der Überfunktion des Motors")
                        resultpass.append("false")
                else:
                    partialresult.append("Waschtrockner vibriert")
                    if(Statement_Rotation_Speed == "normal"):
                        partialresult.append("Trommelmotor hat die richtige Geschwindigkeit erreicht")
                        result.append( "Motor auf Kleinteile überprüfen")
                        resultpass.append("false")
                    elif(Statement_Rotation_Speed == 'toolow'):
                        partialresult.append("Trommelmotor ist zu langsam und erreicht die benötigte Geschwindigkeit nicht")
                        result.append( "Motor auf Kleinteile überprüfen, da diese die Geschwindigkeit beeinträchtigen können")
                        resultpass.append("false")
                    else:
                        partialresult.append("Trommelmotor ist viel zu schnell, er hat die Grenzgeschwindigkeit überschritten")
                        result.append( "Trommelmotorüberfunktion, Stromzufuhr überprüfen")
                        resultpass.append("false")
            subresult.append(partialresult)
        
                    
                    
        #Door Lock Program
        elif(self.diagnosisMode == "Door Lock Program"):
            Pressure = self.sensordata[self.context.index("Pressure")]
            Pressure_Ph1 = []
            Pressure_Ph2 = []
            for value in Pressure:
                if value[2] == 1:
                    Pressure_Ph1.append(value[4])
                elif value[2] == 2:
                    Pressure_Ph2.append(value[4])
            Lock = self.sensordata[self.context.index("Lock")]
            Lock_Ph2 = []
            for value in Lock:
                if value[2] == 2:
                    Lock_Ph2.append(value[4])
        
            if((self.av(Pressure_Ph2) - self.av(Pressure_Ph1))/self.av(Pressure_Ph1) >= 0.2):
                Statement_Pressure  = "normal"
            else:
                Statement_Pressure  = "toolow"
                    
            if(self.av(Lock_Ph2) == 1):
                Statement_Lock  = True
            else:
                Statement_Lock  = False
            
            partialresult = []
            if(Statement_Pressure == "normal"):
                partialresult.append("Druckunterschied konnte festgestellt werden und ist im gewuenschten Bereich")
                if(Statement_Lock):
                    partialresult.append("Verschluss wurde gemessen")
                    result.append( "Keine Fehler gefunden, Schloss funktioniert einwandfrei")
                    resultpass.append("true")
                else:
                    partialresult.append("Kein Verschluss wurde festgestellt" )
                    result.append( "Einer der Sensoren ist defekt, falls ein Klicken beim Start der Diagnose gehoert wurde ist  moeglicherweise der Verschlusssensor defekt")
                    resultpass.append("false")
            else:
                partialresult.append( "Druckunterschied konnte nicht festgestellt werden oder ist zu niedrig" )
                if(Statement_Lock):
                    partialresult.append( "Verschluss wurde gemessen" )
                    result.append( "Einer der Sensoren ist defekt, falls ein Klicken beim Start der Diagnose gehoert wurde ist  moeglicherweise der Drucksensor defekt")
                    resultpass.append("false")
                else:
                    partialresult.append( "Kein Verschluss wurde festgestellt" )
                    result.append( "Schloss defekt, Techniker anrufen und austauschen lassen" )
                    resultpass.append("false")
            subresult.append(partialresult)
            
                    
        #Water Inlet Program
        elif(self.diagnosisMode == "Water Inlet Program"):
            Water_Level = self.sensordata[self.context.index("Water_Level")]
            Water_Level_Ph1 = []
            Water_Level_Ph3 = []
            for value in Water_Level:
                if value[2] == 1:
                    Water_Level_Ph1.append(value[4])
                elif value[2] == 3:
                    Water_Level_Ph3.append(value[4])
            Entrance_Water_Flow = self.sensordata[self.context.index("Entrance_Water_Flow")]
            Entrance_Water_Flow_Ph3 = []
            for value in Entrance_Water_Flow:
                if value[2] == 3:
                    Entrance_Water_Flow_Ph3.append(value[4])
            Water_Hardness = self.sensordata[self.context.index("Water_Hardness")]
            Water_Hardness_Ph3 = []
            for value in Water_Hardness:
                if value[2] == 3:
                    Water_Hardness_Ph3.append(value[4])
                    
        
            if((self.av(Water_Level_Ph3) - self.av(Water_Level_Ph1)) >= 20):
                Statement_Water_Level  = "normal"
            else:
                Statement_Water_Level  = "toolow"
                
            if(self.av(Entrance_Water_Flow_Ph3) == 1):
                Statement_Entrance_Water_Flow  = True
            else:
                Statement_Entrance_Water_Flow  = False
                
            if(self.av(Water_Hardness_Ph3) <= 14):
                Statement_Water_Hardness = "normal"
            else:
                Statement_Water_Hardness = "toohigh"

            partialresult = []
            if(Statement_Water_Level ==  "normal"):
                partialresult.append("Gewünschte Wasserzufuhr erreicht")
                if(Statement_Water_Hardness == "normal"):
                    partialresult.append("Wasserhärtegrad in Ordnung")
                    if(Statement_Entrance_Water_Flow):
                        partialresult.append("Eingangsdurchfluss erkannt")
                        result.append( "Keine Fehler bei der Wasserzufuhr erkannt")
                        resultpass.append("true")
                    else:
                        partialresult.append("Kein Eingangsdurchfluss erkannt")
                        result.append( "Eingangsdurchflusssensor oder Wasserpegelmesser defekt")
                        resultpass.append("false")
                else:
                    partialresult.append("Wasserhärtegrad sehr hoch")
                    if(Statement_Entrance_Water_Flow):
                        partialresult.append("Eingangsdurchfluss erkannt")
                        result.append( "Keine Fehler bei der Wasserzufuhr erkannt, jedoch wird aufgrund des hohen Wassergrades empfohlen, öfter eine Diagnose durchzuführen")
                        resultpass.append("true")
                    else:
                        partialresult.append("Kein Eingangsdurchfluss erkannt")
                        result.append( "Eingangsdurchflusssensor oder Wasserpegelmesser defekt, öftere Diagnose aufgrund des hohen Wasserhärtegrades empfohlen")
                        resultpass.append("false")
            else:
                partialresult.append("Gewünschte Wasserzufuhr konnte nicht erreicht werden")
                if(Statement_Water_Hardness == "normal"):
                    partialresult.append("Wasserhärtegrad in Ordnung")
                    if(Statement_Entrance_Water_Flow):
                        partialresult.append("Eingangsdurchfluss erkannt")
                        result.append( "Eingangsdurchflusssensor oder Wasserpegelmesser defekt")
                        resultpass.append("true")
                    else:
                        partialresult.append("Kein Eingangsdurchfluss erkannt")
                        result.append( "Wassereingangsventil verstopft, überprüfen und lockern")
                        resultpass.append("false")
                else:
                    partialresult.append("Wasserhärtegrad sehr hoch")
                    if(Statement_Entrance_Water_Flow):
                        partialresult.append("Eingangsdurchfluss erkannt")
                        result.append( "Eingangsdurchflusssensor oder Wasserpegelmesser defekt, öftere Diagnose aufgrund des hohen Wasserhärtegrades empfohlen")
                        resultpass.append("false")
                    else:
                        partialresult.append("Kein Eingangsdurchfluss erkannt")
                        partialresult.append( "Fall2" )
                        result.append( "Wassereingangsventil verstopft, überprüfen und lockern, öftere Diagnose aufgrund des hohen Wasserhärtegrades empfohlen")
                        resultpass.append("false")
            subresult.append(partialresult)
        #Long Time Check


        elif(self.diagnosisMode == "Long Time Check"):  
            Laundry_Fill_Level = []
            Laundry_Weight = []
            Washing_Powder_Fill_Level = []
            Water_Hardness = []
            Temperature = []
            Usage_Frequency = []
            Used_Modes = []
            Washing_Powder = []
            
            for value in self.sensordata[self.context.index("Laundry_Fill_Level")]:
                Laundry_Fill_Level.append(value[4])
            for value in self.sensordata[self.context.index("Laundry_Weight")]:
                Laundry_Weight.append(value[4])
            for value in self.sensordata[self.context.index("Washing_Powder_Fill_Level")]:
                Washing_Powder_Fill_Level.append(value[4])
            for value in self.sensordata[self.context.index("Water_Hardness")]:
                Water_Hardness.append(value[4])                                
            for value in self.sensordata[self.context.index("Temperature")]:
                Temperature.append(value[4])                                
            for value in self.sensordata[self.context.index("Usage_Frequency")]:
                Usage_Frequency.append(value[4])                                
            for value in self.sensordata[self.context.index("Used_Modes")]:
                Used_Modes.append(value[4])                                
            for value in self.sensordata[self.context.index("Washing_Powder")]:
                Washing_Powder.append(value[4])
                
            if(self.av(Laundry_Fill_Level)>75):
                Statement_Laundry_Fill_Level  = "toohigh"
            elif(self.av(Laundry_Fill_Level)<35):
                Statement_Laundry_Fill_Level  = "toolow"
            else:
                Statement_Laundry_Fill_Level = "normal"
            
            partialresult = []
            if(Statement_Laundry_Fill_Level == "normal"):
                partialresult.append( "Der durchschnittliche Wäschefüllstand pro Waschvorgang ist optimal und sollte weiter beibehalten werden" )
                result.append( "Waschefüllstand optimal")
                resultpass.append("true")
            elif(Statement_Laundry_Fill_Level == 'toolow'):
                partialresult.append("Es wurde festgestellt, dass im Durchschnitt zu wenig Wäsche pro Waschvorgang gewaschen werden")
                partialresult.append( "Fall2" )
                result.append( "Wäschefüllstand erhöhen, für effizientere Waschvorgänge")
                resultpass.append("false")
            else:
                partialresult.append("Es wurde festgestellt, dass im Durchschnitt zu viel Wäsche pro Waschvorgang gewaschen werden")
                result.append("Wäschefüllstand reduzieren, um Waschtrockner zu schonen")
                resultpass.append("false")
            subresult.append(partialresult)
                
                
            if(self.av(Laundry_Weight) > 10):
                Statement_Laundry_Weight  = "toohigh"
            else:
                Statement_Laundry_Weight = "normal"
            
            partialresult = []
            if(Statement_Laundry_Weight == "normal"):
                partialresult.append("Wäschegewicht unter Grenzwert des Waschtrocknerladegewichts")
                result.append( "Wäschegewicht einhalten")
                resultpass.append("true")
            else:
                partialresult.append("Wäschegewicht unter Grenzwert des Waschtrocknerladegewichts")
                result.append( "Wäschegewicht unbedingt reduzieren, um Defekte von Waschtrocknerkomponenten zu vermeiden")
                resultpass.append("false")
            subresult.append(partialresult)
            
            
            if(self.av(Washing_Powder_Fill_Level)>75):
                Statement_Washing_Powder_Fill_Level  = "high"
            elif(self.av(Washing_Powder_Fill_Level)<35):
                Statement_Washing_Powder_Fill_Level  = "low"
            else:
                Statement_Washing_Powder_Fill_Level = "normal"

            if(self.av(Water_Hardness)<7.3):
                Statement_Water_Hardness  = "soft"
            elif(self.av(Water_Hardness)>14):
                Statement_Water_Hardness  = "hard"
            else:
                Statement_Water_Hardness = "normal"

            if(self.av(Washing_Powder) == 0):
                Statement_Washing_Powder  = "weak"
            elif(self.av(Washing_Powder) == 2):
                Statement_Washing_Powder  = "strong"
            else:
                Statement_Washing_Powder = "normal"    
                
                
            partialresult = []
            if(Statement_Washing_Powder_Fill_Level == "normal"):
                    partialresult.append("Waschpulverfüllhoehe ist im mittleren Bereich")
                    if(Statement_Water_Hardness == "normal"):
                            partialresult.append("Wasserhärtegrad im normalen Bereich")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                    elif(Statement_Water_Hardness == 'soft'):
                            partialresult.append("Wasserhärtegrad weich")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                    else:
                            partialresult.append("Wasserhärtegrad hart")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Genutzes Waschpulver ist viel zu schwach, es wird empfohlen ein stärkeres Waschpulver zu kaufen")
                                resultpass.append("false")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
            elif(Statement_Washing_Powder_Fill_Level == 'low'):
                    partialresult.append("Waschpulverfüllhöhe ist im niedrigen Bereich")
                    if(Statement_Water_Hardness == "normal"):
                            partialresult.append("Wasserhärtegrad im normalen Bereich")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                    elif(Statement_Water_Hardness == 'soft'):
                            partialresult.append("Wasserhärtegrad weich")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                    else:
                            partialresult.append("Wasserhärtegrad hart")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Genutzes Waschpulver ist viel zu schwach, es wird empfohlen ein stärkeres Waschpulver zu kaufen")
                                resultpass.append("false")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Genutzes Waschpulver ist zu schwach, entweder stärkeres Waschpulver kaufen oder Füllmenge erhöhen")
                                resultpass.append("false")
            else:
                    partialresult.append("Waschpulverfüllhöhe ist im hohen Bereich")
                    if(Statement_Water_Hardness == "normal"):
                            partialresult.append("Wasserhärtegrad im normalen Bereich")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                    elif(Statement_Water_Hardness == 'soft'):
                            partialresult.append("Wasserhärtegrad weich")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
                    else:
                            partialresult.append("Wasserhärtegrad hart")
                            if(Statement_Washing_Powder == "normal"):
                                partialresult.append("Genutztes Waschpulver hat mittlere Stärke")
                                result.append( "Nutzung des aktuellen Waschpulvers mit der aktuellen Füllmenge optimal für den Wasserhärtegrad")
                                resultpass.append("true")
                            elif(Statement_Washing_Powder == 'weak'):
                                partialresult.append("Genutztes Waschpulver ist schwach")
                                result.append( "Genutzes Waschpulver ist viel zu schwach, es wird empfohlen ein stärkeres Waschpulver zu kaufen")
                                resultpass.append("false")
                            else:
                                partialresult.append("Genutztes Waschpulver ist stark")
                                result.append( "Nutzung des aktuellen Waschpulvers reicht vollkommen aus, Füllmenge kann reduziert werden")
                                resultpass.append("true")
            subresult.append(partialresult)
            
            
            if(self.av(Temperature)<30):
                Statement_Temperature  = "low"
            elif(self.av(Temperature)>70):
                Statement_Temperature  = "high"
            else:
                Statement_Temperature = "normal"

            if(self.av(Used_Modes) == 0):
                Statement_Used_Modes  = "lowtemperature"
            elif(self.av(Used_Modes) == 2):
                Statement_Used_Modes  = "hightemperature"
            else:
                Statement_Used_Modes = "normal"
                
            
            partialresult = []
            if(Statement_Temperature == "normal"):
                partialresult.append("Gemessene Temperatur: Mittlere Temperatur")
                if(Statement_Used_Modes == "normal"):
                    partialresult.append("Häufig genutzer Modus: Mittlere Temperatur")
                    result.append( "Beim am häufigsten genutzen Modus wurde die richtige Temperatur gemessen")
                    resultpass.append("true")
                elif(Statement_Used_Modes == 'lowtemperature'):
                    partialresult.append("Häufig genutzer Modus: Niedrige Temperatur")
                    result.append( "Heizspirale hat möglicherweise eine Überfunktion, reparieren oder austauschen")
                    resultpass.append("false")
                else:
                    partialresult.append("Häufig genutzer Modus: Hohe Temperatur")
                    result.append( "Heizspirale hat möglicherweise eine Unterfunktion, reparieren oder austauschen")
                    resultpass.append("false")
            elif(Statement_Temperature == 'low'):
                partialresult.append("Gemessene Temperatur: Niedrige Temperatur")
                if(Statement_Used_Modes == "normal"):
                    partialresult.append("Häufig genutzer Modus: Mittlere Temperatur")
                    result.append( "Heizspirale hat möglicherweise eine Unterfunktion, reparieren oder austauschen")
                    resultpass.append("false")
                elif(Statement_Used_Modes == 'lowtemperature'):
                    partialresult.append("Häufig genutzer Modus: Niedrige Temperatur")
                    result.append( "Beim am häufigsten genutzen Modus wurde die richtige Temperatur gemessen")
                    resultpass.append("true")
                else:
                    partialresult.append("Häufig genutzer Modus: Hohe Temperatur")
                    result.append( "Heizspirale hat möglicherweise eine Unterfunktion, reparieren oder austauschen")
                    resultpass.append("false")
            else:
                partialresult.append("Gemessene Temperatur: Hohe Temperatur")
                if(Statement_Used_Modes == "normal"):
                    partialresult.append("Häufig genutzer Modus: Mittlere Temperatur")
                    result.append( "Heizspirale hat möglicherweise eine Überfunktion, reparieren oder austauschen")
                    resultpass.append("false")
                elif(Statement_Used_Modes == 'lowtemperature'):
                    partialresult.append("Häufig genutzer Modus: Niedrige Temperatur")
                    result.append( "Heizspirale hat möglicherweise eine Überfunktion, reparieren oder austauschen")
                    resultpass.append("false")
                else:
                    partialresult.append("Häufig genutzer Modus: Hohe Temperatur")
                    result.append( "Beim am häufigsten genutzen Modus wurde die richtige Temperatur gemessen")
                    resultpass.append("true")
            subresult.append(partialresult)
            
            if(len(Usage_Frequency)<4):
                Statement_Usage_Frequency  = "toolow"
            elif(len(Usage_Frequency)>9):
                Statement_Usage_Frequency  = "toohigh"
            else:
                Statement_Usage_Frequency = "normal"
            
            partialresult = []
            if(Statement_Usage_Frequency == "normal"):
                partialresult.append("Nutzungshäufigkeit in der Woche: " + str(len(Usage_Frequency)))
                result.append( "Nutzungshäufigkeit ist optimal, beibehalten für eine höhere Lebenszeit")
                resultpass.append("true")
            elif(Statement_Usage_Frequency == 'toolow'):
                partialresult.append("Nutzungshäufigkeit in der Woche: " + str(len(Usage_Frequency)))
                result.append( "Waschtrockner wird zu selten genutzt")
                resultpass.append("false")
            else:
                partialresult.append("Nutzungshäufigkeit in der Woche: " + str(len(Usage_Frequency)))
                result.append( "Waschtrockner wird zu oft genutzt, Nutzungshäufigkeit reduzieren um Komponenten zu schonen")
                resultpass.append("false")
            subresult.append(partialresult) 
        
    
        else:
            result = ["no result for this Program"]
            subresult = ["Change Program"]
            resultpass  = ["false"]
        self.result = result
        self.subresult = subresult
        self.resultpass = resultpass
            
	#calculates the average result of a tuple
    def av(self, valuetuple):
        sum = 0
        for index, item in enumerate(valuetuple):
            value = item
            sum += value
        average = sum/len(valuetuple)
        return average
            
    def getresult(self):
        return self.result
    def getresultpass(self):
        return self.resultpass
    def getsubresult(self):
        return self.subresult

