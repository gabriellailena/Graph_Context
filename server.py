from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
import yaml
import json
import pickle
import os
import time
from contextmodel.contextmodel import contextmodel
from contextmodel.sql_preprocessing import sql_to_graph
from contextmodel.context_analysis import analyze_context
from contextmodel.rules_embedding import rules_to_graph
app = Flask(__name__)

# Configure db
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

# Configure Neo4j db
uri = "neo4j+s://acbe0929.databases.neo4j.io"
#uri = "bolt://localhost:7687"
username = "admin"
password = "admin"
graph_db = "neo4j"
#graph_db = "rdfmodel"

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        # Get the json data and insert into the DataBase
        reqJson = request.get_json()
        if(reqJson['nameValuePairs']['mode'] == False):
            phase = reqJson['nameValuePairs']['phase']
            sensor = reqJson['nameValuePairs']['sensor']
            desiredValueType = reqJson['nameValuePairs']['desiredValueType']
            desiredValue = reqJson['nameValuePairs']['desiredValue']
            observedValue = reqJson['nameValuePairs']['observedValue']
            
            range_data = len(phase)
            print ('Request json string is: {}'.format(reqJson))
            
            cur = mysql.connection.cursor()
            
            #stores the data into MySQL Database sensordata
            for item in range(range_data):
                cur.execute("INSERT INTO sensordata (phase, sensor, desired_value_type, desired_value, observed_value) VALUES (%s,%s,%s,%s,%s)" , 
                            (phase[item], sensor[item], desiredValueType[item], desiredValue[item], observedValue[item]))
                mysql.connection.commit()
            
            cur.close()
            return "Success!!!"
        else: 	
            #creates ContextModel and fetches the result
            c =  contextmodel(app, db, reqJson, mysql)
            result = c.getresult()
            subresult = c.getsubresult()
            resultpass = c.getresultpass()
            
            #creates JSON with the results
            jsondata  = {}
            jsondata['result'] = result
            jsondata['subresult'] = subresult
            jsondata['passresult'] = resultpass
        
			#stores result into pickle
            filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
            with open(filename, "wb") as fp:   #Pickling
                pickle.dump(jsondata, fp)
        return "Success!!!"
    else:
        # Exports sql data to .csv
        t0 = time.process_time()
        out_path = "C:\\Users\\ilena\\Dropbox\\context_data.csv"
        sql_to_graph(uri=uri, username=username, password=password, file_path=out_path,
        					 db_name=graph_db)
        t1 = time.process_time() - t0
        print("Export finished in ", t1, "seconds.")
        return render_template('index.html')
		
@app.route('/diagnosis_result')
def show_analysis_results():
	result = analyze_context(uri=uri, username=username, password=password, db_name=graph_db)
	return render_template('diagnosis.html', result=result)

@app.route('/usage')
def show_usage():
	result = analyze_context(uri=uri, username=username, password=password, db_name=graph_db)
	return render_template('usage.html', result=result)

@app.route('/context_model')
def show_viz():
	return render_template('model_visualization.html')

# Run this only one time to embed the state combinations as rules
@app.route('/embed_rules')
def embed_rules():
	rules_to_graph(uri=uri, username=username, password=password, db_name=graph_db)
	return "Rules embedding complete."

@app.route('/data')
def fetchData():
	#fetches the normal sensortable
	cur = mysql.connection.cursor()
	resultValue = cur.execute("SELECT * FROM sensordata")
	if resultValue > 0:
		data = cur.fetchall()
		return render_template('data.html', data=data)

@app.route('/contextdata')
def fetchContextData():
	#fetches the contextdata from MySQL and displays it on WebPage
	cur = mysql.connection.cursor()
	resultValue = cur.execute("SELECT * FROM graphcontextdata")
	if resultValue > 0:
		data = cur.fetchall()
		return render_template('contextdata.html', data=data)
@app.route("/contextresult")
def sendresultjson():
#shows the result of the contextmodel if it's available
	try:
		filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
		with open(filename, "rb") as fp:
			jsondata = pickle.load(fp)
	except Exception:
		jsondata = []
	json_data  = json.dumps(jsondata)
	print("data deleted")
	try:
		filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
		os.remove(filename)
		print("data deleted")
	except Exception:
		pass
	return json_data

@app.route("/deletecontextresult")
def getdeletejson():
#deletes the contextresult, is used when application has already fetched the result
	print("data deleted")
	try:
		filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
		os.remove(filename)
		print("data deleted")
	except Exception:
		pass

@app.route("/contextmodelcheck")
def checkcontextmodel():
#experimental, only for programmer, if he wants to check if the contextmodel works without the need of the application
	reqJson = {'nameValuePairs': {'mode': 'true', 'diagnosisMode': 'Complete Short Program', 'phase': [1, 1], 'sensor': ['Drucksensor', 'Drucksensor'], 'desiredValueType': ['greaterOrEqual', 'lowerOrEqual'], 'desiredValue': [20, 5], 'observedValue': [58, 58], 'time': ['dd','32'], 'unit': ['23','23']}}
	c =  contextmodel(app, db, reqJson, mysql)
	result = c.getresult()
	subresult = c.getsubresult()
	resultpass = c.getresultpass()
	jsondata  = {}
	jsondata['result'] = result
	jsondata['subresult'] = subresult
	jsondata['passresult'] = resultpass
	filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
	with open(filename, "wb") as fp:   #Pickling
		pickle.dump(jsondata, fp)
	return jsondata


if __name__ == '__main__':
	app.run(host="0.0.0.0",port=5000,debug = True)
