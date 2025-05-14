from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

import time
import random
import string

class AutoRegister:
    def __init__(self):
        self.driver = None
        self.temp_email = None
        self.password = "x&b{e#5$yJymsh0"

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=options)
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def get_temp_email(self):
        try:
            self.driver.get("https://tempmailo.com/")
            wait = WebDriverWait(self.driver, 10)
            email_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            self.temp_email = email_element.get_attribute('value')
            print(f"获取到临时邮箱: {self.temp_email}")
            return True
        except Exception as e:
            print(f"获取临时邮箱失败: {str(e)}")
            return False

    def register_nosec(self):
        try:
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get("https://i.nosec.org/register?service=https://fofa.info/f_login")
            
            wait = WebDriverWait(self.driver, 10)
            
            # 填写邮箱
            email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
            email_input.send_keys(self.temp_email)
            
            # 填写密码
            password_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            for pwd_input in password_inputs:
                pwd_input.send_keys(self.password)
            
            # 生成随机用户名
            username = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            username_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='用户昵称']")
            username_input.send_keys(username)
            
            print("\n请手动完成以下步骤:")
            print("1. 输入验证码")
            print("2. 勾选同意协议")
            print("3. 点击注册按钮")
            print("4. 完成后请不要关闭浏览器窗口")
            
            # 保持窗口打开
            while True:
                time.sleep(1)
            
        except Exception as e:
            print(f"注册过程出错: {str(e)}")
            return False

    def run(self):
        try:
            self.setup_driver()
            if self.get_temp_email():
                self.register_nosec()
            else:
                print("获取临时邮箱失败")
        except KeyboardInterrupt:
            print("\n程序已停止")
        except Exception as e:
            print(f"运行出错: {str(e)}")

if __name__ == "__main__":
    auto_register = AutoRegister()
    auto_register.run()
