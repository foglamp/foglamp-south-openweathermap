FILES=__init__.py Weather.py

all: $(FOGLAMP_ROOT)/scripts updateDB
	-mkdir $(FOGLAMP_ROOT)/python/foglamp/plugins/south/Weather
	cp $(FILES) $(FOGLAMP_ROOT)/python/foglamp/plugins/south/Weather

$(FOGLAMP_ROOT)/scripts:
	-echo The environment variable FOGLAMP_ROOT must be set
	@exit 1

install: updateDB
	-mkdir /usr/local/foglamp/plugins/south/Weather
	cp $(FILES) /usr/local/foglamp/plugins/south/Weather

updateDB:
	psql < cmds.sql
