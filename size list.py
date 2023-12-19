import os
from pathlib import Path

desktop_path = os.path.join(Path.home(), "Desktop")  # Get the desktop folder path
file_name = "applications.txt"

folder_path = r"C:\GNU"  # Replace with the path to your GNU folder

# Get a list of all files in the GNU folder
applications = []

for root, dirs, files in os.walk(folder_path):
    for file in files:
        applications.append(file)

# Create the full path for the output file on the desktop
output_file_path = os.path.join(desktop_path, file_name)

# Write the list of applications to the text file
with open(output_file_path, "w") as txt_file:
    for app in applications:
        txt_file.write(app + "\n")

print(f"List of applications has been saved to {output_file_path}")
