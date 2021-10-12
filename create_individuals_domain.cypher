//Device instances
MATCH (dev:n4sch__Class{n4sch__name: "Device"})
MERGE (:n4sch__Instance {n4sch__name: "Automated Wash-Dryer"}) - [:IS_TYPE] -> (dev);
 
//Goal instances
MATCH (tsk:n4sch__Class{n4sch__name: "Goals"})
MERGE (:n4sch__Instance {n4sch__name: "Detect Defect"}) - [:IS_TYPE] -> (tsk)
MERGE (:n4sch__Instance {n4sch__name: "Washing"}) - [:IS_TYPE] -> (tsk)
MERGE (:n4sch__Instance {n4sch__name: "Suggest Maintenance"}) - [:IS_TYPE] -> (tsk)
MERGE (:n4sch__Instance {n4sch__name: "Drying"}) - [:IS_TYPE] -> (tsk);

//Communication instances
MATCH (com:n4sch__Class{n4sch__name: "Communication"})
MERGE (:n4sch__Instance {n4sch__name: "NFC Tag"}) - [:IS_TYPE] -> (com)
MERGE (:n4sch__Instance {n4sch__name: "Web Server"}) - [:IS_TYPE] -> (com);

//Control instances
MATCH (ct:n4sch__Class{n4sch__name: "Control"});

//Actuator instances
MATCH (a:n4sch__Class{n4sch__name: "Actuator"})
MERGE (:n4sch__Instance {n4sch__name: "Blower", mode: "Fan Program"}) - [:IS_TYPE] -> (a)
MERGE (:n4sch__Instance {n4sch__name: "Door Lock", mode: "Door Lock Program"}) - [:IS_TYPE] -> (a) 
MERGE (:n4sch__Instance {n4sch__name: "Drain Pump", mode: "Pump Out Program"}) - [:IS_TYPE] -> (a) 
MERGE (:n4sch__Instance {n4sch__name: "Drum Motor", mode: "Drum Motor Program"}) - [:IS_TYPE] -> (a) 
MERGE (:n4sch__Instance {n4sch__name: "Water Heater", mode: "Long Time Check"}) - [:IS_TYPE] -> (a) 
MERGE (:n4sch__Instance {n4sch__name: "Water Inlet Valve", mode: "Water Inlet Program"}) - [:IS_TYPE] -> (a) ;

//Sensor instances
MATCH (sn:n4sch__Class{n4sch__name: "Sensor"})
MERGE (:n4sch__Instance {n4sch__name: "Temperature Sensor", type: "Internal", mode: "Long Time Check"}) - [:IS_TYPE] -> (sn)
MERGE (:n4sch__Instance {n4sch__name: "Ambient Temperature Sensor", type: "External"}) - [:IS_TYPE] -> (sn)
MERGE (:n4sch__Instance {n4sch__name: "Ambient Humidity Sensor", type: "External"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Washing Powder Fill Level Sensor", type: "Internal", mode: "Long Time Check"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Door Lock Sensor", type: "Internal", mode: "Door Lock Program"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Loudness Sensor", type: "Internal", mode: ["Drum Motor Program", "Fan Program"]}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Vibration Sensor", type: "Internal", mode: ["Drum Motor Program", "Fan Program"]}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Mass Air Flow Sensor", type: "Internal", mode: "Fan Program"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Pressure Sensor", type: "Internal", mode: "Door Lock Program"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Rotation Speed Sensor", type: "Internal", mode: "Drum Motor Program"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Water Flow Sensor", type: "Internal", mode: ["Water Inlet Program", "Pump Out Program"]}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Water Fill Level Sensor", type: "Internal", mode: ["Water Inlet Program", "Pump Out Program"]}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Laundry Fill Level Sensor", type: "Internal", mode: "Long Time Check"}) - [:IS_TYPE] -> (sn) 
MERGE (:n4sch__Instance {n4sch__name: "Laundry Weight Sensor", type: "Internal", mode: "Long Time Check"}) - [:IS_TYPE] -> (sn) ;
 
