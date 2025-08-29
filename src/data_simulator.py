import os
import random
import logging
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(log_dir, 'data_simulator.log'), filemode='a')

# Global variables for LLM to avoid reloading for each note
tokenizer = None
model = None
generation_pipeline = None

def load_model_for_generation(model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
    """Loads a text generation model and tokenizer."""
    global tokenizer, model, generation_pipeline
    if generation_pipeline is None:
        logging.info(f"Loading model for generation: {model_name}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16) # Use bfloat16 for efficiency
            generation_pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                torch_dtype=torch.bfloat16,
                device="cpu" # Force CPU for local generation
            )
            logging.info("Model for generation loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model {model_name} for generation: {e}")
            tokenizer = None
            model = None
            generation_pipeline = None

def generate_note_with_llm(patient_id, note_id, prompt_template, patient_name, patient_dob, physician_name):
    """Generates a single clinical note using the loaded LLM."""
    if generation_pipeline is None:
        logging.error("LLM not loaded. Cannot generate notes. Returning placeholder content.")
        return f"Placeholder clinical note for {patient_id}, {note_id}. LLM generation failed."

    full_prompt = prompt_template.format(
        patient_id=patient_id,
        note_id=note_id,
        patient_name=patient_name,
        patient_dob=patient_dob,
        physician_name=physician_name
    )
    
    try:
        # Adjust generation parameters for more concise and relevant notes
        generated_text = generation_pipeline(
            full_prompt,
            max_new_tokens=250, # Limit length to reduce repetition
            num_return_sequences=1,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7, # Revert to original temperature
            pad_token_id=tokenizer.eos_token_id # Important for generation
        )[0]['generated_text']

        # Extract only the generated part, removing the prompt
        note_content = generated_text[len(full_prompt):].strip()
        logging.info(f"Generated note for {patient_id}, {note_id} (first 100 chars): {note_content[:100]}...")
        return note_content
    except Exception as e:
        logging.error(f"Error generating note for {patient_id}, {note_id} with LLM: {e}")
        return f"Error generating clinical note for {patient_id}, {note_id}. Details: {e}"

def create_simulated_data(num_patients=3, data_dir="data"):
    """Creates simulated patient clinical notes in the specified data directory using an LLM."""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logging.info(f"Created data directory: {data_dir}")

    # Load the LLM once
    load_model_for_generation()
    if generation_pipeline is None:
        logging.error("Skipping LLM-based data generation due to model loading failure.")
        return

    # Define an improved and more structured prompt for clinical notes
    prompt_template = """
    You are a medical professional writing a concise clinical note. Ensure there is some variation in content but also some common medical phrases and lab results across notes for the same patient to simulate real-world scenarios.
    Generate a clinical note for Patient {patient_name} (DOB: {patient_dob}) with lung nodule, seen by Dr. {physician_name}.
    The note should include:
    - Patient name: {patient_name}
    - Date of Birth: {patient_dob}
    - Visited Physician: Dr. {physician_name}
    - Date:
    - Chief Complaint:
    - History of Present Illness (HPI):
    - Physical Examination Findings:
    - Lab Results: (e.g., Blood Count: 500, Hemoglobin: 12.5, Glucose: 100)
    - Assessment:
    - Plan:
    - Next visit:

    Clinical Note:
    """

    logging.info(f"Creating {num_patients} patients with random notes (2-5 each) in '{data_dir}' using TinyLlama...")
    
    patient_details = {
        "patient_001": {"name": "John Doe", "dob": "1985-03-15", "physician": "Smith"},
        "patient_002": {"name": "James Luis", "dob": "1978-11-22", "physician": "Jones"},
        "patient_003": {"name": "Ben Don", "dob": "1992-07-01", "physician": "Williams"},
    }

    for i in range(1, num_patients + 1):
        patient_id = f"patient_{i:03d}"
        
        if patient_id not in patient_details:
            logging.warning(f"No details found for {patient_id}. Skipping.")
            continue

        patient_name = patient_details[patient_id]["name"]
        patient_dob = patient_details[patient_id]["dob"]
        physician_name = patient_details[patient_id]["physician"]

        patient_dir = os.path.join(data_dir, patient_id)
        if not os.path.exists(patient_dir):
            os.makedirs(patient_dir)
            logging.info(f"  Created patient directory: {patient_dir}")

        num_notes_for_patient = random.randint(2, 5) # Random number of notes per patient
        logging.info(f"  Generating {num_notes_for_patient} notes for {patient_id} ({patient_name})...")

        for j in range(1, num_notes_for_patient + 1):
            note_id = f"note_{j:02d}.txt"
            note_path = os.path.join(patient_dir, note_id)
            
            # Generate content using LLM
            content = generate_note_with_llm(
                patient_id,
                note_id,
                prompt_template,
                patient_name=patient_name,
                patient_dob=patient_dob,
                physician_name=physician_name
            )
            
            try:
                with open(note_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logging.info(f"  Created {note_path}")
            except Exception as e:
                logging.error(f"Error writing note to {note_path}: {e}")

    logging.info("Simulated data creation complete.")

if __name__ == "__main__":
    create_simulated_data()