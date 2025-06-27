
# Selenium LinkedIn Profile Scraper

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![Beautiful Soup](https://img.shields.io/badge/beautifulsoup4-4.9+-yellow.svg)](https://www.crummy.com/software/BeautifulSoup/)
[![pandas](https://img.shields.io/badge/pandas-1.0+-orange.svg)](https://pandas.pydata.org/)
[![Webdriver Manager](https://img.shields.io/badge/webdriver--manager-3.5+-brightgreen.svg)](https://pypi.org/project/webdriver-manager/)

## About

This Python script utilizes the Selenium WebDriver to automate the process of navigating to and extracting publicly available information from LinkedIn profiles. It logs into LinkedIn using provided environment variables for credentials and then scrapes data from a specified profile URL. The extracted data, where obtainable through direct scraping, is then saved into a CSV file. **Please be aware that LinkedIn's website structure changes frequently, and direct scraping of certain data points like email addresses and phone numbers is generally not possible and violates LinkedIn's terms of service. This script focuses on publicly available profile information. This was requsted by a Cyber Security specialist for a very specific use-case.**

## Setup

1.  **Prerequisites:**
    * **Python 3.6+** installed on your system. You can download it from [https://www.python.org/downloads/](https://www.python.org/downloads/).
    * **pip** (Python package installer) should be included with your Python installation.

2.  **Install Dependencies:**
    Open your terminal or command prompt, navigate to the `Selenium_Python_WebScrapper` directory, and run the following command to install the necessary Python libraries:

    ```bash
    pip install selenium webdriver-manager beautifulsoup4 pandas
    ```

3.  **Set Environment Variables:**
    For security reasons, the script uses environment variables to store your LinkedIn username and password. You need to set these before running the script.

    * **On macOS/Linux:**
        Open your terminal and use the `export` command:
        ```bash
        export LINKEDIN_USER="your_linkedin_username"
        export LINKEDIN_PASS="your_linkedin_password"
        ```
        You might want to add these lines to your shell's configuration file (e.g., `.bashrc`, `.zshrc`) to make them persistent.

    * **On Windows:**
        Open Command Prompt or PowerShell and use the `set` command:
        ```bash
        set LINKEDIN_USER="your_linkedin_username"
        set LINKEDIN_PASS="your_linkedin_password"
        ```
        To make these persistent, you can use the `setx` command (note that this might require administrator privileges):
        ```bash
        setx LINKEDIN_USER "your_linkedin_username"
        setx LINKEDIN_PASS "your_linkedin_password"
        ```

    **Replace `"your_linkedin_username"` and `"your_linkedin_password"` with your actual LinkedIn credentials.**

## Usage

1.  **Navigate to the Script Directory:**
    Open your terminal or command prompt and navigate to the `Selenium_Python_WebScrapper` directory where you saved the `your_script_name.py` file (replace `your_script_name.py` with the actual name of your Python file).

2.  **Run the Script:**
    Execute the Python script using the following command:

    ```bash
    python your_script_name.py
    ```

    The script will prompt you to enter the full LinkedIn profile URL you want to scrape.

3.  **Enter Profile URL:**
    Copy and paste the complete URL of the LinkedIn profile you want to scrape and press Enter.

4.  **View Results:**
    After the script finishes execution, the scraped data (if any is successfully extracted) will be saved in a CSV file named `linkedin_data.csv` in the same directory where you ran the script.

## Important Considerations and Limitations

* **Website Structure Changes:** LinkedIn frequently updates its website structure. This script relies on specific HTML elements and CSS selectors, which may break without notice, requiring updates to the script.
* **Terms of Service:** Scraping LinkedIn profiles might violate their terms of service. Use this script responsibly and for personal, non-commercial purposes only. Be aware of the potential risks involved.
* **Data Availability:** Many of the fields requested in the `FIELD_NAMES` list (e.g., email, phone number, detailed company information) are **not publicly available** on LinkedIn profiles and cannot be reliably scraped directly. This script primarily focuses on extracting publicly visible information.
* **Rate Limiting:** LinkedIn may implement rate limiting or other measures to prevent automated scraping. Excessive or rapid scraping attempts may lead to temporary or permanent blocking of your IP address or account. The script includes random delays to mimic human behavior, but this does not guarantee you won't be detected.
* **Login Requirement:** The script logs into LinkedIn to access profile information. Ensure your login credentials are correct and securely stored as environment variables.
* **CAPTCHA:** LinkedIn may present CAPTCHA challenges during login, which can prevent the script from working.
* **"Not Scraped" Fields:** The script explicitly marks fields that are generally not available through direct profile scraping as "Not Scraped" in the output CSV.
* **Ethical Use:** Use this script ethically and responsibly. Do not use it for spamming, generating leads for unsolicited outreach, or any other activities that violate privacy or LinkedIn's terms of service.

## Disclaimer

This script is provided for educational and personal use only. The author is not responsible for any misuse or violation of LinkedIn's terms of service that may result from using this script. Use it at your own risk. Always respect website terms of service and robots.txt files.
