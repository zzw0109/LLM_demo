from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch
import logging
import re

# Logging is configured in main.py to ensure all logs go to app.log

class ClinicalNoteClassifier:
    """
    A classifier for clinical notes using a pre-trained Hugging Face LLM.
    It classifies whether a patient needs follow-up or not.
    """
    def __init__(self, model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initializes the classifier by loading a pre-trained TinyLlama model and tokenizer.
        """
        logging.info(f"Loading TinyLlama model for classification: {model_name}...")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16)
            self.classifier_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                torch_dtype=torch.bfloat16,
                device="cpu" # Force CPU for local generation
            )
            logging.info("TinyLlama model for classification loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading TinyLlama model {model_name} for classification: {e}")
            self.tokenizer = None
            self.model = None
            self.classifier_pipeline = None

    def classify_note(self, text):
        """
        Classifies a single clinical note to determine if a patient needs follow-up using TinyLlama.

        Args:
            text (str): The preprocessed clinical note text.

        Returns:
            str: "Needs Follow-up" or "No Follow-up".
        """
        if self.classifier_pipeline is None:
            logging.error("TinyLlama classifier not loaded. Cannot perform classification.")
            return "Error: Classifier not loaded"

        try:
            # Craft a prompt for TinyLlama to perform binary classification with few-shot examples
            classification_prompt = (
                f"You are a clinical expert in lung nodule. Analyze the following clinical notes and determine if the patient needs a follow-up for lung nodule only. "
                f"Respond concisely with either 'Needs Follow-up' or 'No Follow-up'.\n\n"
                
                f"Example 1:\n"
                f"Clinical Note: Patient presented with a 5mm stable lung nodule, no changes from previous scans. No new symptoms.\n"
                f"Classification: No Follow-up\n\n"
                
                f"Example 2:\n"
                f"Clinical Note: New 1.2cm lung nodule identified. Patient reports recent weight loss and persistent cough. Biopsy recommended.\n"
                f"Classification: Needs Follow-up\n\n"
                
                f"Example 3:\n"
                f"Clinical Note: Patient has a history of smoking. A 8mm lung nodule was found, which has slightly increased in size since the last imaging. Further imaging in 3 months is advised.\n"
                f"Classification: Needs Follow-up\n\n"
                
                f"Clinical Note: {text}\n\n"
                f"Classification:"
            )

            # Generate response using TinyLlama
            generated_text = self.classifier_pipeline(
                classification_prompt,
                max_new_tokens=20, # Keep response concise for classification
                num_return_sequences=1,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.1, # Low temperature for more deterministic output
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                add_special_tokens=True
            )[0]['generated_text']

            # Extract the classification from the generated text
            response_text = generated_text[len(classification_prompt):].strip()
            
            # Use regex for more flexible matching of the classification
            if re.search(r'needs\s+follow-up', response_text, re.IGNORECASE):
                return "Needs Follow-up"
            elif re.search(r'no\s+follow-up', response_text, re.IGNORECASE):
                return "No Follow-up"
            else:
                logging.warning(f"TinyLlama returned an ambiguous classification: '{response_text}'")
                return f"Uncertain (TinyLlama response: '{response_text}')"
        except Exception as e:
            logging.error(f"Error during TinyLlama classification: {e}")
            return "Error during classification"

if __name__ == "__main__":
    classifier = ClinicalNoteClassifier()

    # Test cases
    note1 = "Patient presented with severe headache. Follow-up recommended: yes. Diagnosis: migraine."
    note2 = "Patient is recovering well. No acute distress. Follow-up recommended: no."
    note3 = "Patient expressed concerns about medication side effects. Further investigation needed."
    note4 = "Routine check-up. All clear."

    logging.info(f"\nNote 1: '{note1}'")
    logging.info(f"Classification: {classifier.classify_note(note1)}")

    logging.info(f"\nNote 2: '{note2}'")
    logging.info(f"Classification: {classifier.classify_note(note2)}")

    logging.info(f"\nNote 3: '{note3}'")
    logging.info(f"Classification: {classifier.classify_note(note3)}")

    logging.info(f"\nNote 4: '{note4}'")
    logging.info(f"Classification: {classifier.classify_note(note4)}")