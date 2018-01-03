--- Database commands to insert the new plugin into FogLAMP

--- Create the south service instannce
INSERT INTO foglamp.scheduled_processes ( name, script ) VALUES ( 'Weather', '["services/south"]');

--- Add the schedule to start the service at system startup
INSERT INTO foglamp.schedules ( id, schedule_name, process_name, schedule_type,schedule_interval, exclusive )
     VALUES ( '543a59ce-a9ca-11e7-abc4-cec278b6b21d', 'Weather', 'Weather', 1, '0:0', true );

--- Insert the config needed to load the plugin
INSERT INTO foglamp.configuration ( key, description, value )
     VALUES ( 'Weather', 'Weather report from Open Weather Map',
	      '{"plugin" : { "type" : "string", "value" : "Weather", "default" : "Weather", "description" : "Plugin to load" } }' );

