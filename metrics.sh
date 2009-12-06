#!/bin/sh

server_dir="Flimsy/flimsy"
server_files="controllers/map.py public/scripts/map.js templates/map.html"
server_tests="tests/functional/test_sensor.py"

echo "---Coordinator---"
echo "Test lines of code"
wc -l coordinator/test*.py
echo "Total lines of code"
wc -l coordinator/*.py
echo "---Server---"
cd $server_dir
echo "Test lines of code"
wc -l $server_tests
echo "Total lines of code"
wc -l $server_files $server_tests
