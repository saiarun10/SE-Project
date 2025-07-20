#!/bin/bash

# ==============================================================================
# Diagram & File Tree Generation Script
# ==============================================================================
# This script automates the creation of:
# 1. A file tree of the project, excluding specified directories and files.
# 2. A Class Diagram from Python source code using pyreverse and PlantUML.
# 3. An Entity-Relationship Diagram (ERD) from a SQLite database.
# 4. A Swagger/OpenAPI documentation file in YAML format.
#
# This script is configured with specific paths for the SE-Project structure
# and saves all output to a centralized 'supplementary_files' directory.
#
# Prerequisites:
# - tree
# - pyreverse (pip install pylint)
# - eralchemy2 (pip install eralchemy2)
# - graphviz (sudo apt-get install graphviz or brew install graphviz)
# - PlantUML (Requires plantuml.jar in the same directory as this script)
# - PyYAML (pip install PyYAML)
# - Flask (pip install Flask)
# ==============================================================================

# --- Configuration ---
# Get the directory where the script is located (the 'backend' folder).
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# --- Project Structure and Output Configuration ---
# The output directory is an absolute path.
SUPPLEMENTARY_DIR="/home/shib/Documents/SE-Project/supplementary_files"

# Source files and directories are relative to the script's location.
DATABASE_FILE="instance/database.db"
MODEL_FILE="model.py"
ROUTES_DIR="routes"
# Corrected the name of the swagger generation script
SWAGGER_SCRIPT="generate_swagger_yaml.py"

# Create the output directory if it doesn't exist
mkdir -p "$SUPPLEMENTARY_DIR"

# --- Output File Names ---
# Intermediate files are created in the script's directory and then removed.
# Final output files are saved in the 'supplementary_files' directory.
FILE_TREE_OUTPUT="$SUPPLEMENTARY_DIR/file_tree.txt"
CLASS_DIAGRAM_PUML="class_diagram.puml" # Intermediate file
CLASS_DIAGRAM_PNG="$SUPPLEMENTARY_DIR/class_diagram.png"
ERD_DOT="database_erd.dot" # Intermediate file
ERD_PNG="$SUPPLEMENTARY_DIR/database_erd.png"
SWAGGER_YAML_OUTPUT="$SUPPLEMENTARY_DIR/swagger_documentation.yaml"

echo "Starting file generation..."
echo "All output will be saved to: $SUPPLEMENTARY_DIR/"
echo "--------------------------------------------------"

# 1. Generate File Tree
# ---------------------
# Excludes common virtual environment, cache, git, and generated files/folders.
echo "Step 1: Generating project file tree..."
# The 'tree' command is run on the parent directory of the script ('../')
# Updated exclusion list to match the correct swagger script name.
tree -a -I "venv|__pycache__|.git|node_modules|instance|supplementary_files|diagrams|create_diagram.sh|generate_swagger_yaml.py|*.db" ../ > "$FILE_TREE_OUTPUT"
if [ $? -eq 0 ]; then
    echo "Success: File tree saved to $FILE_TREE_OUTPUT"
else
    echo "Error: Failed to generate file tree. Is 'tree' installed?"
fi
echo "--------------------------------------------------"


# 2. Generate Class Diagram
# -------------------------
# This uses pyreverse to generate a .puml file from the model and routes.
echo "Step 2: Generating class diagram..."
pyreverse "$ROUTES_DIR" "$MODEL_FILE" -o plantuml -p Diagram
if [ $? -eq 0 ]; then
    # Check if the expected output file was actually created before trying to move it.
    if [ -f "classes_Diagram.puml" ]; then
        mv "classes_Diagram.puml" "$CLASS_DIAGRAM_PUML"
        echo "Success: PlantUML file created as $CLASS_DIAGRAM_PUML"

        if [ -f "plantuml.jar" ]; then
            echo "Found plantuml.jar. Converting to PNG..."
            # Tell plantuml to use the specified output directory.
            # It will automatically create a .png with the same name as the input .puml file.
            java -jar plantuml.jar "$CLASS_DIAGRAM_PUML" -o "$(dirname "$CLASS_DIAGRAM_PNG")"
            if [ $? -eq 0 ]; then
                echo "Success: Class diagram saved to $CLASS_DIAGRAM_PNG"
                rm "$CLASS_DIAGRAM_PUML" # Clean up intermediate file
            else
                echo "Error: Failed to convert .puml to .png. Check Java and plantuml.jar."
            fi
        else
            echo "Warning: 'plantuml.jar' not found. Skipping PNG conversion."
        fi
    else
        echo "Warning: pyreverse ran successfully but did not generate a 'classes_Diagram.puml' file. Skipping class diagram."
    fi
else
    echo "Error: Failed to generate class diagram. Is 'pyreverse' (pylint) installed?"
fi
echo "--------------------------------------------------"


# 3. Generate ERD Diagram
# -----------------------
# This uses eralchemy to create a .dot file and graphviz to render it as a PNG.
echo "Step 3: Generating ERD from database..."
if [ -f "$DATABASE_FILE" ]; then
    eralchemy -i "sqlite:///$SCRIPT_DIR/$DATABASE_FILE" -o "$ERD_DOT"
    if [ $? -eq 0 ]; then
        echo "Success: ERD .dot file created as $ERD_DOT"
        dot -Tpng "$ERD_DOT" -o "$ERD_PNG"
        if [ $? -eq 0 ]; then
            echo "Success: ERD image saved to $ERD_PNG"
            rm "$ERD_DOT" # Clean up intermediate file
        else
            echo "Error: Failed to convert .dot to .png. Is 'graphviz' installed?"
        fi
    else
        echo "Error: Failed to generate .dot file. Is 'eralchemy2' installed?"
    fi
else
    echo "Error: Database file '$SCRIPT_DIR/$DATABASE_FILE' not found. Skipping ERD generation."
fi
echo "--------------------------------------------------"


# 4. Generate Swagger YAML Documentation
# ----------------------------------------
# This runs a python script to generate the swagger.yaml file.
echo "Step 4: Generating Swagger YAML documentation..."
if [ -f "$SWAGGER_SCRIPT" ]; then
    # Run the python script, passing the absolute output directory as an argument
    python3 "$SWAGGER_SCRIPT" "$SUPPLEMENTARY_DIR"
    if [ $? -eq 0 ]; then
        echo "Success: Swagger YAML saved to $SWAGGER_YAML_OUTPUT"
    else
        echo "Error: Failed to generate Swagger YAML. Check the python script and dependencies."
    fi
else
    echo "Error: Swagger generation script '$SWAGGER_SCRIPT' not found. Skipping."
fi
echo "--------------------------------------------------"

echo "Script finished."
