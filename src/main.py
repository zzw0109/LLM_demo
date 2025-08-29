import os
import logging
from data_loader import load_patient_notes
from preprocessing import preprocess_patient_notes
from llm_classifier import ClinicalNoteClassifier
from results_saver import save_results, save_shortened_note # Import new function

# Configure logging for the main script
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(log_dir, 'main.log'), filemode='a')

def run_classification_workflow(data_dir="data", results_filename="follow_up_results.txt", results_dir="results"):
    """
    Orchestrates the entire workflow for patient clinical note classification.
    """
    logging.info("--- Starting Patient Follow-up Classification Workflow ---")

    # 1. Initialize LLM Classifier
    classifier = ClinicalNoteClassifier()
    if classifier.classifier_pipeline is None: # Check if LLM loading failed
        logging.error("Failed to initialize LLM classifier. Aborting workflow.")
        return

    # 2. Get list of all patient IDs
    try:
        patient_ids = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        if not patient_ids:
            logging.warning(f"No patient directories found in {data_dir}. Please run data_simulator.py first.")
            return
    except FileNotFoundError:
        logging.error(f"Data directory '{data_dir}' not found. Please ensure it exists and contains patient data.")
        return
    except Exception as e:
        logging.error(f"Error listing patient directories in {data_dir}: {e}")
        return

    classification_results = {}

    for patient_id in patient_ids:
        logging.info(f"\nProcessing patient: {patient_id}")
        try:
            # 3. Load patient notes
            notes = load_patient_notes(patient_id, data_dir)
            if not notes:
                logging.info(f"  No notes found for {patient_id}. Skipping.")
                continue

            # 4. Preprocess notes (deduplicate)
            shortened_doc = preprocess_patient_notes(notes)
            logging.info(f"  Deduplicated and shortened document (first 200 chars): {shortened_doc[:200]}...")

            # Save the shortened note
            save_shortened_note(patient_id, shortened_doc) # Call the new function

            # 5. Classify the preprocessed document
            classification = classifier.classify_note(shortened_doc)
            classification_results[patient_id] = classification
            logging.info(f"  Classification: {classification}")
        except Exception as e:
            logging.error(f"Error processing patient {patient_id}: {e}")
            classification_results[patient_id] = f"Error: {e}"

    # 6. Save results
    save_results(classification_results, results_filename, results_dir)

    logging.info("\n--- Workflow Complete ---")
    logging.info(f"To view results in the Streamlit app, run: streamlit run src/app.py")

if __name__ == "__main__":
    run_classification_workflow()