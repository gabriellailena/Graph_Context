//Anomaly instances
MATCH (an:n4sch__Class{n4sch__name: "Anomaly"})
MERGE (:n4sch__Instance {n4sch__name: "Actuator Defect"}) - [:IS_TYPE] -> (an)
MERGE (:n4sch__Instance {n4sch__name: "Sensor Defect"}) - [:IS_TYPE] -> (an)
MERGE (:n4sch__Instance {n4sch__name: "Hard Water"}) - [:IS_TYPE] -> (an)
MERGE (:n4sch__Instance {n4sch__name: "Position"}) - [:IS_TYPE] -> (an)
MERGE (:n4sch__Instance {n4sch__name: "Foreign Object"}) - [:IS_TYPE] -> (an)
MERGE (:n4sch__Instance {n4sch__name: "Undefined"}) - [:IS_TYPE] -> (an)
MERGE (:n4sch__Instance {n4sch__name: "Power Supply"}) - [:IS_TYPE] -> (an);

//Usage instances
MATCH (us:n4sch__Class{n4sch__name: "Usage_Optimization"})
MERGE (:n4sch__Instance {n4sch__name: "Reduce Detergent"}) - [:IS_TYPE] -> (us)
MERGE (:n4sch__Instance {n4sch__name: "Stronger/More Detergent"}) - [:IS_TYPE] -> (us)
MERGE (:n4sch__Instance {n4sch__name: "Reduce Laundry"}) - [:IS_TYPE] -> (us)
MERGE (:n4sch__Instance {n4sch__name: "Run Diagnosis Programs"}) - [:IS_TYPE] -> (us)
MERGE (:n4sch__Instance {n4sch__name: "Reduce Usage Frequency"}) - [:IS_TYPE] -> (us)
MERGE (:n4sch__Instance {n4sch__name: "Increase Laundry"}) - [:IS_TYPE] -> (us);

//Message instances
MATCH (m:n4sch__Class{n4sch__name: "Message"})
MERGE (:n4sch__Instance {n4sch__name: "Error message", cause: ["Actuator Defect", "Sensor Defect"], message: "Component defect detected. Please check the related component(s): -foo-"}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Warning message", cause: ["Hard Water"], message: "Water hardness level is high. Higher diagnosis frequency is recommended."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Warning message", cause: ["Power Supply"], message: "Motor is working too hard. Please check the power supply for defects."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Undefined message", cause: ["Undefined"], message: "Cause of defects/abnormal behavior is undefined. Consider running another diagnosis program."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Error message", cause: ["Position"], message: "Please check and re-adjust the drum position as it may have caused system disturbances."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Error message", cause: ["Foreign Object"], message: "Please check for possible foreign object(s) inside the following component(s): -foo-"}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Suggestion", cause: ["Reduce Detergent"], message: "Amount of detergent can be reduced for more effective washing."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Suggestion", cause: ["Stronger/More Detergent"], message: "Please use a stronger detergent or add more detergent for more optimal washing with the current water hardness level."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Suggestion", cause: ["Reduce Laundry"], message: "Reduce the amount/weight of laundry to preserve machine lifetime."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Suggestion", cause: ["Increase Laundry"], message: "Increase the amount/weight of laundry to maximize energy usage."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Suggestion", cause: ["Reduce Usage Frequency"], message: "Consider decreasing your washing frequency to save energy."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Suggestion", cause: ["Run Diagnosis Programs"], message: "The washing machine is seldom used, consider running other diagnosis programs to check for possible defects/necessary maintenance."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Normal message", message: "The following component(s): -foo- is/are working properly."}) - [:IS_TYPE] -> (m)
MERGE (:n4sch__Instance {n4sch__name: "Optimal message", message: "-foo- is/are optimal."}) - [:IS_TYPE] -> (m);

