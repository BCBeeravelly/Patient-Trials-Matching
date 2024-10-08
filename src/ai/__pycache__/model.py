import json
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

def identify_criteria_keywords(trial_criteria):
    """Identify relevant keywords from clinical trial criteria.

    Args:
        trial_criteria (str): The criteria text from a clinical trial.

    Returns:
        str: A response from the language model identifying relevant keywords or attributes 
        from the provided trial criteria.

    This function communicates with a language model to extract significant keywords 
    related to patient eligibility criteria from the input trial criteria.
    """
    print("Identifying criteria keywords...")
    system_message = """
    You are a clinical trial assistant.
    Your task is to read the inclusion, exclusion, and other criteria of a clinical trial, and identify relevant keywords from each criterion.
    
    Common keywords may include: "Gender", "Age", "Race", "Ethnic Group", "Language", "BMI", "BPM", "Height", "Weight", etc.

    For each criterion, respond with the most relevant keyword or attribute it is concerned with.
    """

    llm = ChatOpenAI(temperature=0, model='gpt-4o-mini', openai_api_key=openai_api_key)

    prompt_template = PromptTemplate(
        input_variables=["criteria"],
        template=f"""
        {system_message}

        Trial Criteria: {{criteria}}

        For each criterion, identify the relevant keyword or patient attribute.
        """
    )
    
    prompt = prompt_template.format(criteria=trial_criteria)
    response = llm(prompt)
    
    return response

def extract_relevant_patient_data(patient_ehr):
    """Extract relevant patient data from electronic health records (EHR).

    Args:
        patient_ehr (dict): A dictionary containing patient EHR data.

    Returns:
        dict: A dictionary containing relevant patient attributes such as 
        Gender, Age, Race, and other medical history details.

    This function retrieves specific data points from the patient EHR that 
    are necessary for assessing eligibility for clinical trials.
    """
    print("Extracting relevant patient data...")
    relevant_patient_data = {
        "Gender": patient_ehr.get("Gender"),
        "Age": patient_ehr.get("Age"),
        "Race": patient_ehr.get("Race"),
        "Ethnic Group": patient_ehr.get("Ethnic Group"),
        "Language": patient_ehr.get("Language"),
        "Vital Signs": patient_ehr.get("Vital Signs"),
        "Medications": patient_ehr.get("Medications"),
        "Problems": patient_ehr.get("Problems"),
        "Surgeries": patient_ehr.get("Surgeries"),
        "Immunizations": patient_ehr.get("Immunizations"),
    }
    return relevant_patient_data

def evaluate_criteria_by_keywords(criteria_keywords, patient_ehr):
    """Evaluate patient eligibility based on identified keywords and EHR data.

    Args:
        criteria_keywords (str): Identified keywords from trial criteria.
        patient_ehr (dict): A dictionary containing patient EHR data.

    Returns:
        str: A response from the language model indicating whether the patient meets 
        the inclusion or exclusion criteria based on the identified keywords.

    This function uses a language model to compare patient data against clinical trial 
    criteria keywords and provide an eligibility assessment for each criterion.
    """
    print("Evaluating criteria by keywords...")
    system_message = """
    You are a clinical trial assistant.
    Your task is to compare the patient's information (Gender, Age, Race, Ethnic Group, Language, Vital Signs) 
    with the clinical trial's inclusion and exclusion criteria using the identified keywords.
    
    For each inclusion criterion, respond with one of the following:
    - "Yes" if the patient meets the criterion
    - "No" if there is evidence that the criterion is not met
    - "Yes" if there is no information available to determine eligibility.
    
    For each exclusion criterion, respond with one of the following:
    - "Yes" if the patient does not meet the criterion
    - "No" if there is evidence that the criterion is met
    - "Yes" if there is no information available to determine eligibility.
    """

    llm = ChatOpenAI(temperature=0, model='gpt-4o-mini', openai_api_key=openai_api_key)

    relevant_patient_data = extract_relevant_patient_data(patient_ehr)

    prompt_template = PromptTemplate(
        input_variables=["criteria_keywords", "patient_data"],
        template=f"""
        {system_message}

        Criteria Keywords: {{criteria_keywords}}

        Patient Information: {{patient_data}}

        For each criterion keyword, respond with:
        - "Yes" if the patient meets the criterion
        - "No" if the patient does not meet the criterion and reason
        
        While evaluating one criteria, consider only the respective criteria but not any other criteria.
        
        The format of response should be as below:
        
        Inclusion Criteria:
        - Keyword Placeholder 1: Yes 
        - Keyword Placeholder 2: No 
        .
        .
        .
        
        Exclusion Criteria:
        - Keyword Placeholder 1: No
        - Keyword Placeholder 2: Yes
        .
        .
        .
        
        While giving the response, do not output the whole criteria mentioned in the txt file. Instead, just give the keyword and the response.
      """
    )

    prompt = prompt_template.format(
        criteria_keywords=criteria_keywords,
        patient_data=relevant_patient_data
    )
    
    response = llm(prompt)
    
    return response

def process_patient_eligibility(trial_criteria, patient_ehr):
    """Process the eligibility of a patient for a given clinical trial.

    Args:
        trial_criteria (str): The inclusion and exclusion criteria of the clinical trial.
        patient_ehr (dict): A dictionary containing patient EHR data.

    Returns:
        str: A response indicating the evaluation results of the patient's eligibility 
        against the trial criteria.

    This function orchestrates the process of identifying relevant keywords from trial 
    criteria and evaluating them against the patient's EHR to determine eligibility.
    """
    print("Processing patient eligibility...")
    criteria_keywords = identify_criteria_keywords(trial_criteria)
    
    eligibility_results = evaluate_criteria_by_keywords(criteria_keywords, patient_ehr)
    
    return eligibility_results.content

def parse_eligibility_results(eligibility_results):
    """Parse eligibility results from the language model response.

    Args:
        eligibility_results (str): The raw response from the eligibility evaluation.

    Returns:
        dict: A dictionary containing eligibility criteria as keys and their evaluation 
        results as values.

    This function separates the inclusion and exclusion criteria results from the 
    language model's response into a structured dictionary.
    """
    print("Parsing eligibility results...")
    inclusion_criteria, exclusion_criteria = eligibility_results.split('Exclusion Criteria:')
    
    eligibility_dict = {}
    
    for line in inclusion_criteria.split('\n'):
        if line.strip().startswith('-'):
            key, value = line.strip('- ').split(': ')
            eligibility_dict[key.strip()] = value.strip()
    
    for line in exclusion_criteria.split('\n'):
        if line.strip().startswith('-'):
            key, value = line.strip('- ').split(': ')
            eligibility_dict[key.strip()] = value.strip()
    
    return eligibility_dict

def extract_ids(patient_ehr_path, trial_criteria_path):
    """Extract patient and trial IDs from file paths.

    Args:
        patient_ehr_path (str): The file path of the patient's EHR JSON file.
        trial_criteria_path (str): The file path of the trial criteria text file.

    Returns:
        tuple: A tuple containing the extracted patient ID and trial ID.

    This function retrieves IDs from the filenames of the patient EHR and trial criteria 
    files, which are used for further processing and identification.
    """
    print("Extracting IDs from file paths...")
    patient_id = os.path.basename(patient_ehr_path).split('_')[0]
    
    trial_id = os.path.basename(trial_criteria_path).split('_')[0]
    
    return patient_id, trial_id

def extract_study_title(trial_criteria_path):
    """Extract the study title from trial criteria file.

    Args:
        trial_criteria_path (str): The file path of the trial criteria text file.

    Returns:
        str: The study title if found, else None.

    This function reads the first line of the trial criteria file to extract 
    the study title, which is used in the output JSON.
    """
    print("Extracting study title from trial criteria...")
    with open(trial_criteria_path, 'r') as f:
        first_line = f.readline().strip()
        
        if first_line.startswith("Study Title:"):
            return first_line.replace("Study Title:", "").strip()
            
    return None

def create_eligibility_json(patient_id, trial_id, study_title, eligibility_dict):
    """
    Create a JSON structure for a patient's eligibility in a clinical trial.

    Args:
        patient_id (str): The ID of the patient.
        trial_id (str): The ID of the trial.
        study_title (str): The title of the clinical trial.
        eligibility_dict (dict): A dictionary containing eligibility criteria and their status.

    Returns:
        dict: A JSON-like dictionary representing the trial's eligibility for the patient.
    """
    print(f"Creating JSON structure for patient {patient_id} and trial {trial_id}...")
    
    eligibility_json = {
        "trialId": trial_id,
        "studyTitle": study_title,
        "eligibilityCriteriaMet": [
            criterion for criterion, status in eligibility_dict.items() if status == "Yes"
        ]
    }
    
    return eligibility_json

def determine_overall_eligibility(eligibility_dict):
    """
    Determine the overall eligibility of a patient based on individual criteria evaluations.

    Args:
        eligibility_dict (dict): A dictionary containing eligibility criteria and their status.

    Returns:
        str: "Yes" if the patient meets all criteria, otherwise "No".
    """
    print("Determining overall eligibility...")
    
    return "Yes" if all(value == 'Yes' for value in eligibility_dict.values()) else "No"

def save_eligibility_json(output_filename, new_trial_info):
    """
    Save the eligibility information to a JSON file, appending to existing data if the file exists.

    Args:
        output_filename (str): The path to the output JSON file.
        new_trial_info (dict): The new trial eligibility information to be saved.
    """
    # Check if output file already exists
    if os.path.exists(output_filename):
        # Read existing data
        with open(output_filename, 'r') as f:
            existing_data = json.load(f)
    else:
        # If no existing data, start with an empty structure
        existing_data = {"eligibleTrials": []}

    # Append new trial info to eligibleTrials
    existing_data["eligibleTrials"].append(new_trial_info)

    # Write updated data back to file
    with open(output_filename, 'w') as f:
        json.dump(existing_data, f, indent=2)

def process_patients_and_trials(patient_dir, trial_dir, output_dir):
    """
    Process patient EHR files against clinical trial criteria to determine eligibility.

    Args:
        patient_dir (str): Directory containing patient EHR JSON files.
        trial_dir (str): Directory containing trial criteria text files.
        output_dir (str): Directory where eligibility results will be saved.
    """
    print(f"Processing patients in directory: {patient_dir}")
    
    # Get all patient EHR files
    patient_files = [f for f in os.listdir(patient_dir) if f.endswith('.json')]
    
    # Iterate through each patient file
    for patient_file in patient_files:
        print(f"Processing file: {patient_file}")
        
        patient_path = os.path.join(patient_dir, patient_file)
        
        # Read the patient EHR
        with open(patient_path) as f:
            patient_ehr = json.load(f)
        
        # Extract patient ID from file name
        patient_id = os.path.basename(patient_path).split('_')[0]
        
        # Iterate through each trial criteria file in trial directory
        for trial_file in os.listdir(trial_dir):
            if trial_file.endswith('_criteria.txt'):
                print(f"Processing trial file: {trial_file}")
                
                trial_path = os.path.join(trial_dir, trial_file)
                
                # Read trial criteria
                with open(trial_path) as f:
                    trial_criteria = f.read()
                
                # Extract trial ID and study title
                trial_id = os.path.basename(trial_file).split('_')[0]
                study_title = extract_study_title(trial_path)

                # Process eligibility for this patient and trial
                eligibility_results = process_patient_eligibility(trial_criteria, patient_ehr)
                eligibility_dict = parse_eligibility_results(eligibility_results)

                # Determine overall eligibility
                final_eligibility = determine_overall_eligibility(eligibility_dict)

                # Print final eligibility for this trial
                print(f"Final Eligibility for Trial {trial_id} (Patient {patient_id}): {final_eligibility}")

                if final_eligibility == "Yes":
                    # Create JSON structure only if eligible
                    new_trial_info = create_eligibility_json(patient_id, trial_id, study_title, eligibility_dict)
                    
                    # Save JSON file under output directory (appending eligible trials)
                    output_filename = os.path.join(output_dir, f"{patient_id}_eligibility.json")
                    save_eligibility_json(output_filename, new_trial_info)

# Define directories for patients and trials
patient_directory = '/Users/bharathbeeravelly/Desktop/patient-trials-matching/data/processed/patients_small'
trial_directory = '/Users/bharathbeeravelly/Desktop/patient-trials-matching/data/raw/scraped_small'
output_directory = '/Users/bharathbeeravelly/Desktop/patient-trials-matching/data/outputs_small'

# Run the processing function
process_patients_and_trials(patient_directory, trial_directory, output_directory)