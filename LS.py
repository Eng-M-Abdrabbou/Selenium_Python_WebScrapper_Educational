import csv
import time
import random
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- Configuration ---
LINKEDIN_USERNAME = os.environ.get('LINKEDIN_USER') # Use environment variable for username
LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASS') # Use environment variable for password
OUTPUT_CSV_FILE = 'linkedin_data.csv'

# --- Field List (Based on your request) ---
# Note: Many of these are NOT typically available via direct scraping
FIELD_NAMES = [
    "status", "email", "first_name", "last_name", "full_name", "email_status",
    "title", "company_name", "company_url", "company_domain", "company_linkedin_url",
    "linkedin_url", "headline", "country", "state", "city",
    "estimated_num_employees", "phone_number", "sanitized_phone_number",
    "seniority", "industry", "secondary_industries", "industries",
    "functions", "departments", "subdepartments", "keywords"
]

# --- Helper Function ---
def safe_get_text(element, selector, attribute=None):
    """Safely extracts text or attribute from a BeautifulSoup element."""
    try:
        if attribute:
            found = element.select_one(selector)
            return found[attribute].strip() if found and found.has_attr(attribute) else None
        else:
            found = element.select_one(selector)
            return found.get_text(strip=True) if found else None
    except Exception:
        return None

def random_delay(min_seconds=3, max_seconds=8):
    """Waits for a random duration to mimic human behavior."""
    time.sleep(random.uniform(min_seconds, max_seconds))

# --- Main Scraping Logic ---
def scrape_profile(driver, profile_url):
    """Scrapes a single LinkedIn profile."""
    print(f"Scraping profile: {profile_url}")
    driver.get(profile_url)
    random_delay(5, 10) # Wait for page to potentially load

    # --- IMPORTANT: Scroll to load dynamic content ---
    # LinkedIn loads content dynamically as you scroll. You might need multiple scrolls.
    print("Scrolling page...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(3): # Scroll down a few times
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_delay(2, 4)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break # Stop scrolling if height doesn't change
        last_height = new_height

    random_delay(3, 6) # Final wait after scrolling

    # --- Get Page Source & Parse ---
    try:
        # Wait for a key element to ensure page is loaded (adjust selector as needed)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'h1')) # Example: Wait for main name heading
        )
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
    except Exception as e:
        print(f"Error waiting for page load or getting source for {profile_url}: {e}")
        return None

    # --- Data Extraction (HIGHLY LIKELY TO BREAK - REQUIRES UPDATING SELECTORS) ---
    # You MUST inspect the LinkedIn profile HTML using browser dev tools to find the correct
    # CSS selectors (classes, IDs, tags). These change FREQUENTLY.
    # The selectors below are educated GUESSES and WILL need updating.
    data = {field: None for field in FIELD_NAMES} # Initialize dictionary
    data['linkedin_url'] = profile_url

    # Basic Info Section (pv-text-details__left-panel) - Adjust selector
    profile_section = soup.select_one('main section:first-of-type') # Very generic, likely needs refinement
    if profile_section:
        data['full_name'] = safe_get_text(profile_section, 'h1') # Usually the H1 element
        if data['full_name'] and ' ' in data['full_name']:
             parts = data['full_name'].split(' ', 1)
             data['first_name'] = parts[0]
             data['last_name'] = parts[1] if len(parts) > 1 else None
        else:
             data['first_name'] = data['full_name'] # Handle single names

        data['headline'] = safe_get_text(profile_section, 'div.text-body-medium') # Often a div after the name

        # Location (Might be in a separate span or div) - Adjust selector
        location_element = profile_section.select_one('span.text-body-small.inline.t-black--light')
        if location_element:
            location_text = location_element.get_text(strip=True)
            loc_parts = [p.strip() for p in location_text.split(',')]
            if len(loc_parts) == 3: # City, State, Country
                data['city'] = loc_parts[0]
                data['state'] = loc_parts[1]
                data['country'] = loc_parts[2]
            elif len(loc_parts) == 2: # City/State, Country or City, Region
                data['city'] = loc_parts[0] # Guessing city/state
                data['country'] = loc_parts[1]
            elif len(loc_parts) == 1:
                data['country'] = loc_parts[0] # Or maybe just country

    # --- Experience Section ---
    # Finding the current position is tricky. Often involves looking for "Present"
    # This requires iterating through experience items.
    # Selectors here are highly unstable.
    experience_items = soup.select('li.pvs-list__paged-list-item') # Generic selector for list items in sections
    current_experience = None

    # Try to find the experience section explicitly (difficult)
    experience_section = None
    all_sections = soup.select('section.artdeco-card') # A common card element
    for section in all_sections:
        header = section.select_one('h2 span[aria-hidden="true"]')
        if header and 'Experience' in header.get_text(strip=True):
            experience_section = section
            break

    if experience_section:
        # Find list items within the identified experience section
        exp_items_in_section = experience_section.select('li.pvs-list__paged-list-item') # Adjust selector
        for item in exp_items_in_section:
            # Check for "Present" in the date range - selector needs verification
            date_range_element = item.select_one('span.t-14.t-normal span[aria-hidden="true"]')
            if date_range_element and 'Present' in date_range_element.get_text():
                current_experience = item
                break # Found the most current one with "Present"

        if current_experience:
            # Extract data from the current experience item - Selectors need verification!
            data['title'] = safe_get_text(current_experience, 'span[aria-hidden="true"]') # Often the main span
            company_info = current_experience.select_one('span.t-14.t-normal span[aria-hidden="true"]') # Might be the second span
            if company_info:
                 company_text = company_info.get_text(strip=True)
                 # Basic split, might need refinement if format includes employment type (e.g., "Company Name · Full-time")
                 data['company_name'] = company_text.split('·')[0].strip()

            # Company LinkedIn URL (if available as a link) - Selector needs verification
            company_link_element = current_experience.select_one('a[data-field="experience_company_logo"]') # Check link around logo or company name
            if company_link_element:
                 href = company_link_element.get('href')
                 if href and 'linkedin.com/company/' in href:
                     data['company_linkedin_url'] = "https://www.linkedin.com" + href.split('?')[0] # Clean URL
                 # Getting company domain/URL usually requires visiting the company page (adds complexity/risk)
                 # data['company_url'] = ? # Needs another step
                 # data['company_domain'] = ? # Needs another step

    # --- Industry (Often on the company page, not directly on profile experience) ---
    # Sometimes the main profile has an industry listed in the "About" or another section
    # Needs inspection. For now, we'll leave it None.
    # data['industry'] = ?

    # --- Fields That CANNOT Be Reliably Scraped Directly ---
    print("Warning: The following fields are generally NOT available via direct profile scraping:")
    print("  email, phone_number, status, email_status, sanitized_phone_number,")
    print("  estimated_num_employees (sometimes inferred from company page), seniority (inferred),")
    print("  secondary_industries, functions, departments, subdepartments, keywords")
    data['status'] = 'Not Scraped'
    data['email'] = 'Not Scraped'
    data['email_status'] = 'Not Scraped'
    data['estimated_num_employees'] = 'Not Scraped'
    data['phone_number'] = 'Not Scraped'
    data['sanitized_phone_number'] = 'Not Scraped'
    data['seniority'] = 'Not Scraped' # Could try to infer from title keywords
    data['industry'] = data.get('industry', 'Not Scraped') # Use scraped if found, else default
    data['secondary_industries'] = 'Not Scraped'
    data['industries'] = data.get('industry', 'Not Scraped') # Use main industry if found
    data['functions'] = 'Not Scraped'
    data['departments'] = 'Not Scraped'
    data['subdepartments'] = 'Not Scraped'
    data['keywords'] = 'Not Scraped' # Could potentially extract from 'About' section text

    print(f"Finished scraping {profile_url}")
    return data

# --- Main Execution ---
if __name__ == "__main__":
    if not LINKEDIN_USERNAME or not LINKEDIN_PASSWORD:
        print("Error: Please set LINKEDIN_USER and LINKEDIN_PASS environment variables.")
        exit(1)

    target_profile_url = input("Enter the full LinkedIn profile URL: ")
    if not target_profile_url or "linkedin.com/in/" not in target_profile_url:
        print("Invalid LinkedIn profile URL.")
        exit(1)

    print("Initializing WebDriver...")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Running headless often gets detected by LinkedIn - start without it for debugging
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36") # Mimic a real browser

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    all_data = []

    try:
        # --- Login ---
        print("Attempting to log in...")
        driver.get("https://www.linkedin.com/login")
        random_delay(2, 5)

        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        )

        username_field.send_keys(LINKEDIN_USERNAME)
        random_delay(0.5, 1.5)
        password_field.send_keys(LINKEDIN_PASSWORD)
        random_delay(0.5, 1.5)
        password_field.send_keys(Keys.RETURN)

        print("Login submitted. Waiting for potential redirect/home page...")
        # Wait for a known element on the feed page to confirm login
        try:
            WebDriverWait(driver, 20).until(
                 EC.presence_of_element_located((By.ID, "global-nav-search")) # Search bar
            )
            print("Login successful!")
        except Exception as e:
             print(f"Login failed or took too long. Check credentials or CAPTCHA. Error: {e}")
             # Consider saving page source here for debugging driver.save_screenshot('login_error.png')
             raise Exception("Login Failed") # Stop the script if login fails

        random_delay(3, 7)

        # --- Scrape Target Profile ---
        profile_data = scrape_profile(driver, target_profile_url)
        if profile_data:
            all_data.append(profile_data)
        else:
            print(f"Failed to scrape data for {target_profile_url}")

    except Exception as e:
        print(f"An error occurred: {e}")
        # Optional: Save screenshot on error
        # driver.save_screenshot('error_screenshot.png')

    finally:
        print("Closing WebDriver.")
        driver.quit()

    # --- Save to CSV ---
    if all_data:
        print(f"Saving data to {OUTPUT_CSV_FILE}...")
        df = pd.DataFrame(all_data)
        # Reorder columns to match requested list
        df = df[FIELD_NAMES]
        try:
            # Check if file exists to write header accordingly
            file_exists = os.path.isfile(OUTPUT_CSV_FILE)
            df.to_csv(OUTPUT_CSV_FILE, mode='a', index=False, header=not file_exists, quoting=csv.QUOTE_ALL)
            print("Data saved successfully.")
        except Exception as e:
            print(f"Error saving data to CSV: {e}")
    else:
        print("No data was scraped.")