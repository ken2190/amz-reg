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


first_names = read_file_helper("./databases/name/first_name.txt")
last_names = read_file_helper("./databases/name/last_name.txt")

hotmail_data = read_file_helper("mail.txt")


mail_domain_data = read_file_helper("host_mail_domain.txt")

HOST_DOMAIN = mail_domain_data.split("|")[0]
PASSWORD_HOST_DOMAIN = mail_domain_data.split("|")[1]

user_agents = {}
user_agents["android"] = read_file_helper("./databases/user-agents/user-agents-android.txt")





class SeleniumBot:
    def __init__(self,order_url,register_url,proxy = None,user_agent_option = None ,is_firefox = True):
        self.register_url = register_url
        self.order_url = order_url
        self.proxy = proxy
        self.is_firefox = is_firefox
        self.user_agent_option = user_agent_option
    
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
        return False


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


    def register_account(self,email,paswd): 
        last_name = last_names[randint(0,len(last_names)-1)]
        first_name = first_names[randint(0,len(first_names)-1)]
        full_name = last_name + " " + first_name
        self.email = email
        self.paswd = paswd


        try:
            self.driver.get(self.register_url)

            sleep(randint(1,3))
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.ID, 'emailAddress'))).send_keys(email)
            sleep(uniform(0.5,1.5))
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.TAG_NAME, 'button'))).click()

            # register url
            #if "register" in self.driver.current_url:
            sleep(randint(1,2))
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, 'ap_customer_name'))).send_keys(full_name)
            sleep(randint(1,2))
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.ID, 'ap_password'))).send_keys(paswd)
            sleep(uniform(0.2,0.6))
            try:
                WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.ID, 'ap_password_check'))).send_keys(paswd)
            except:
                pass
            sleep(uniform(0.2,0.6))
            # click create
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'continue'))).click()

            is_solved_captcha = self.solving_captcha(timeout=60)
            if is_solved_captcha:
                # after pass captcha
                try:
                    # wait input code
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'cvf-input-code')))
                except:
                    pass
                
                if not "hotmail" in email or "outlook" in email:
                    otp_data = get_code_amz_yandex(HOST_DOMAIN,PASSWORD_HOST_DOMAIN,email)
                else:
                    otp_data = get_code_amz(email,paswd)
                if otp_data["status_code"] == 1:
                    # get code success
                    WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.ID, 'cvf-input-code'))).send_keys(otp_data["code"])
                    sleep(uniform(0.5,1))
                    WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.CLASS_NAME, 'a-button-input'))).click()

                    if self.wait_url(url="account-setup/finish",timeout=30):
                        sleep(randint(1,2))
                        WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.TAG_NAME, 'button'))).click()
                        if self.wait_element(element=By.ID,name="twotabsearchtextbox"):
                            # register successs => save account
                            write_file_helper("amz_account.txt",f"{email}|{paswd}")
                            sleep(randint(1,3))
                            for _ in range(2):
                                try:
                                    self.driver.get(self.order_url)

                                    WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, 'submit.digital-bulk-buy-now'))).click()

                                    sleep(randint(1,2))
                                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "a-button-input"))).click()
                                    sleep(randint(1,2))
                                    WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "a-button-input.a-button-text")))[0].click()
                                    sleep(randint(1,2))
                                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, "placeYourOrder1"))).click()
                                    if self.wait_url(url="buy/thankyou",timeout=30):
                                        sleep(randint(5,10))
                                        # save account order success
                                        write_file_helper("amz_account_order_success.txt",f"{email}|{paswd}")
                                        break
                                except:
                                    pass
                                
                elif otp_data["status_code"] == 0:
                    write_file_helper("hotmail_khongnhandccode.txt",f"{email}|{paswd}")
                elif otp_data["status_code"] == -1:
                    write_file_helper("hotmail_die.txt",f"{email}|{paswd}")
            
            self.driver.quit()
            return True
        except Exception as e:
            print(e)
            self.driver.quit()
            return False




proxy_running = []

def bot_helper(hotmail,order_url,register_url,proxy = None,user_agent_option = None ,is_firefox = True):
    bot = SeleniumBot(order_url,register_url,proxy,user_agent_option,is_firefox)
    is_init = bot.init_selenium()
    if is_init:
        bot.register_account(hotmail["email"],hotmail["password"])


def run(hotmail_list,order_urls,register_url,proxy_data = None,user_agent_option = None ,is_firefox = True):
    global port_running
    thread_list = list()
    
    proxy = proxy_data.split("|")[0]
    proxyguys_rest_url = proxy_data.split("|")[1]
    number_thread = len(hotmail_list)
    for index in range(number_thread):
        order_url = order_urls[randint(0,len(order_urls)-1)]
        hotmail = hotmail_list[index]
        t = threading.Thread(name='Email {}'.format(hotmail["email"]), target=bot_helper, args=(hotmail,order_url,register_url,proxy,user_agent_option,is_firefox))
        t.start()
        sleep(5)
        thread_list.append(t)

    for thread in thread_list:
        thread.join()
    proxyguys_api(proxyguys_rest_url)
    sleep(60)
    proxy_running.remove(proxy)


proxy_data_list = read_file_helper("proxy_proxyguys.txt")

def get_hotmail(number):
    global hotmail_data
    hotmail_list = []
    for v in hotmail_data:
        hotmail_got_data = read_file_helper("mail_got.txt")
        if not v in hotmail_got_data:
            write_file_helper("mail_got.txt",v)
            hotmail_dict  = {}
            if "|" in v:
                hotmail_dict["email"] = v.split("|")[0]
                hotmail_dict["password"] = v.split("|")[1]
            else:
                hotmail_dict["email"] = v
                hotmail_dict["password"] = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(randint(8,15)))
            hotmail_list.append(hotmail_dict)

            if len(hotmail_list) == number:
                return hotmail_list
    return hotmail_list



def check_account_non_register():
    global hotmail_data
    f = open("mail_got.txt","w")
    f.close()
    f = open("mail.txt","w")
    f.close()

    amz_account = read_file_helper("amz_account.txt")
    for v in hotmail_data:
        if not v in amz_account:
            write_file_helper("mail.txt",v)


def start_helper(data):
    global hotmail_data
    number_of_threads = int(data["number_of_threads"])
    user_agent_option = "android" if data["is_user_agent"] == "True" else None
    order_urls = data["order_url"].strip().split("\n")
    register_url = data["register_url"]
    is_ok = False
    for _ in range(1000000):
        for proxy_data in proxy_data_list:
            
            proxy = proxy_data.split("|")[0]
            if not proxy in proxy_running:
                hotmail_list = get_hotmail(number_of_threads)
                print("hotmail_list",hotmail_list)
                if len(hotmail_list) == 0:
                    if not is_ok:
                        
                        check_account_non_register()
                        hotmail_data = read_file_helper("mail.txt")
                        if len(hotmail_data) < 20:
                            is_ok = True
                        break
                    else:
                        return True
                t = threading.Thread(target=run,args=(hotmail_list,order_urls,register_url,proxy_data,user_agent_option))
                t.start()
                sleep(2)
                proxy_running.append(proxy)
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
    except:
        return jsonify({"status": 400, "message": "fail"})


if __name__ == '__main__':
    app.run()