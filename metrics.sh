#!/bin/sh

echo "Test lines of code"
wc -l coordinator/test*.py
echo "Total lines of code"
wc -l coordinator/*.py
