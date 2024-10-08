import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to store the scraped data (you can create a scraped folder)
output_dir = os.path.join(current_dir, '..', '..', 'data', 'raw', 'scraped')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def scrape_criteria(driver, study_url, nct_number, nct_name):
    """
    Scrape the inclusion/exclusion and other criteria from a clinical trial study page.
    
    Parameters:
    driver (webdriver): The Selenium WebDriver instance.
    study_url (str): The URL of the clinical trial study.
    nct_number (str): The NCT number of the clinical trial.
    nct_name (str): The title of the clinical trial.
    
    Saves the scraped criteria to a text file named <nct_number>_criteria.txt in the specified output directory.
    """
    # Construct the URL for participation criteria
    criteria_url = study_url + "#participation-criteria"
    driver.get(criteria_url)  # Navigate to the criteria URL
    driver.maximize_window()   # Maximize the browser window

    try:
        # Wait until the inclusion/exclusion criteria element is present and retrieve its text
        inclusion_exclusion_criteria = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="participation-criteria"]/ctg-participation-criteria/div[2]/div/div[2]/div[1]'))
        )
        inclusion_exclusion_text = inclusion_exclusion_criteria.text

        # Wait until the other criteria element is present and retrieve its text
        other_criteria = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="participation-criteria"]/ctg-participation-criteria/div[2]/div/div[2]/div[2]'))
        )
        other_criteria_text = other_criteria.text

        # Formatting text for output
        formatted_text = f"Study Title: {nct_name}\nInclusion/Exclusion Criteria:\n{inclusion_exclusion_text}\n\nOther Criteria:\n{other_criteria_text}"
        
        # Create the output file path
        file_name = f"{nct_number}_criteria.txt"
        output_path = os.path.join(output_dir, file_name)
        
        # Save the formatted text to a text file
        with open(output_path, 'w') as file:
            file.write(formatted_text)

        print(f"Data for {nct_number} successfully written to {file_name}")
    
    except Exception as e:
        # Handle any errors that occur during scraping
        print(f"An error occurred for {nct_number}: {str(e)}")

def main():
    """
    Main function to initialize the WebDriver and read study links from a CSV file,
    then scrape criteria for each study.
    """
    # Initialize the WebDriver (Make sure to specify the correct path to your chromedriver)
    driver = webdriver.Chrome()  # Ensure chromedriver is in PATH or specify path here
    
    # Path to the CSV file containing study links
    csv_path = os.path.join(current_dir, '..', '..', 'data', 'raw', 'study-links.csv')
    
    # Read the study-links.csv file into a DataFrame
    df = pd.read_csv(csv_path)

    # Loop over each study URL in the CSV and scrape the data
    for index, row in df.iterrows():
        study_url = row['Study URL']
        nct_number = row['NCT Number']
        nct_name = row['Study Title']
        
        print(f"Scraping data for NCT Number: {nct_number} from URL: {study_url}")
        
        # Call the scrape_criteria function for each study
        scrape_criteria(driver, study_url, nct_number, nct_name)

if __name__ == "__main__":
    main()  
