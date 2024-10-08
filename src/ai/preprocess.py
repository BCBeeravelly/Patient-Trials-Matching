import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Namespace for the XML
ns = {'hl7': 'urn:hl7-org:v3'}

# Sections of interest in the XML data
sections = ['Allergies and Adverse Reactions', 'Medications', 'Diagnostic Results', 'Problems', 'Surgeries', 'Vital Signs', 'Immunizations']

def calculate_age(birth_time_str):
    """Calculate age based on birth time string.

    Args:
        birth_time_str (str): The birth time in the format 'YYYYMMDDHHMMSS'.

    Returns:
        int: The calculated age.
    """
    birth_time = datetime.strptime(birth_time_str, '%Y%m%d%H%M%S')
    today = datetime.today()
    return today.year - birth_time.year - ((today.month, today.day) < (birth_time.month, birth_time.day))

def calculate_duration(start_date_str, stop_date_str):
    """Calculate the number of days between start and stop dates (inclusive).

    Args:
        start_date_str (str): The start date in ISO format.
        stop_date_str (str): The stop date in ISO format.

    Returns:
        str: Duration in days as a string, or None if dates are invalid.
    """
    if start_date_str and stop_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M:%SZ')
            stop_date = datetime.strptime(stop_date_str, '%Y-%m-%dT%H:%M:%SZ')
            duration = (stop_date - start_date).days + 1  # Inclusive of both start and stop dates
            return f"{duration} days"  # Return the duration as a string
        except ValueError:
            return "Invalid date format"
    return None


def calculate_last_usage(stop_date_str):
    """Calculate the number of days since the last usage or indicate currently used.

    Args:
        stop_date_str (str): The stop date in ISO format.

    Returns:
        str: Description of last usage or indication of current use.
    """
    if stop_date_str:
        try:
            stop_date = datetime.strptime(stop_date_str, '%Y-%m-%dT%H:%M:%SZ')
            today = datetime.today()
            days_since_last_use = (today - stop_date).days
            return f"{days_since_last_use} days ago"
        except ValueError:
            return "Invalid date"
    return "Currently used"


def extract_patient_details(root):
    """Extract basic patient details from the XML.

    Args:
        root (ElementTree): The root of the XML tree.

    Returns:
        dict: A dictionary containing patient details.
    """
    patient_data = {}
    
    record_target = root.find('hl7:recordTarget/hl7:patientRole', ns)
    if record_target is not None:
        # Patient ID
        patient_id = record_target.find('hl7:id', ns)
        if patient_id is not None:
            patient_data['Patient ID'] = patient_id.get('extension')

        # Given Name
        given_name = record_target.find('.//hl7:name/hl7:given', ns).text if record_target.find('.//hl7:name/hl7:given', ns) is not None else None
        patient_data['Given Name'] = given_name

        # Gender
        gender_code = record_target.find('hl7:patient/hl7:administrativeGenderCode', ns)
        if gender_code is not None:
            patient_data['Gender'] = gender_code.get('code')

        # Birth Time and Age Calculation
        birth_time = record_target.find('hl7:patient/hl7:birthTime', ns)
        if birth_time is not None:
            birth_time_value = birth_time.get('value')
            patient_data['Birth Time'] = birth_time_value
            patient_data['Age'] = calculate_age(birth_time_value)
            
        # Race
        race_code = record_target.find('hl7:patient/hl7:raceCode', ns)
        if race_code is not None:
            patient_data['Race'] = race_code.get('displayName')
            
        # Ethnic Group
        ethnic_group = record_target.find('hl7:patient/hl7:ethnicGroupCode', ns)
        if ethnic_group is not None:
            patient_data['Ethnic Group'] = ethnic_group.get('displayName')
            
        # Extract languageCode code
        language_code = record_target.find('hl7:patient/hl7:languageCommunication/hl7:languageCode', ns)
        if language_code is not None:
            patient_data['Language'] = language_code.get('code')

    return patient_data

def extract_section_data(section_title, section, patient_data):
    """Extracts information from a given section and appends it to the patient_data dictionary.

    Args:
        section_title (str): The title of the section being extracted.
        section (ElementTree): The XML section element to extract data from.
        patient_data (dict): The patient data dictionary to update with the extracted information.
    """
    print(f"Extracting Section: {section_title}")

    # Use section_title as the data_key for patient_data
    data_key = section_title

    # Initialize the list for the specified data_key if it doesn't exist
    if data_key not in patient_data:
        patient_data[data_key] = []

    # Extract the rows from the section (assuming table structure)
    rows = section.findall('.//hl7:tbody/hl7:tr', ns)

    for row in rows:
        # Handle the "Medications" section specifically
        if section_title == 'Medications':
            start_date = row.find('hl7:td[1]', ns).text if row.find('hl7:td[1]', ns) is not None else None
            stop_date = row.find('hl7:td[2]', ns).text if row.find('hl7:td[2]', ns) is not None else None
            description = row.find('hl7:td[3]', ns).text if row.find('hl7:td[3]', ns) is not None else None

            info = {
                'Start': start_date,
                'Stop': stop_date,
                'Description': description,
                'Duration of Usage': calculate_duration(start_date, stop_date),
                'Last Usage': calculate_last_usage(stop_date)
            }
            patient_data[data_key].append(info)

        # Handle the "Vital Signs" section specifically
        elif section_title == 'Vital Signs':
            info = {
                'Start': row.find('hl7:td[1]', ns).text if row.find('hl7:td[1]', ns) is not None else None,
                'Stop': row.find('hl7:td[2]', ns).text if row.find('hl7:td[2]', ns) is not None else None,
                'Description': row.find('hl7:td[3]', ns).text if row.find('hl7:td[3]', ns) is not None else None,
                'Value': row.find('hl7:td[5]', ns).text if row.find('hl7:td[5]', ns) is not None else None
            }
            patient_data[data_key].append(info)
        
        # Handle other sections
        else:
            # For other sections, only extract Start, Stop, and Description
            start_date = row.find('hl7:td[1]', ns).text if row.find('hl7:td[1]', ns) is not None else None
            stop_date = row.find('hl7:td[2]', ns).text if row.find('hl7:td[2]', ns) is not None else None
            description = row.find('hl7:td[3]', ns).text if row.find('hl7:td[3]', ns) is not None else None
            info = {
                'Start': start_date,
                'Stop': stop_date,
                'Description': description,
                'Duration': calculate_duration(start_date, stop_date),
                'Last': calculate_last_usage(stop_date)
            }
            patient_data[data_key].append(info)

def extract_all_sections(root, patient_data):
    """Extract all relevant sections (Allergies, Medications, etc.) from the XML.

    Args:
        root (ElementTree): The root of the XML tree.
        patient_data (dict): The patient data dictionary to update with extracted sections.
    """
    structured_body = root.find('.//hl7:structuredBody', ns)

    if structured_body is not None:
        for component in structured_body.findall('hl7:component', ns):
            section = component.find('hl7:section', ns)
            if section is not None:
                title = section.find('hl7:title', ns)
                
                if title is not None:
                    section_title = title.text.strip()  # Get the section title and strip whitespace

                    # If the section title matches one of the sections we're interested in
                    for section_name in sections:
                        if section_name in section_title:
                            # Extract the section data
                            extract_section_data(section_title, section, patient_data)

def process_xml_files(xml_directory, output_directory):
    """Process multiple XML files in the specified directory.

    Args:
        xml_directory (str): The directory containing XML files to process.
        output_directory (str): The directory where the processed JSON files will be saved.

    This function reads all XML files from the specified xml_directory, extracts patient details and relevant data sections,
    and saves the results as JSON files in the specified output_directory. Each JSON file is named based on the patient's ID
    (extension) extracted from the XML data.

    Returns:
        None: This function does not return any value. It writes output directly to the file system.
    
    Raises:
        FileNotFoundError: If the xml_directory does not exist or cannot be accessed.
        ET.ParseError: If any XML file is not well-formed or cannot be parsed.
    """
    for file_name in os.listdir(xml_directory):
        if file_name.endswith('.xml'):
            xml_file_path = os.path.join(xml_directory, file_name)
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # Initialize patient_data dictionary for each XML file
            patient_data = {}

            # Extract basic patient details
            patient_data.update(extract_patient_details(root))

            # Extract additional sections (Allergies, Medications, etc.)
            extract_all_sections(root, patient_data)

            # Create JSON output file name based on patient ID (extension)
            patient_id = patient_data.get('Patient ID', 'unknown')
            output_file = f"{patient_id}_data.json"
            output_file_path = os.path.join(output_directory, output_file)

            # Write patient data to JSON
            with open(output_file_path, 'w') as json_file:
                json.dump(patient_data, json_file, indent=4)

            print(f"Processed {xml_file_path} and saved to {output_file_path}")

# This block runs only if this script is executed directly
if __name__ == "__main__":
    # Define the directories
    xml_directory = '/Users/bharathbeeravelly/Desktop/patient-trials-matching/data/raw/patients_ehr'
    output_directory = '/Users/bharathbeeravelly/Desktop/patient-trials-matching/data/processed/patients_json'

    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Process the XML files
    process_xml_files(xml_directory, output_directory)

