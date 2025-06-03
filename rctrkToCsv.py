import json
import csv
import os
from datetime import datetime

def convert_rctrk_to_csv(input_file, output_file):
    with open(input_file, "r", encoding="utf-8", errors="ignore") as file:
        data = json.load(file)
    
    markers = data.get("markers", [])
    
    # Sort markers by date_unix
    markers.sort(key=lambda x: x["date"])
    
    # Define CSV column names
    columns = ["date_unix", "date", "lat", "lon", "countRate", "doseRate", "acc"]
    
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        
        for marker in markers:
            # Keep original Unix timestamp and convert to readable date
            marker["date_unix"] = marker["date"]
            marker["date"] = datetime.utcfromtimestamp(marker["date"]).strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow(marker)

def process_rctrk_files(input_folder, output_folder):
    # Ensure output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Clear output folder
    for file in os.listdir(output_folder):
        file_path = os.path.join(output_folder, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    # Process each .rctrk file in input folder
    for file in os.listdir(input_folder):
        if file.endswith(".rctrk"):
            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, file.replace(".rctrk", ".csv"))
            convert_rctrk_to_csv(input_file, output_file)
            print(f"Converted {file} to CSV.")

# Example usage
input_folder = "gdanskRctkFiles"
output_folder = "GdanskCSV"
process_rctrk_files(input_folder, output_folder)
print(f"All files have been converted and saved in {output_folder}.")
