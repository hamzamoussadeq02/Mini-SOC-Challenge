import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# URL of the Wazuh dashboard
url = "https://localhost"

# --- Chrome Options ---
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')

# --- Initialize WebDriver ---
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

exit_code = 0  # Assume success, flip to 1 if something fails

# --- Test 1: HTTPS reachability ---
try:
    driver.get(url)
    print("✅ Test Passed: Dashboard is reachable over HTTPS")
except WebDriverException as e:
    print(f"❌ Test Failed: Dashboard is not reachable. Error: {e}")
    exit_code = 1

# --- Test 2: Page title ---
expected_title = "Wazuh"  # Adjust to your actual dashboard title
if driver.title == expected_title:
    print(f"✅ Test Passed: Page title is '{driver.title}'")
else:
    print(f"❌ Test Failed: Expected '{expected_title}' but got '{driver.title}'")
    exit_code = 1

# --- Test 3: Login form elements ---
try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']")))
    print("✅ Username element found")
except TimeoutException:
    print("❌ Username element NOT found")
    exit_code = 1

try:
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']")))
    print("✅ Password element found")
except TimeoutException:
    print("❌ Password element NOT found")
    exit_code = 1

try:
    wait.until(EC.presence_of_element_located(
        (By.XPATH, "//span[@class='euiButtonContent euiButton__content']//span[text()='Log in']")))
    print("✅ Login button found")
except TimeoutException:
    print("❌ Login button NOT found")
    exit_code = 1

# --- Clean up ---
driver.quit()
sys.exit(exit_code)   # 🔴 CI/CD pass/fail signal
