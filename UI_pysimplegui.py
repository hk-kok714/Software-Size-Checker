import PySimpleGUI as sg
import subprocess
import os
import json
import winreg
import win32con
from fuzzywuzzy import fuzz
from packaging import version
import re
import operator


search_text_page1 = ""  # For Page 1
search_text_page2 = ""  # For Page 2
folder_path = "" # Define as Global Variable

def compare_sizes(selected_folder, item_sizes):
    
    result_data = []
    missing_apps = set(item_sizes.keys())
    
    for root, dirs, files in os.walk(selected_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.basename(file_path) in item_sizes:
                size = os.path.getsize(file_path)
                expected_size = item_sizes[os.path.basename(file_path)]  # Reference value
                missing_apps.discard(os.path.basename(file_path))
                result_data.append((os.path.basename(file_path), expected_size, size, "Pass" if int(size) == int(expected_size) else "Failed"))
    
    for missing_app in missing_apps:
        result_data.append((missing_app, item_sizes.get(missing_app, "N/A"), "N/A", "Missing"))
    
    return result_data



# Function to handle the search logic
def perform_search(search_text, table_data):
    # Filter the table_data to include only rows where the software name contains the search_text
    filtered_data = [row for row in table_data if search_text in row[1].lower()]
  
    # Update the table with the filtered data for Page 1
    window["-TABLE-"].update(values=filtered_data)


def perform_size_search(search_text, table_data):
    # Filter the table_data to include only rows where the software name contains the search_text
    filtered_data = [row for row in table_data if search_text in row[0].lower()]

    # Update the table with the filtered data for Page 2
    window["-SIZE_TABLE-"].update(values=filtered_data)


# Function to create the layout for Page 2: Software Checker
def create_page1_layout():
    layout = [
        [
            sg.Button("Check", key="-CHECK-"),  
        ],
        [
           sg.InputText(key="-SEARCH-", size=(20, 1), do_not_clear = True, enable_events=True),
            sg.Button("Search", key="-SEARCH_BUTTON-"),
        ],
        [
            sg.Table(
                values=[],
                headings=["List", "Software", "Required Version", "Installed Version", "Status"],
                auto_size_columns=False,
                justification="left",
                num_rows=20,
                key="-TABLE-",
                col_widths=[10, 40, 20, 20, 20],
                background_color="#045D5D",
                text_color="white",
                bind_return_key=True,
                row_colors=[("white", "#045D5D"), ("white", "yellow"), ("white", "red")],
                enable_events = True,
                enable_click_events = True
            ),
        ],
        [
            sg.Column(layout=[
                [sg.Frame('Software Found Info', font=("Helvetica", 12, "bold"), layout=[
                    [sg.Text("Number of Required Softwares:"), sg.Text("0", key="-REQUIRED-")],
                    [sg.Text("Number of Matched Version Software:"), sg.Text("0", key="-MATCHED_VERSION-")],
                    [sg.Text("Number of Softwares Found:"), sg.Text("0", key="-FOUND-")],
                    [sg.Text("Number of Softwares Not Found:"), sg.Text("0", key="-NOT_FOUND-")],
                ], element_justification="left", size=(445, 150))],
            ]),
            sg.Column(layout=[
                [sg.Frame('List of Missing/Failed Status', font=("Helvetica", 12, "bold"), layout=[
                    [sg.Multiline("", key="-MISSING_FAILED-", size=(80, 10), disabled=True, background_color="#045D5D", text_color="white")], 
                ], element_justification="left", size=(445, 250))],  
            ]),
        ],
    ]

    return layout


def create_page2_layout():
    
# Determine the display path based on the availability of 'Tools' and 'GNU' folders
    paths_to_check = ["C:\\Tools\\GNU", "C:\\Tools"]

    for path in paths_to_check:
        if os.path.exists(path):
            display_path = path
            break
    else:
        display_path = "C"

     

    layout = [
        [
            sg.Text("                                GNU Folder Directory Path:"),
            sg.InputText(default_text = display_path, key="-FOLDER-", readonly=True, text_color="#045D5D", background_color="White", disabled_readonly_background_color="White"),
            sg.Button("Browse", key="-CHECK_SIZE-"), 

        ],
        [
            sg.InputText(key="-SEARCH_SIZE-", size=(20, 1), do_not_clear=True, enable_events=True),
            sg.Button("Search", key="-SEARCH_BUTTON_SIZE-"),
            
        ],
        [
            sg.Table(
                values=[],  # Data will be updated when comparing
                headings=["Application", "Expected Size (Bytes)", "Retrieval Size (Bytes)", "Status"],
                auto_size_columns=False,
                justification="left",
                num_rows=20,  # Increased table size
                key="-SIZE_TABLE-",
                col_widths=[40, 20, 20, 20],  # Adjust column widths as needed
                background_color="#045D5D",
                text_color="white",
                bind_return_key=True,  # This enables row coloring
                row_colors=[("white", "#045D5D"), ("white", "yellow"), ("white", "red")],
                enable_events = True,
                enable_click_events = True
            ),
        ],
        [
            sg.Column(layout=[
                [sg.Frame('Size Found Info', font=("Helvetica", 12, "bold"), layout=[
                    [sg.Text("Number of Required Size:"), sg.Text("98", key="-REQUIRED_SIZE-")],
                    [sg.Text("Number of Matched Sizes Found:"), sg.Text("0", key="-MATCHED_SIZE-")], 
                    [sg.Text("Number of Sizes Found:"), sg.Text("0", key="-FOUND_SIZE-")],
                    [sg.Text("Number of Sizes Not Found:"), sg.Text("0", key="-NOT_FOUND_SIZE-")],
                ], element_justification="left", size=(445, 150))],
            ]),
            sg.Column(layout=[
                [sg.Frame('List of Incorrect Sizes Applications', font=("Helvetica", 12, "bold"), layout=[
                    [sg.Multiline("", key="-INCORRECT_SIZES-", size=(80, 10), disabled=True, background_color="#045D5D", text_color="white")],  
                ], element_justification="left", size=(445, 250))],  
            ]),
        ],
    ]

    return layout


def run_size_check(folder_path):
    try:
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

        if folder_path:
            # Compare the sizes and update the table
            result_data = compare_sizes(folder_path, item_sizes)
            window["-SIZE_TABLE-"].update(values=result_data)

            # Calculate the number of matched sizes found (Pass status)
            num_matched_sizes = sum(1 for _, _, _, status in result_data if status == "Pass")

            # Calculate the number of sizes found (total items in the table)
            num_sizes_found = len(result_data)

            # Calculate the number of sizes not found (Number of Required Size - Number of Sizes Found)
            num_required_size = int(window["-REQUIRED_SIZE-"].get())

            # Calculate the number of "Missing" statuses
            num_missing_sizes = sum(1 for _, _, _, status in result_data if status == "Missing")

            # Update the corresponding GUI elements
            window["-MATCHED_SIZE-"].update(num_matched_sizes)
            window["-FOUND_SIZE-"].update(num_sizes_found)
            window["-NOT_FOUND_SIZE-"].update(num_missing_sizes)  # Update with the count of "Missing" statuses

            # Collect names of incorrect sizes applications
            incorrect_sizes_list = [
                (app, status, item_sizes.get(app, "N/A")) for app, _, _, status in result_data if status in ("Failed", "Missing")
            ]

            # Update the "List of Incorrect Sizes Applications"
            window["-INCORRECT_SIZES-"].update("\n".join([f"{app}: {status}, Expected Size: {expected_size}" for app, status, expected_size in incorrect_sizes_list]))
    except Exception as e:
        sg.popup_error(f"An error occurred while checking folder size: {e}")

# Function to run "Main_21.py" when the "Check" button is clicked
def run_main_21():
    try:
        # Merge the existing data with the new data for current PC software
        current_pc_output_file = merge_current_pc_data("currentpc_software.json")

        # Load software data
        software_data = load_software_data('C:/Users/hai-kent.kok/Desktop/My/software.json')
        
        # Load current PC data
        current_pc_data = load_current_pc_data(current_pc_output_file)
        
        # Generate results
        results = generate_results(software_data, current_pc_data)

        # Define the output file path for the results
        results_output_file = "results.json"
        
        # Combine the script directory and relative output file path for results
        script_directory = os.path.dirname(os.path.abspath(__file__))
        results_output_file = os.path.join(script_directory, results_output_file)

        # Save the results to the JSON file
        with open(results_output_file, 'w') as results_file:
            json.dump(results, results_file, indent=4)

        # After running Main_21.py, update the table with the latest data
        update_gui()
    except Exception as e:
        sg.popup_error(f"An unexpected error occurred: {e}")

# Function to load software data
def load_software_data(file_path):
    with open(file_path, 'r') as software_file:
        return json.load(software_file)['software_list']

# Function to load current PC data
def load_current_pc_data(file_path):
    with open(file_path, 'r') as current_pc_file:
        return json.load(current_pc_file)

# Function to update the table with the latest data and row colors
def update_gui():
    try:
        # Load the latest data from "results.json"
        with open('C:/Users/hai-kent.kok/Desktop/My/results.json', 'r') as json_file:
            results = json.load(json_file)

        updated_data = [
            [i + 1, software, result_data["Required Version"], result_data["Installed Version"], result_data["Status"]]
            for i, (software, result_data) in enumerate(results.items())
        ]

        # Calculate other statistics and update labels
        num_required = len(results)
        num_matched_version = len([result_data for result_data in results.values() if result_data["Status"] == "Pass"])
        num_found = len([result_data for result_data in results.values() if result_data["Status"] in ["Pass", "Failed"]])
        num_not_found = len([result_data for result_data in results.values() if result_data["Status"] == "Missing"])

        window["-REQUIRED-"].update(num_required)
        window["-MATCHED_VERSION-"].update(num_matched_version)
        window["-FOUND-"].update(num_found)
        window["-NOT_FOUND-"].update(num_not_found)

        # Create a list of row colors based on the "Status" column
        row_colors = []
        for _, _, _, _, status in updated_data:
            if status == "Failed":
                row_colors.append(("white", "red"))  # White text on red background for "Failed"
            elif status == "Missing":
                row_colors.append(("white", "yellow"))  # White text on yellow background for "Missing"
            else:
                row_colors.append(("white", "#045D5D"))  # White text on default background

        # Update the table with the latest data and row colors
        window["-TABLE-"].update(values=updated_data, row_colors=row_colors)

        # Update the "List of Missing/Failed Status"
        missing_failed_list = [
            f"{software}: {result_data['Status']}"
            for software, result_data in results.items()
            if result_data['Status'] in ["Failed", "Missing"]
        ]
        window["-MISSING_FAILED-"].update("\n".join(missing_failed_list))
    except Exception as e:
        sg.popup_error(f"An error occurred while updating the table: {e}")

# Function to merge existing data with new data for current PC software
def merge_current_pc_data(output_file):
    installed_programs = get_installed_programs()
    
    # Get the absolute path of the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Combine the script directory and relative output file path for current PC software
    output_file = os.path.join(script_directory, output_file)
    
    # Clear the contents of the existing file before saving
    with open(output_file, 'w') as json_file:
        json.dump([], json_file)

    # Merge the existing data with the new data
    updated_data = installed_programs

    # Save the updated data to the JSON file for current PC software
    save_to_json(updated_data, output_file)

    return output_file

# Function to get a list of installed programs on the current PC
def get_installed_programs():
    program_list = []

    # Define the flags for 32-bit and 64-bit views
    flags = [win32con.KEY_WOW64_32KEY, win32con.KEY_WOW64_64KEY]

    # Connect to the Uninstall registry keys for each flag and HKEY_CURRENT_USER
    reg_hives = [win32con.HKEY_LOCAL_MACHINE, win32con.HKEY_CURRENT_USER]

    for reg_hive in reg_hives:
        for flag in flags:
            try:
                aReg = winreg.ConnectRegistry(None, reg_hive)
                aKey = winreg.OpenKey(aReg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, win32con.KEY_READ | flag)
                count_subkey = winreg.QueryInfoKey(aKey)[0]

                for i in range(count_subkey):
                    try:
                        asubkey_name = winreg.EnumKey(aKey, i)
                        asubkey = winreg.OpenKey(aKey, asubkey_name)
                        program = {}

                        program['Name'] = winreg.QueryValueEx(asubkey, "DisplayName")[0]
                        program['Version'] = winreg.QueryValueEx(asubkey, "DisplayVersion")[0]
                        program['Publisher'] = winreg.QueryValueEx(asubkey, "Publisher")[0]

                        # Try to retrieve the installation directory
                        try:
                            program['InstallLocation'] = winreg.QueryValueEx(asubkey, "InstallLocation")[0]
                        except EnvironmentError:
                            program['InstallLocation'] = None

                        program_list.append(program)
                    except EnvironmentError:
                        continue

            except Exception as e:
                print(f"Error accessing registry: {e}")

    return program_list

# Function to save data to a JSON file
def save_to_json(data, output_file):
    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Function to match installed items with required items
def match_item(required_name, required_version, installed_item):
    name_similarity = fuzz.token_set_ratio(required_name.lower(), installed_item['Name'].lower())
    
    # Check if either version is 'N/A'
    if required_version == 'N/A' or installed_item['Version'] == 'N/A':
        return name_similarity >= 70
    
    # Special case: Handle Google Chrome
    if 'Google Chrome' in required_name.lower() or 'chrome' in required_name.lower():
        return name_similarity >= 80 and fuzz.ratio('Google Chrome', installed_item['Name']) >= 80
    
     # Special case for "Microsoft Visual C++"
    if 'microsoft visual c++' in required_name.lower():
        # Extract the version from the name using regular expressions
        version_match_required = re.search(r'(\d+(\.\d+)+)', required_name, re.IGNORECASE)
        version_match_installed = re.search(r'(\d+(\.\d+)+)', installed_item['Name'], re.IGNORECASE)

        if version_match_required and version_match_installed:
            required_version = version_match_required.group(0)
            installed_version = version_match_installed.group(0)
            
            # Compare version similarity
            version_similarity = fuzz.ratio(required_version, installed_version)
            
            # Check if both name and version meet the similarity threshold
            return name_similarity >= 70 and version_similarity >= 70
        
    # Special case: Handle WinMerge
    if 'winmerge' in required_name.lower():
        # Extract the version from the name using regular expressions
        version_match = re.search(r'WinMerge (\d+(\.\d+)+)', installed_item['Name'], re.IGNORECASE)
        if version_match:
            installed_version = version_match.group(1)
            # Compare the extracted version with the required version
            if version.parse(installed_version) >= version.parse(required_version):
                return True
            
     # Special case for "NVIDIA Graphics Driver"
    if 'NVIDIA Graphics Driver' in required_name.lower():
        # Extract the version number from the name
        version_match_required = re.search(r'(\d+(\.\d+)+)', required_name, re.IGNORECASE)

        if version_match_required:
            required_version = version_match_required.group(0)

            # Assume the number behind the name is the installed version
            installed_version_match = re.search(r'(\d+(\.\d+)+)', installed_item['Name'])

            if installed_version_match:
                installed_version = installed_version_match.group(0)

                # Compare version similarity
                version_similarity = fuzz.ratio(required_version, installed_version)

                # Check if both name and version meet the similarity threshold
                return name_similarity >= 70 and version_similarity >= 70
        
            
    # For other cases, split the name into words and check if all words appear in the installed software name
    required_name_words = required_name.lower().split()
    installed_name_words = installed_item['Name'].lower().split()
    name_similarity_words = fuzz.token_set_ratio(required_name_words, installed_name_words)

    # Parse the version strings and compare
    version_similarity = fuzz.ratio(required_version, installed_item['Version'])
    if 'microsoft visual c++' in required_name.lower():
        return name_similarity >= 70 and version_similarity >= 70
    else:
        return name_similarity >= 70 and name_similarity_words >= 70

# Function to generate results
import re

def generate_results(software_data, current_pc_data):
    results = {}

    # Create a dictionary to store the highest version number for each software name
    highest_versions = {}

    for software_item in software_data:
        software_name = software_item['Name']
        required_version = software_item['Required Version']

        matched_items = []
        for current_pc_item in current_pc_data:
            if match_item(software_name, required_version, current_pc_item):
                matched_items.append(current_pc_item)

        if matched_items:
            # Sort matched items by version number (in descending order)
            matched_items.sort(key=lambda x: get_version_number(x['Version']), reverse=True)
            
            # Select the item with the highest version number
            matched_item = matched_items[0]
            
            installed_version = matched_item['Version']
            if installed_version >= required_version:
                status = 'Pass'
            else:
                status = 'Failed'
            
            # Update the highest version for this software
            if software_name not in highest_versions:
                highest_versions[software_name] = installed_version
            else:
                # Check if the current version is higher than the stored highest version
                if get_version_number(installed_version) > get_version_number(highest_versions[software_name]):
                    highest_versions[software_name] = installed_version
        else:
            status = 'Missing'
            installed_version = 'N/A'
            
        # Special case: If the software name contains "WinMerge," display it as "WinMerge"
        if 'WinMerge' in software_name:
            software_name = 'WinMerge'

        results[software_name] = {
            'Required Version': required_version,
            'Installed Version': installed_version,
            'Status': status
        }

    return results

def get_version_number(version_str):
    # Extract the version number from a string using regular expressions
    version_match = re.search(r'(\d+(\.\d+)*)', version_str)
    if version_match:
        return version_match.group(1)
    else:
        return '0'  # Return '0' if no version number is found

# Function to retrieve .NET Framework versions and save them to a JSON file
def retrieve_dotnet_versions():
    def get_dotnet_version(registry_path):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                version = winreg.QueryValueEx(key, "Version")[0]
                return version
        except Exception as e:
            print(f"Error reading registry: {e}")
            return "N/A"

    # Get the versions of .NET Framework 3.5 and 4.8
    dotnet_35_version = get_dotnet_version(r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v3.5")
    dotnet_48_version = get_dotnet_version(r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full")

    # Create a dictionary to store the versions
    dotnet_versions = {
        ".NET Framework 3.5": dotnet_35_version,
        ".NET Framework 4.8": dotnet_48_version
    }

    # Save the versions to a JSON file
    with open('.network_frame.json', 'w') as json_file:
        json.dump(dotnet_versions, json_file, indent=4)

    print(".NET Framework 3.5 Version:", dotnet_35_version)
    print(".NET Framework 4.8 Version:", dotnet_48_version)
    
    
# Update Data in C:\\Tools\\GNU before Browse
def update_gnu_data():
    tools_path = "C:\\Tools"
    gnu_path = "C:\\Tools\\GNU"
    
    if not os.path.exists(tools_path) and not os.path.exists(gnu_path):
        sg.popup_error("Error: Both 'Tools' folder and 'GNU' folder are missing.")
        return None
    
    if not os.path.exists(gnu_path):
        sg.popup_error("Error: 'GNU' folder is missing.")
        return None

    
    run_size_check(gnu_path)
    return gnu_path


# Create the layout for Page 1: Software Checker
page1_layout = create_page1_layout()

# Create the layout for Page 2: Size Checker
page2_layout = create_page2_layout()

# Create the PySimpleGUI window with the default tab content
default_tutorial_layout = [
    [sg.Text("Welcome to 'Software & Size Checker.' This is the default page and a simple tutorial for users.\n\n"
             "1. For 'Page 1: Software Checker,' please kindly click on the 'Check' button to run version checking.\n\n"
             "2. For 'Page 2: Size Checker,' please select the 'GNU' folder manually by clicking on the 'Browse' button.\n\n"
             "Thank you and have a nice day! ;)")],
]

layout = [
    [
        sg.TabGroup(
            [
                [
                    sg.Tab("Default: Tutorial", default_tutorial_layout, key="-TAB1-"),
                    sg.Tab("Page 1: Software Checker", page1_layout, key="-TAB2-"),
                    sg.Tab("Page 2: Size Checker", page2_layout, key="-TAB3-"),  # Added the new tab here
                ],
            ],
            key="-TABS-",
            tab_location="top",
        ),
    ],
]

# Create the PySimpleGUI window
window = sg.Window("Software & Size Checker", layout, finalize=True, size=(1000, 600), resizable= True)

original_table_data = []
original_size_table_data = []

update_page1_data = False
update_page2_data = False

    
folder_path = update_gnu_data()
table_data = window["-SIZE_TABLE-"].get()
original_size_table_data = table_data

update_page2_data = True

def parse_version(version):
    # Replace numbers with a numeric value and keep non-numeric parts as they are
    return tuple(int(x) if x.isdigit() else x for x in re.split(r'([0-9]+)', version))

def get_sort_key(item):
    try:
        # Try to convert the item to a numeric type
        return (0, float(item))
    except (ValueError, TypeError):
        # If conversion fails, return a tuple with a high value for data type and the parsed version
        return (1, parse_version(str(item).lower()))
def sort_order_table(table, col_clicked, current_sort_order):
    try:
        # This takes the table and sorts everything given the column number (index)
        # Use a custom key function to handle mixed data types
        table = sorted(table, key=lambda row: get_sort_key(row[col_clicked]), reverse=current_sort_order[col_clicked])
        # Toggle the sort order for the next click
        current_sort_order[col_clicked] = not current_sort_order[col_clicked]
    except Exception as e:
        sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    return table


def sort_table(window, event, row_count, col_count, current_sort_order):
    if isinstance(event, tuple):
        if event[0] == '-TABLE-':
            # event[2][0] is the row
            # event[2][1] is the column
            if event[2][0] == -1 and event[2][1] != -1:
                col_num_clicked = event[2][1]
                table_values = window["-TABLE-"].get()
                
                # Adjust the number of columns based on the provided col_count
                data = [row[:col_count] for row in table_values]
                
                new_table = sort_order_table(data, col_num_clicked, current_sort_order)
                update_table(window, new_table)
                

def sort_size_table(window, event, row_count, col_count, current_sort_order):
    if isinstance(event, tuple):
        if event[0] == '-SIZE_TABLE-':
            if event[2][0] == -1 and event[2][1] != -1:
                col_num_clicked = event[2][1]
                table_values = window["-SIZE_TABLE-"].get()
                
                # Adjust the number of columns based on the provided col_count
                data = [list(map(str, row[:col_count])) for row in table_values]

                new_table = sort_order_table(data, col_num_clicked, current_sort_order)
                update_size_table(window, new_table)
                
# Initialize current sort order with ascending for each column
current_sort_order_table = [False, False, False, False, False]
            

def update_table(window, data):
    window["-TABLE-"].update(values=data)
    
def update_size_table(window, data):
    window["-SIZE_TABLE-"].update(values=data)
    
    
while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED:
        break
    
    # Example usage for a 4-row, 5-column table
    sort_table(window, event, row_count=5, col_count=5, current_sort_order=current_sort_order_table)
    # Example usage for a 4-row, 5-column table
    sort_size_table(window, event, row_count=4, col_count=4, current_sort_order=current_sort_order_table)

    if event == "-CHECK-":
        run_main_21()
        table_data = window["-TABLE-"].get()
        original_table_data = table_data
        update_gui()
        update_page1_data = True
        

    if event == "-CHECK_SIZE-":
        folder_path = sg.popup_get_folder("Select 'GNU' Folder for Size Checking", no_window = True)
        if folder_path:
            window["-FOLDER-"].update(folder_path)
            run_size_check(folder_path)
            table_data = window["-SIZE_TABLE-"].get()
            original_size_table_data = table_data   
            update_page2_data = True
            
        else:
            sg.popup_error("Error: 'GNU' folder selection cancelled or missing.")
            
            
    if event in ("-SEARCH_BUTTON-", "\r", "-SEARCH-"):
        # For Page 1
        search_text_page1 = values["-SEARCH-"].strip().lower()
        table_data = window["-TABLE-"].get()
        perform_search(search_text_page1, table_data)
        
        if not search_text_page1:
            window["-TABLE-"].update(values=original_table_data)
        
    if event in ("-SEARCH_BUTTON_SIZE-", "\r", "-SEARCH_SIZE-"):
        # For Page 2
        search_text_page2 = values["-SEARCH_SIZE-"].strip().lower()
        table_data = window["-SIZE_TABLE-"].get()
        perform_size_search(search_text_page2, table_data)
        
        if not search_text_page2:
            window["-SIZE_TABLE-"].update(values=original_size_table_data)
        

        
     # Update data on Page 1 when the check button is clicked
    if update_page1_data:
        if not values["-SEARCH-"]:
            table_data = window["-TABLE-"].get()
            window["-TABLE-"].update(values=table_data)
            

    # Update data on Page 2 when the browse button is clicked
    if update_page2_data:
         if not values["-SEARCH_SIZE-"]:
            table_data = window["-SIZE_TABLE-"].get()
            window["-SIZE_TABLE-"].update(values=table_data)
        

window.close()

