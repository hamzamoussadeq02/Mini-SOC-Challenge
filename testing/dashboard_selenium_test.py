from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# URL of the Wazuh dashboard
url = "https://192.168.1.27"

# --- Chrome Options ---
options = Options()
options.add_argument('--headless')                 # Run Chrome in headless mode (no GUI)
options.add_argument('--no-sandbox')               # Needed for Linux environments without a GUI
options.add_argument('--disable-dev-shm-usage')    # Avoids some shared memory issues
options.add_argument('--ignore-certificate-errors')# Accept self-signed certificates

# --- Initialize WebDriver ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds for elements to appear

# --- Test 1: HTTPS reachability ---
try:
    driver.get(url)
    print("✅ Test Passed: Dashboard is reachable over HTTPS")
except WebDriverException as e:
    print(f"❌ Test Failed: Dashboard is not reachable. Error: {e}")

# --- Test 2: Page title ---
expected_title = "Wazuh"  # Adjust to the actual dashboard title
if driver.title == expected_title:
    print(f"✅ Test Passed: Page title is '{driver.title}'")
else:
    print(f"❌ Test Failed: Expected '{expected_title}' but got '{driver.title}'")

# --- Test 3: Login form elements ---
login_elements_status = {"username": False, "password": False, "login_button": False}
# Check Username input
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    print("✅ Username element found")
    login_elements_status["username"] = True
except TimeoutException:
    print("❌ Username element NOT found")

# Check Password input
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
    print("✅ Password element found")
    login_elements_status["password"] = True
except TimeoutException:
    print("❌ Password element NOT found")

# Check Login button
try:
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//span[@class='euiButtonContent euiButton__content']//span[text()='Log in']")))
    print("✅ Login button found")
    login_elements_status["login_button"] = True
except TimeoutException:
    print("❌ Login button NOT found")

# Overall summary
if all(login_elements_status.values()):
    print("✅ Test Passed: All login form elements are present")
else:
    print("❌ Test Failed: Some login form elements are missing")
# --- Clean up ---
driver.quit()