# NLP Patient Follow-up Classification Project

This project demonstrates a simple Natural Language Processing (NLP) pipeline for classifying patient clinical notes to determine if a patient needs a follow-up appointment. It's designed as a foundational project for an interview, showcasing data simulation, text preprocessing (deduplication and keyword extraction), a local Large Language Model (LLM) for classification, and a Streamlit application for result visualization.

## Project Structure

```
.
├── data/
│   └── patient_001/
│       ├── note_01.txt
│       └── ...
├── results/
│   └── follow_up_results.txt
├── src/
│   ├── app.py
│   ├── data_loader.py
│   ├── data_simulator.py
│   ├── llm_classifier.py
│   ├── main.py
│   └── preprocessing.py
└── requirements.txt
└── README.md
```

- `data/`: Contains simulated patient clinical notes, organized by patient ID.
- `results/`: Stores the classification output (e.g., `follow_up_results.txt`).
- `src/`: Contains all Python source code.
    - `app.py`: Streamlit application to display classification results.
    - `data_loader.py`: Functions to load patient clinical notes.
    - `data_simulator.py`: Script to generate synthetic patient clinical notes for testing.
    - `llm_classifier.py`: Module for loading and performing inference with a local LLM.
    - `main.py`: Orchestrates the entire workflow from data loading to result saving.
    - `preprocessing.py`: Functions for deduplicating clinical notes and extracting keywords.
- `requirements.txt`: Lists all necessary Python dependencies.
- `README.md`: This project documentation.

## Features

- **Data Simulation**: Generates realistic-looking clinical notes using a local, small LLM (TinyLlama) based on prompts, including some duplication to simulate real-world data.
- **Document Shortening**:
    - **Deduplication**: Removes duplicate sentences across multiple clinical notes for a single patient using a regex-based sentence splitter.
    - **Keyword Extraction**: Extracts important keywords from the deduplicated documents to further condense information.
-   **Lab Result Extraction**: Extracts and combines numerical lab results (e.g., "Blood Count", "Hemoglobin") from all clinical notes for a patient into a time-series-like format (e.g., "Blood Count: 300, 400, 700").
-   **LLM-based Classification**: Utilizes a local, open-source LLM (DistilBERT for sentiment analysis, adapted for follow-up classification) to determine if a patient needs follow-up.
- **Result Storage**: Saves classification outcomes to a plain text file for easy review.
- **Streamlit Application**: Provides an interactive web interface to visualize the classification results.

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    # If this were a git repository
    # git clone <repository-url>
    # cd nlp-patient-followup
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    ```

3.  **Activate the virtual environment:**
    -   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    -   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    ```bash
    python3 -m pip install -r requirements.txt
    ```

## How to Run

1.  **Generate Simulated Data:**
    First, create the dummy patient clinical notes.
    ```bash
    python3 src/data_simulator.py
    ```
    This will create a `data/` directory with several patient subdirectories, each containing multiple `.txt` notes.

2.  **Run the Classification Workflow:**
    Execute the main script to process the notes, classify them, and save the results.
    ```bash
    python3 src/main.py
```
    This will output the classification results to `src/results/follow_up_results.txt`. All application logs will be saved to `app.log` in the root directory. It will also download the TinyLlama model the first time it runs.

3.  **Launch the Streamlit Application:**
    To view the results in a web browser, run the Streamlit app:
    ```bash
    python -m streamlit run src/app.py
    ```
    This command will open a new tab in your default web browser displaying the application.

## Customization and Further Improvements

-   **LLM Choice**: The classification LLM is `distilbert-base-uncased-finetuned-sst-2-english` for sentiment analysis, which is then mapped to "Needs Follow-up" or "No Follow-up". The data generation LLM is `TinyLlama/TinyLlama-1.1B-Chat-v1.0`. For more accurate clinical classification or more sophisticated data generation, consider:
    -   Fine-tuning a BERT-like model on a dataset specifically labeled for patient follow-up.
    -   Using a domain-specific LLM (e.g., BioBERT, ClinicalBERT) if available and suitable for local deployment.
    -   Exploring other small, efficient LLMs from Hugging Face for local inference or data generation.
-   **Keyword Extraction**: Enhance keyword extraction using more advanced techniques like TF-IDF, RAKE, or even a small LLM for summarization/keyphrase extraction.
-   **Lab Result Processing**: Improve the regex for lab result extraction to cover more variations or integrate a more sophisticated NLP entity recognition model.
-   **LLM Input Truncation**: The LLM input is now truncated to the model's maximum sequence length to prevent errors with long documents.
-   **Deduplication Logic**: Refine the deduplication logic to handle semantic duplicates (sentences with similar meaning but different wording) rather than just exact line matches.
-   **Evaluation**: Implement metrics to evaluate the LLM's classification performance (e.g., accuracy, precision, recall, F1-score) if a labeled dataset becomes available.
-   **User Interface**: Add more interactive elements to the Streamlit app, such as:
    -   Ability to select different result files.
    -   Filtering results by classification.
    -   Displaying the original and preprocessed notes for a selected patient.
-   **Error Handling**: Implement more granular error handling and user feedback mechanisms.
-   **Configuration**: Externalize configuration parameters (e.g., model name, data paths) into a configuration file.