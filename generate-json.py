import json
import os

# Define your software data as a list of dictionaries
software_list = [
    {
        "name": "NVIDIA Graphics Driver",
        "path": "",
        "Required Version": "516.94"
    },
    {
        "name": "Intel INF Alder Lake",
        "path": "",
        "Required Version": "10.1.18836.8283"
    },
    {
        "name": "Intel Management Engine Interface",
        "path": "",
        "Required Version": "2137.15.0.2461"
    },
    {
        "name": "Intel Utility",
        "path": "",
        "Required Version": "18.36.1.1016"
    },
    {
        "name": "Microsoft .Net Framework 3.5 Redistributable for Windows",
        "path": "",
        "Required Version": "3.5.30729.4926"
    },
    {
        "name": "Microsoft .Net Framework 4.8 Redistributable for Windows",
        "path": "",
        "Required Version": "4.8.04084"
    },
    {
        "name": "Asmedia USB 3.1",
        "path": "",
        "Required Version": "10.0.19041.3031"
    },
    {
        "name": "Marvell LAN",
        "path": "",
        "Required Version": "3.1.3.0"
    },
    {
        "name": "Intel Graphic",
        "path": "",
        "Required Version": "31.0.101.2121"
    },
    {
        "name": "Motherboard driver installer (ISO format)",
        "path": "",
        "Required Version": "V1.00"
    },
    {
        "name": "Euresys Coaxlink",
        "path": "",
        "Required Version": "13.0.1.35"
    },
    {
        "name": "Euresys Memento",
        "path": "",
        "Required Version": "12.7.1.102"
    },
    {
        "name": "Basler Pylon Camera Software Suite",
        "path": "",
        "Required Version": "5.0.11.10913"
    },
    {
        "name": "Euresys Multicam",
        "path": "",
        "Required Version": "6.15.1.3573"
    },
    {
        "name": "VTHAL",
        "path": "",
        "Required Version": "5.4.0.0"
    },
    {
        "name": "PL2303 USB-to-Serial",
        "path": "",
        "Required Version": "1.20.0.0"
    },
    {
        "name": "Keyence AutoID Network Navigator",
        "path": "",
        "Required Version": "8.3.1"
    },
    {
        "name": "Sentinel System Driver Installer 7.6",
        "path": "",
        "Required Version": "7.6.0"
    },
    {
        "name": "Sentinel Runtime",
        "path": "",
        "Required Version": "7.90.24540.60000"
    },
    {
        "name": "Microsoft Visual C++ 2008(x86)",
        "path": "",
        "Required Version": "9.0.30729.6161"
    },
    {
        "name": "Microsoft Visual C++ 2008(x64)",
        "path": "",
        "Required Version": "9.0.30729.6161"
    },
    {
        "name": "Microsoft Visual C++ 2010(x86)",
        "path": "",
        "Required Version": "10.0.40219"
    },
    {
        "name": "Microsoft Visual C++ 2010(x64)",
        "path": "",
        "Required Version": "10.0.40219"
    },
    {
        "name": "Microsoft Visual C++ 2013(x86)",
        "path": "",
        "Required Version": "12.0.30501.0"
    },
    {
        "name": "Microsoft Visual C++ 2013(x64)",
        "path": "",
        "Required Version": "12.0.30501.0"
    },
    {
        "name": "Microsoft Visual C++ 2015-2022(x86)",
        "path": "",
        "Required Version": "14.34.31938.0"
    },
    {
        "name": "Microsoft Visual C++ 2015-2022(x64)",
        "path": "",
        "Required Version": "14.34.31938.0"
    },
    {
        "name": "Arduino (Free License, read before setup)",
        "path": "",
        "Required Version": "1.8.8"
    },
    {
        "name": "Teknic Meridian-APS 7.3.121",
        "path": "",
        "Required Version": "7.3.121"
    },
    {
        "name": "Teknic ClearPath USB Drivers",
        "path": "",
        "Required Version": "2.2.5.2"
    },
    {
        "name": "ClearView (Z Height)",
        "path": "",
        "Required Version": "1.7.123"
    },
    {
        "name": "ServoStudio (Manufacturer: Servotronix)",
        "path": "",
        "Required Version": "1.5"
    },
    {
        "name": "Delta driver ASDA_Soft_V6.3.2.18-SP-KA_Installer",
        "path": "",
        "Required Version": "6.3.2.18"
    },
    {
        "name": "MiniGui (Sidecam) Gen 4",
        "path": "",
        "Required Version": "MiniGui 4.0_R2"
    },
    {
        "name": "MiniGui (AOI)",
        "path": "",
        "Required Version": "2.2.0.2"
    },
    {
        "name": "MiniGui (SPI)",
        "path": "",
        "Required Version": "2.2.0.2G_R4.7_API"
    },
    {
        "name": "Vitrox License Server",
        "path": "",
        "Required Version": "3.5.0.0"
    },
    {
        "name": "VOneAgent",
        "path": "",
        "Required Version": "1.1.0.0"
    },
    {
        "name": "7-zip",
        "path": "",
        "Required Version": "23.01"
    },
    {
        "name": "Adobe Acrobat",
        "path": "",
        "Required Version": "23.001.20064"
    },
    {
        "name": "Google Chrome",
        "path": "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "Required Version": "114.0.5735.134"
    },
    {
        "name": "Paint.Net",
        "path": "",
        "Required Version": "5.0.3"
    },
    {
        "name": "Winmerge",
        "path": "",
        "Required Version": "2.16.24.0"
    },
    {
        "name": "TeliCamSDK",
        "path": "",
        "Required Version": "4.0.2.1"
    },
    {
        "name": "TeliU3vDrvInst64",
        "path": "",
        "Required Version": "3.2.11.1"
    }
    # Add more software entries as needed
]

# Get the directory of the script
script_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the relative path for the JSON file
json_filename = "software.json"
json_filepath = os.path.join(script_directory, json_filename)

# Write the software list directly to the JSON file, overwriting the previous content
with open(json_filepath, "w") as json_file:
    json.dump({"software_list": software_list}, json_file, indent=4)

print(f"Software data has been saved to {json_filepath}")

