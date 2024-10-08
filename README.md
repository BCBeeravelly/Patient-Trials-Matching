# Patient Trials Matching

This project is designed to match patient data with clinical trials based on eligibility criteria. It leverages web scraping techniques to gather trial information and processes patient electronic health records (EHR) to determine eligibility.
## Table of Contents 
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
## Features 
- Scrapes inclusion and exclusion criteria from clinical trial websites. 
- Processes patient EHRs in JSON format to assess eligibility for trials. 
- Outputs eligibility results in a structured JSON format. 
## Installation 

 1. **Clone the Repository:**
 2. **Set up a virtual Environment**: ```source env/bin/activate```
 3. **Install required packages**: ```pip install -r requirements.txt```
 4. **Set up WebDriver:**
	 * Download and install the appropriate WebDriver for your browser (e.g., ChromeDriver for Google Chrome).
	 * Make sure the WebDriver is in your system's PATH.
## Usage
1. Organize input data:
	* Place patient EHR JSON files in the `data/processed/patients` directory. (For the scope of the project, I have created another directory ```patients_small``` with smaller dataset for demonstrating the results)
	* Place clinical trial criteria text files in the `data/raw/scraped` directory. (For the scope of the project, I have created another directory ```scraped_small``` for demonstrating the results for demonstrating the results)
2. Run the scripts using ```master.py``` and pass the arguments ```--scrape```, ```--preprocess```, ```--tests```.,```---model``` to run scraping, preprocessing, unit tests and AI model scripts.
3. You can find the experimentation of different scraping, preprocessing and modeling strategies in the ```notebooks``` directory.
4. Replace/Update ```spreadsheet_id, token_spreadsheet, openaiapi``` in the ```.env``` file.