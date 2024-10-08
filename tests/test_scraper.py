import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add the project root directory to PYTHONPATH for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.scraping.scraper import scrape_criteria  # Import the scrape_criteria function

class TestScrapeCriteria(unittest.TestCase):
    """
    Unit tests for the scrape_criteria function in the scraper module.

    This class contains test cases to validate the functionality of scraping 
    inclusion and exclusion criteria from clinical trial webpages.
    """

    @patch("selenium.webdriver.Chrome")
    @patch("selenium.webdriver.support.ui.WebDriverWait")
    def test_scrape_criteria(self, mock_wait, mock_driver):
        """
        Test the scrape_criteria function using a mock WebDriver.

        This test simulates the behavior of a Selenium WebDriver to ensure that
        the scrape_criteria function correctly interacts with the web elements
        and processes the criteria as expected.
        """
        # Create a mock driver instance to simulate browser actions
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        
        # Simulate the text returned from the inclusion/exclusion and other criteria containers
        mock_inclusion_element = MagicMock()
        mock_inclusion_element.text = "Inclusion Criteria: Age > 18\nExclusion Criteria: None"
        
        mock_other_element = MagicMock()
        mock_other_element.text = "Some other criteria"
        
        # Simulate the elements that would be returned by WebDriverWait
        mock_wait.return_value.until.side_effect = [mock_inclusion_element, mock_other_element]
        
        # Call the scrape_criteria function with a test URL and mocked driver
        scrape_criteria(mock_driver_instance, "https://clinicaltrials.gov/ct2/show/NCT12345678", "NCT12345678", "Test Study")
        
        # Assertions to verify correct function behavior
        mock_driver_instance.get.assert_called_with("https://clinicaltrials.gov/ct2/show/NCT12345678#participation-criteria")
        mock_driver_instance.maximize_window.assert_called_once()  # Check if maximize_window was called
        
        # Construct the expected file path for the output
        expected_file_path = os.path.join("/Users/bharathbeeravelly/Desktop/patient-trials-matching/data/raw/scraped", "NCT12345678_criteria.txt")
        
        # Check if the expected output file exists (skip actual content check for now)
        self.assertTrue(os.path.exists(expected_file_path))

        # Clean up after test by removing the created file
        if os.path.exists(expected_file_path):
            os.remove(expected_file_path)

# Entry point for running the unit tests
if __name__ == "__main__":
    unittest.main()
