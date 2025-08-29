import os
import re
import logging

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(log_dir, 'preprocessing.log'), filemode='a')

def _split_into_sentences(text):
    """
    Splits a text into sentences using a simple regex-based approach.
    This is a basic implementation and might not handle all edge cases perfectly.
    """
    # Split by periods, question marks, or exclamation marks, followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def deduplicate_notes(notes):
    """
    Identifies and removes duplicate content across multiple clinical notes at the sentence level.

    Args:
        notes (list): A list of strings, where each string is the content of a clinical note.

    Returns:
        str: A single string containing the deduplicated content from all notes.
    """
    unique_sentences_ordered = {} # make sure the split sentences are in order
    for note in notes:
        sentences = _split_into_sentences(note)
        for sentence in sentences:
            stripped_sentence = sentence.strip()
            if stripped_sentence and stripped_sentence not in unique_sentences_ordered:
                unique_sentences_ordered[stripped_sentence] = None 
    
    logging.info(f"Deduplicated {len(notes)} notes into {len(unique_sentences_ordered)} unique sentences.")

    return "\n".join(unique_sentences_ordered.keys())


def generalize_sensitive_info(text):
    """
    Replaces specific sensitive information (Doctor names, Patient names, DOBs) with generic placeholders.
    """
    # Doctor names 
    text = re.sub(r'(Dr\.\s+[A-Z][a-zA-Z\s]+)', r'Dr. [DOCTOR_NAME]', text)
    text = re.sub(r'(Seen by Dr\.\s+[A-Z][a-zA-Z\s]+)', r'Seen by Dr. [DOCTOR_NAME]', text)
    text = re.sub(r'(Visited Physician:\s+[A-Z][a-zA-Z\s]+)', r'Visited Physician: [DOCTOR_NAME]', text)
    
    # Names 
    text = re.sub(r'(Patient\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', r'Patient [PATIENT_NAME]', text)
    text = re.sub(r'(\b[A-Z][a-z]+\s+[A-Z][a-z]+\b)(?=\s+\(DOB:|\s+was seen by|\s+has a history)', r'[PATIENT_NAME]', text) # Catches "John Doe" before DOB or "was seen by"
    

    text = re.sub(r'(DOB:\s+\d{4}-\d{2}-\d{2})', r'DOB: [DATE_OF_BIRTH]', text)
    
    # Dates
    text = re.sub(r'(Date:\s+\d{1,2}/\d{1,2}/\d{4})', r'Date: [DATE]', text)
    text = re.sub(r'(on\s+\d{1,2}/\d{1,2}/\d{4})', r'on [DATE]', text)
    
    return text


def extract_and_combine_lab_results(notes):
    """
    Extracts lab results from a list of clinical notes and combines them into a series
    for each lab test.

    Args:
        notes (list): A list of strings, where each string is the content of a clinical note.

    Returns:
        str: A formatted string of combined lab results (e.g., "Blood Count: 300, 400, 700").
    """
    combined_lab_results = {}
    # capture the lab test name (e.g., "Blood Count", "Hemoglobin") and the numerical value.
    lab_result_pattern = re.compile(r'(?i)(blood count|hemoglobin|glucose|creatinine|cholesterol|sodium|potassium|wbc|rbc|platelets|hba1c|tsh|hematocrit|white blood cell count)\s*:\s*(\d+\.?\d*)')

    for note in notes:
        for match in lab_result_pattern.finditer(note):
            lab_name = match.group(1).strip().title() # Normalize name (e.g., "blood count" -> "Blood Count")
            lab_value = match.group(2).strip()
            
            if lab_name not in combined_lab_results:
                combined_lab_results[lab_name] = []
            combined_lab_results[lab_name].append(lab_value)
    
    formatted_results = []
    for lab_name, values in combined_lab_results.items():
        formatted_results.append(f"{lab_name}: {', '.join(values)}")
    
    if formatted_results:
        logging.info(f"Extracted and combined lab results: {'; '.join(formatted_results)}")
        # Return the formatted string, the dictionary, and the regex pattern used for extraction
        return "Lab Results: " + "; ".join(formatted_results), combined_lab_results, lab_result_pattern
    else:
        logging.info("No lab results found in notes.")
        return "", {}, None


def preprocess_patient_notes(notes):
    """
    Orchestrates the preprocessing pipeline: deduplication and lab result extraction.

    Args:
        notes (list): A list of strings, where each string is the content of a clinical note.

    Returns:
        str: The deduplicated and lab-result-combined content.
    """
    logging.info("Starting preprocessing for patient notes...")
    generalized_notes = [generalize_sensitive_info(note) for note in notes]
    deduplicated_content = deduplicate_notes(generalized_notes)
    
    # Extract and combine lab results, also getting the pattern used for extraction
    combined_lab_results_str, combined_lab_results_dict, lab_result_pattern = extract_and_combine_lab_results(generalized_notes)

    # Remove individual lab result mentions from the deduplicated content
    if lab_result_pattern:
        shortened_document = lab_result_pattern.sub("", deduplicated_content)
        shortened_document = re.sub(r'\n\s*\n', '\n\n', shortened_document).strip()
    else:
        shortened_document = deduplicated_content
    
    # extra cleanup
    shortened_document = re.sub(r'\s*-\s*', ' - ', shortened_document) 
    shortened_document = re.sub(r',,+', ',', shortened_document) 
    shortened_document = re.sub(r'\s{2,}', ' ', shortened_document) 
    shortened_document = re.sub(r'(\s*[,.;])', r'\1', shortened_document) #
    shortened_document = shortened_document.strip() 

    # Add the combined lab results to the end of the document
    if combined_lab_results_str:
        if shortened_document:
            shortened_document += "\n\n" + combined_lab_results_str
        else:
            shortened_document = combined_lab_results_str

    logging.info("Preprocessing complete.")
    return shortened_document

if __name__ == "__main__":
    sample_notes = [
        "Patient presented with symptoms. Vital signs stable. Discussed treatment options. Blood Count: 500.",
        "Vital signs stable. Patient advised to rest and hydrate. Discussed treatment options. Hemoglobin: 12.5.",
        "Patient presented with symptoms. No acute distress noted. Patient advised to rest and hydrate. Blood Count: 600.",
        "Patient presented with symptoms. Vital signs stable. Chief complaint: fever. Glucose: 100."
    ]
    
    shortened_doc = preprocess_patient_notes(sample_notes)
    logging.info("--- Preprocessed Document ---")
    logging.info(shortened_doc)
    
    print("\n" + "="*30 + "\n")

    sample_notes_labs = [
        "Lab Results: Blood Count: 300. Hemoglobin: 14.0.",
        "Blood Count: 400. Glucose: 95.",
        "Hemoglobin: 13.2. Blood Count: 700."
    ]
    combined_labs, _, _ = extract_and_combine_lab_results(sample_notes_labs)
    logging.info("--- Combined Lab Results Example ---")
    logging.info(combined_labs)