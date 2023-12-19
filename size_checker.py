import PySimpleGUI as sg
import os
import json

# Function to compare the sizes of applications in the selected folder with item_sizes.json
def compare_sizes(selected_folder, item_sizes):
    result_data = []
    missing_apps = set(item_sizes.keys())
    
    for root, dirs, files in os.walk(selected_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.basename(file_path) in item_sizes:
                size = os.path.getsize(file_path)
                expected_size = item_sizes[os.path.basename(file_path)]  # Convert expected size to bytes
                if int(size) == int(expected_size):  # Convert both sizes to integers for accurate comparison
                    status = "Pass"
                else:
                    status = "Failed"
                missing_apps.discard(os.path.basename(file_path))
                result_data.append((os.path.basename(file_path), size, expected_size, status))
    
    for missing_app in missing_apps:
        result_data.append((missing_app, "N/A", item_sizes.get(missing_app, "N/A"), "Missing"))
    
    return result_data

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
item_sizes_path = os.path.join(script_dir, "item_sizes.json")

# Load item_sizes.json
try:
    with open(item_sizes_path, 'r') as json_file:
        item_sizes = json.load(json_file)
except FileNotFoundError:
    sg.popup_error("item_sizes.json not found. Please make sure it's in the same directory as this script.")
    item_sizes = {}

# Layout for Page 2: Size Checker
page2_layout = [
    [
        sg.Text("Select a folder to compare with item_sizes.json:"),
        sg.InputText(key="-FOLDER-"),
        sg.FolderBrowse(),
        sg.Button("Compare", key="-COMPARE-"),
    ],
    [
        sg.Table(
            values=[],  # Data will be updated when comparing
            headings=["Application", "Retrieval Size (Bytes)", "Expected Size (Bytes)", "Status"],  # Updated column headers
            auto_size_columns=False,
            justification="left",
            num_rows=20,  # Increased table size
            key="-TABLE2-",
            col_widths=[40, 20, 20, 20],  # Adjust column widths as needed
        )
    ]
]

# Create the PySimpleGUI window for Page 2
window = sg.Window("Size Checker", page2_layout, finalize=True, size=(1000, 600))  # Increased window size

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "-COMPARE-":
        folder_to_compare = values["-FOLDER-"]
        if folder_to_compare:
            # Compare the sizes and update the table
            result_data = compare_sizes(folder_to_compare, item_sizes)
            window["-TABLE2-"].update(values=result_data)

window.close()
