# MBTA train times for adafruit matrix

display the current MBTA arrival times on an adafruit matrix

Developed for matrix portal m4 and LED matrix panel (32x64) from adafruit

Requires adafruit account for time syncing, and a wifi network (provide these credentails in secrets)

Also may require you to install libraries onto the matrix portal (see imports)

For MBTA api documentation see this page: https://api-v3.mbta.com/docs/swagger/index.html#/Schedule/ApiWeb_ScheduleController_index

You will probably want to change the line and station, which is done by editing the constants at the top of the code.py file based on the MBTA documentation.
