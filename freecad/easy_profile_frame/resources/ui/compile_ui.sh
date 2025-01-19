#!/bin/bash

# Loop through all .ui files in the current directory
for ui_file in *.ui; do
    # Check if there are any .ui files in the directory
    if [ -e "$ui_file" ]; then
        # Generate the corresponding .py file name by replacing the .ui extension with .py
        py_file="${ui_file%.ui}.py"

        # Use pyside6-uic to compile the .ui file into a .py file
        echo "Compiling $ui_file to $py_file..."
        pyside6-uic "$ui_file" -o "$py_file"

        # Check if the compilation was successful
        if [ $? -eq 0 ]; then
            echo "Successfully compiled $ui_file to $py_file."
        else
            echo "Failed to compile $ui_file."
        fi
    else
        echo "No .ui files found in the current directory."
        break
    fi
done