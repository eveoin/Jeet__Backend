from flask import Flask, request, redirect, url_for
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from getpass import getpass
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        passwd = request.form['password']

        # Use ChromeDriverManager to manage ChromeDriver installation
        chrome_driver_path = ChromeDriverManager().install()

        # Create Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True  # Run Chrome in headless mode

        # Initialize Chrome WebDriver with Chrome options and path
        service = Service(chrome_driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Navigate to Facebook
        driver.get('https://www.facebook.com')

        # Wait for the page to load
        driver.implicitly_wait(10)  # Adjust the timeout as needed

        # Find username and password fields by ID
        txtUsername = driver.find_element(By.ID, 'email')
        txtPasswd = driver.find_element(By.ID, 'pass')

        # Enter username and password
        txtUsername.send_keys(username)
        txtPasswd.send_keys(passwd)

        # Find login button by ID and submit
        btnLogin = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'u_0_b')))
        btnLogin.click()

        return redirect(url_for('success'))
    return '''
        <form method="post">
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br><br>
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/success')
def success():
    return 'Login Successful'

if __name__ == '__main__':
    app.run(debug=True, port=40)