import os
import json
import re
import pandas as pd

# Directories
base_dir = "/Users/emilyheffernan/Documents/Projects/EyeTrackingImages/images"
behavioural_data_dir = "/Users/emilyheffernan/Documents/Projects/EyeTrackingImages/behavioural_data"

# Pattern to match image files
pattern = re.compile(r"S(\d+)_trial(\d+)_plot\.png")

metadata = {"participants": []}
participant_map = {}

# Walk through the directory structure
for root, dirs, files in os.walk(base_dir):
    for file in files:
        match = pattern.match(file)
        if match:
            participant_num = int(match.group(1))
            trial_num = int(match.group(2))
            
            participant_id = f"S{participant_num:03d}"
            
            # Get or create participant entry
            if participant_id not in participant_map:
                participant_map[participant_id] = {
                    "id": participant_id,
                    "trials": []
                }
                metadata["participants"].append(participant_map[participant_id])
            
            # Find corresponding Excel file
            excel_files = [f for f in os.listdir(behavioural_data_dir) if f.startswith(participant_id) and f.endswith(".xlsx")]
            
            if excel_files:
                excel_path = os.path.join(behavioural_data_dir, excel_files[0])  # Take the first matching file
                df = pd.read_excel(excel_path)
                trial_data = df[df["Trial"] == trial_num]
                
                if not trial_data.empty:
                    Type = trial_data["TrialType"].values[0]
                    Corr = int(trial_data["Corr"].values[0]) if pd.notna(trial_data["Corr"].values[0]) else "Unknown"
                else:
                    Type = "Unknown"
                    Corr = "Unknown"
            else:
                Type = "MissingFile"
                Corr = "MissingFile"
            
            # Add trial to participant
            participant_map[participant_id]["trials"].append({
                "trialNumber": trial_num,
                "filename": file,
                "Type": Type,
                "Corr": Corr
            })

# Sort participants by ID
metadata["participants"].sort(key=lambda p: p["id"])

# Sort trials by trial number for each participant
for participant in metadata["participants"]:
    participant["trials"].sort(key=lambda t: t["trialNumber"])

# Write metadata to file
with open("metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print(f"Generated metadata for {len(metadata['participants'])} participants")
