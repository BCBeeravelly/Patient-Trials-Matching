import argparse
import subprocess
import os
import sys

def run_scraper():
    print("Running the scraper...")
    subprocess.run([sys.executable, os.path.join('scraping', 'scraper.py')])

def run_preprocess():
    print("Running the preprocessor...")
    subprocess.run([sys.executable, os.path.join('ai', 'preprocess.py')])

def run_model():
    print("Running the model...")
    subprocess.run([sys.executable, os.path.join('ai', 'model.py')])

def run_tests():
    print("Running unit tests...")
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'ai', '-p', '*_test.py'])

def main(scrape, preprocess, model, test):
    if scrape:
        run_scraper()
    if preprocess:
        run_preprocess()
    if model:
        run_model()  # Only run the model if specified
    if test:
        run_tests()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master program to run scraping, preprocessing, and modeling.")
    parser.add_argument('--scrape', action='store_true', help="Run the scraper.")
    parser.add_argument('--preprocess', action='store_true', help="Run the preprocessor.")
    parser.add_argument('--test', action='store_true', help="Run unit tests.")
    
    args = parser.parse_args()
    
    main(args.scrape, args.preprocess, args.test)
