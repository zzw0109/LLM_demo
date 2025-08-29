import os
import logging

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(log_dir, 'data_loader.log'), filemode='a')

def load_patient_notes(patient_id, data_dir="data"):
    """
    Loads all clinical notes for a given patient from the specified data directory.

    Args:
        patient_id (str): The ID of the patient (e.g., "patient_001").
        data_dir (str): The base directory where patient data is stored.

    Returns:
        list: A list of strings, where each string is the content of a clinical note.
    """
    patient_notes = []
    patient_path = os.path.join(data_dir, patient_id)

    if not os.path.isdir(patient_path):
        logging.error(f"Patient directory not found at {patient_path}")
        return []

    for filename in os.listdir(patient_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(patient_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    patient_notes.append(f.read())
            except Exception as e:
                logging.error(f"Error reading file {file_path}: {e}")
    return patient_notes

if __name__ == "__main__":
    patient_id = "patient_001"
    notes = load_patient_notes(patient_id)
    if notes:
        logging.info(f"Loaded {len(notes)} notes for {patient_id}.")
        for i, note in enumerate(notes):
            logging.info(f"\n--- Note {i+1} ---")
            logging.info(note[:200] + "...") # Print first 200 characters
    else:
        logging.info(f"No notes loaded for {patient_id}.")