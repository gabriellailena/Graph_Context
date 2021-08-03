from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import json
import pickle
import os
import time
from contextmodel.contextmodel import contextmodel
from contextmodel.sql_preprocessing import sql_to_graph
from contextmodel.context_analysis import analyze_context
app = Flask(__name__)

# Configure MySQL db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:admin@localhost:3306/contextmodeldata'
db = SQLAlchemy(app)
conn = db.engine.connect().connection

# Configure Neo4j db
uri = "bolt://localhost:7687"
username = "admin"
password = "admin"
graph_db = "rdfmodel"

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
			print('Request json string is: {}'.format(reqJson))

			# Stores the data into MySQL Database sensordata
			for item in range(range_data):
				session = db.session()
				session.execute("INSERT INTO sensordata (phase, sensor, desired_value_type, desired_value, observed_value) VALUES (%s,%s,%s,%s,%s)" ,
						(phase[item], sensor[item], desiredValueType[item], desiredValue[item], observedValue[item]))
				session.commit()
			
			session.close()
			return "Success!!!"
		else:
			# Creates context model and fetches the result
			c = contextmodel(app, db, reqJson)
			result = c.getresult()
			subresult = c.getsubresult()
			resultpass = c.getresultpass()

			# Creates JSON with the results
			jsondata  = {}
			jsondata['result'] = result
			jsondata['subresult'] = subresult
			jsondata['passresult'] = resultpass

			# Exports sql data to .csv
			t0 = time.clock()
			out_path = "C:\\Users\\ilena\\.Neo4jDesktop\\relate-data\\dbmss\\dbms-1a688a58-6f36-4dce-99e7-a26342fefc17\\import\\contextdata.csv"
			sql_to_graph(uri=uri, username=username, password=password, connection=conn, file_path=out_path,
						 db_name=graph_db)
			t1 = time.clock() - t0
			print("Export finished in ", t1, "seconds.")

			# Stores result into pickle
			filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
			with open(filename, "wb") as fp:   # Pickling
				pickle.dump(jsondata, fp)
			return "Success!!!"


	else:
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

@app.route("/contextresult")
def sendresultjson():
	# Shows the result of the context model if it's available
	try:
		filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
		with open(filename, "rb") as fp:
			jsondata = pickle.load(fp)
	except Exception:
		jsondata = []
	json_data  = json.dumps(jsondata)
	return json_data

@app.route("/deletecontextresult")
def getdeletejson():
	# Deletes the context result, is used when application has already fetched the result
	try:
		filename = os.path.dirname(__file__) + "\\contextmodel\\contextdata\\Result\\contextresultjson.txt"
		os.remove(filename)
	except Exception:
		pass


if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)
