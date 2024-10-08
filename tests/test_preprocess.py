import sys
import os
import unittest
import xml.etree.ElementTree as ET
from src.ai.preprocess import extract_section_data

# Add the parent directory to the system path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestExtractSectionData(unittest.TestCase):
    """
    Unit tests for the extract_section_data function in the preprocessing module.

    This class contains test cases to validate the extraction of medication 
    information from XML data.
    """

    def setUp(self):
        """
        Set up test environment by creating sample XML data and initializing 
        patient data dictionary before each test.
        """
        # Sample XML data for testing
        self.xml_data = '''<root xmlns:hl7="urn:hl7-org:v3">
            <hl7:component>
                <hl7:section>
                    <hl7:title>Medications</hl7:title>
                    <hl7:tbody>
                        <hl7:tr>
                            <hl7:td>2023-01-01T00:00:00Z</hl7:td>
                            <hl7:td>2023-01-10T00:00:00Z</hl7:td>
                            <hl7:td>Aspirin</hl7:td>
                        </hl7:tr>
                        <hl7:tr>
                            <hl7:td>2023-02-01T00:00:00Z</hl7:td>
                            <hl7:td>2023-02-05T00:00:00Z</hl7:td>
                            <hl7:td>Ibuprofen</hl7:td>
                        </hl7:tr>
                    </hl7:tbody>
                </hl7:section>
            </hl7:component>
        </root>'''
        # Parse the XML string into an ElementTree
        self.root = ET.fromstring(self.xml_data)
        # Initialize a dictionary to hold patient data
        self.patient_data = {}

    def test_extract_medications(self):
        """
        Test the extraction of medication data from the XML structure.

        This test checks whether the extract_section_data function correctly 
        populates the patient_data dictionary with medication information.
        """
        # Call the function to extract medication data
        extract_section_data("Medications", self.root.find('.//hl7:section', {'hl7': 'urn:hl7-org:v3'}), self.patient_data)

        # Define the expected data after extraction
        expected_data = [
            {
                'Start': '2023-01-01T00:00:00Z',
                'Stop': '2023-01-10T00:00:00Z',
                'Description': 'Aspirin',
                'Duration of Usage': '10 days',  # Assumed that calculate_duration works correctly
                'Last Usage': '636 days ago'  # Replace with expected value based on your logic
            },
            {
                'Start': '2023-02-01T00:00:00Z',
                'Stop': '2023-02-05T00:00:00Z',
                'Description': 'Ibuprofen',
                'Duration of Usage': '5 days',  # Assumed that calculate_duration works correctly
                'Last Usage': '610 days ago'  # Replace with expected value based on your logic
            }
        ]

        # Validate the data extracted
        self.assertIn('Medications', self.patient_data)  # Check if 'Medications' key exists
        self.assertEqual(len(self.patient_data['Medications']), 2)  # Validate number of entries
        self.assertEqual(self.patient_data['Medications'], expected_data)  # Check if extracted data matches expected

# Entry point for running the unit tests
if __name__ == '__main__':
    unittest.main()
