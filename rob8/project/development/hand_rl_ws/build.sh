#!/usr/bin/bash

catkin_make --cmake-args "-DCMAKE_EXPORT_COMPILE_COMMANDS=On"

echo "Sourcing workspace..."
source devel/setup.bash
echo "Done"
