import os
import logging

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(log_dir, 'results_saver.log'), filemode='a')

def save_results(results, output_filename="follow_up_results.txt", results_dir="results"):
    """
    Saves the classification results to a plain text file.

    Args:
        results (dict): A dictionary where keys are patient IDs and values are their classification results.
                        Example: {"patient_001": "Needs Follow-up", "patient_002": "No Follow-up"}
        output_filename (str): The name of the output file.
        results_dir (str): The directory where the results file will be saved.
    """
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        logging.info(f"Created results directory: {results_dir}")

    output_path = os.path.join(results_dir, output_filename)

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("--- Patient Follow-up Classification Results ---\n\n")
            for patient_id, classification in results.items():
                f.write(f"Patient ID: {patient_id}\n")
                f.write(f"Classification: {classification}\n")
                f.write("-" * 30 + "\n")
        logging.info(f"Classification results saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving results to {output_path}: {e}")

def save_shortened_note(patient_id, shortened_content, shortened_notes_dir="results/shortened_notes"):
    """
    Saves the shortened clinical note content for a specific patient to a file.

    Args:
        patient_id (str): The ID of the patient.
        shortened_content (str): The deduplicated and keyword-extracted content.
        shortened_notes_dir (str): The directory where shortened notes will be saved.
    """
    if not os.path.exists(shortened_notes_dir):
        os.makedirs(shortened_notes_dir)
        logging.info(f"Created shortened notes directory: {shortened_notes_dir}")

    output_path = os.path.join(shortened_notes_dir, f"{patient_id}_shortened.txt")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(shortened_content)
        logging.info(f"Shortened note for {patient_id} saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving shortened note for {patient_id} to {output_path}: {e}")

if __name__ == "__main__":
    # Example usage for classification results
    sample_results = {
        "patient_001": "Needs Follow-up",
        "patient_002": "No Follow-up",
        "patient_003": "Needs Follow-up"
    }
    save_results(sample_results)

    sample_results_2 = {
        "patient_A": "No Follow-up",
        "patient_B": "Needs Follow-up"
    }
    save_results(sample_results_2, output_filename="another_results.txt")

    # Example usage for shortened notes
    sample_shortened_content = """
    Patient presented with fever and headache.
    Diagnosis: Viral infection.
    Medication: Ibuprofen.
    Keywords: fever, headache, ibuprofen
    """
    save_shortened_note("patient_test_001", sample_shortened_content)