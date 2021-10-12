//Un-comment the below two lines when importing for the first time
//CREATE CONSTRAINT n10s_unique_uri ON (r:Resource)
//ASSERT r.uri IS UNIQUE;

CALL n10s.graphconfig.init();
CALL n10s.onto.import.fetch("file:///C:\\Users\\ilena\\Documents\\INFOTECH\\Master Thesis\\Products\\automated-wash-dryer-system.owl", "Turtle");
CALL n10s.onto.import.fetch("file:///C:\\Users\\ilena\\Documents\\INFOTECH\\Master Thesis\\Products\\automated-wash-dryer-application.owl", "Turtle");