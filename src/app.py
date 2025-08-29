import streamlit as st
import os
import logging

# Logging is configured in main.py to ensure all logs go to app.log

def load_results(results_filename="follow_up_results.txt", results_dir="results"):
    """
    Loads classification results from a plain text file.

    Args:
        results_filename (str): The name of the results file.
        results_dir (str): The directory where the results file is located.

    Returns:
        str: The content of the results file, or an error message if not found.
    """
    results_path = os.path.join(results_dir, results_filename)
    if not os.path.exists(results_path):
        logging.warning(f"Results file not found at {results_path}")
        return f"Error: Results file not found at {results_path}"
    
    try:
        with open(results_path, "r", encoding="utf-8") as f:
            logging.info(f"Successfully loaded results from {results_path}")
            return f.read()
    except Exception as e:
        logging.error(f"Error reading results file {results_path}: {e}")
        return f"Error reading results file {results_path}: {e}"

def main():
    st.set_page_config(page_title="Patient Follow-up Classifier", layout="wide")
    st.title("🩺 Patient Follow-up Classification App")

    st.markdown("""
    This application displays the classification results for patient clinical notes,
    indicating whether a patient needs a follow-up appointment or not.
    """)

    st.header("Classification Results")

    results_content = load_results(results_dir="src/results")
    if "Error" in results_content:
        st.error(results_content)
        st.info("Please ensure the classification process has been run and results are saved in the 'results' directory.")
    else:
        st.text(results_content)

    st.markdown("---")
    st.write("Developed for NLP interview project.")

if __name__ == "__main__":
    main()