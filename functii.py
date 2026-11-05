import csv
import os
import random
import re
# from datetime import datetime
import datetime
import pandas as pd
import json
from selenium.common import exceptions
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import http.client
from datetime import date
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
from live_predictions import update_match_live
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
import random
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from dotenv import load_dotenv

load_dotenv()


def required_env(name):
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set {name} in .env (see .env.example).")
    return value


def site_b_selector(selector):
    # "@UI" stands for the site's CSS class prefix, kept in .env.
    return selector.replace("@UI", required_env("SITE_B_UI_PREFIX"))

# options = webdriver.ChromeOptions()
# prefs = {"credentials_enable_service": False,
#          "profile.password_manager_enabled": False}
# options.add_experimental_option("prefs", prefs)
# options.add_argument("--start-maximized")
# options.add_argument("--disable-notifications")
# options.add_argument('--no-sandbox')

# # disable the "Chrome is controled by automated software" message from browser
# options.add_experimental_option("useAutomationExtension", False)
# options.add_experimental_option("excludeSwitches", ["enable-automation"])
# options.add_experimental_option("detach", True)

# # set path to chromedriver.exe
# PATH = Service("/root/Documents/chromedriver-linux64/chromedriver")

# # set user-agent
# useragentarray = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/108.0.0.0 Safari/537.36",
#                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#                   "Chrome/107.0.0.0 Safari/537.36", ]

# driver = webdriver.Chrome(options=options)

# # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver.command_executor.set_timeout(10000)
# driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[random.randint(0, 1)]})
# ---- Configure Edge options ----

# ---------- Edge options ----------
options = EdgeOptions()
prefs = {"credentials_enable_service": False,
         "profile.password_manager_enabled": False}
options.add_experimental_option("prefs", prefs)
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument('--no-sandbox')

# disable "Chrome is controlled by automated software"
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("detach", True)

# ---------- User-agent ----------
useragentarray = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
]
user_agent = random.choice(useragentarray)
options.add_argument(f"user-agent={user_agent}")

# ---------- Create Edge driver (no explicit PATH) ----------
driver = webdriver.Edge(options=options)  # Selenium will use default Windows EdgeDriver
driver.set_page_load_timeout(30)  # optional timeout

class SiteB:
    def __init__(self):
        self.list_sport_sites: list = ["https://www.espn.com/", "https://www.eurosport.ro/",
                                       "https://www.cbssports.com/", "https://www.digisport.ro/",
                                       "https://www.sport.ro/", "https://www.gsp.ro/", "https://www.fanatik.ro/",
                                       "https://www.fanatik.ro/",
                                       "https://as.ro/"]
        self.predictions_list: list = []
        self.predictions_extracted = False
        self.start_day = 0
        self.event_predicitons_list: list = []
        self.counter = 0
        self.no_of_sites_to_visit = 0
        self.sites_counter = 0
        self.run_while = False
        self.scroll_counter = 0
        self.timer = 0
        self.random_time = random.randint(362661, 401540)
        self.seconds_counter = 0
        self.function_to_execute = "do_nothing"
        self.liveEvents = []
        self.clicked_container = 0
        self.gdpr_timer = 0
        self.what_to_to = 0
        self.visit_sport = 2
        self.event_list_position = 0
        self.lovitura_de_start = "0"
        self.time_now = "0"
        self.bets_counter = 0
        self.meciextras = ""
        self.predictions = {}
        self.placebet_counter = 0
        self.check_login = False
        self.balance = 0
        self.prediction_to_remove = ""
        self.placed_bet = False
        self.over_goals_counter = 0
        self.repeat_try_make_bets = 0
        self.try_to_make_bet = 4
        self.get_live_event = 3
        self.procent_de_pariere = 30
        self.oldtime = time.time()
        self.used_matches = []

    def check_for_popup(self):
        try:
            driver.find_element(by=By.CLASS_NAME, value="optly-modal-close").click()
            # time.sleep(random.randint(4, 7))
        except NoSuchElementException:
            self.counter += 1
            pass

    def end_of_function(self):
        self.counter = 0
        self.what_to_to += 1

    def extract_predictions(self):
        # get predicitons
        print("extrag predictii")
        today = date.today()
        api_key = required_env("PREDICTIONS_API_KEY")
        api_host = required_env("PREDICTIONS_API_HOST")
        api_path = required_env("PREDICTIONS_API_PATH").rstrip("/")

        conn = http.client.HTTPSConnection(api_host)

        headers = {
            'X-RapidAPI-Key': api_key,
            'X-RapidAPI-Host': api_host
        }

        conn.request("GET", api_path + "/" + str(today) + "/" + str(today), headers=headers)

        res = conn.getresponse()
        data = res.read()
        data_str: str = str(data)
        # print(data_str)
        # create a dictionary with homeTeam as key and a list of predictions assigned to each key
        for i in range(data_str.count('}')):
            self.predictions_list.append(re.match(r'(.*)("id.*)', re.sub(r'\'', r'', data_str.split("}")[i])).group(2))
        for i in range(len(self.predictions_list)):
            new_list = []
            if float(str(self.predictions_list[i].split(',')[20].split(':')[1][1:-1])) >= 50:
                new_list.append("Peste 1.5")
                new_list.append("Peste 1")
                new_list.append("Peste 1.25")
            else:
                new_list.append("Sub 1.5")
                new_list.append("Sub 1.15")
                new_list.append("Sub 2")
                new_list.append("Sub 2.25")
            if float(str(self.predictions_list[i].split(',')[21].split(':')[1][1:-1])) >= 50:
                new_list.append("Peste 2")
                new_list.append("Peste 2.25")
                new_list.append("Peste 2.5")
                new_list.append("Peste 1.75")
            else:
                new_list.append("Sub 2.5")
                new_list.append("Sub 2.75")
                new_list.append("Sub 3")
                new_list.append("Sub 3.25")
            if float(str(self.predictions_list[i].split(',')[22].split(':')[1][1:-1])) >= 50:
                new_list.append("Peste 3")
                new_list.append("Peste 3.25")
                new_list.append("Peste 3.5")
                new_list.append("Peste 2.75")
            else:
                new_list.append("Sub 3.5")
                new_list.append("Sub 3.75")
                new_list.append("Sub 4")
            self.predictions[self.predictions_list[i].split(',')[5].split(':')[1][1:-1]] = new_list

        self.predictions_extracted = True
        self.end_of_function()

        print("Astazi sunt: " + str(len(self.predictions)))

    def set_event_predictions(self, elem: str):
        self.event_predicitons_list.append(str(elem).split(',')[10])
        self.event_predicitons_list.append(str(elem).split(',')[11])
        self.event_predicitons_list.append(str(elem).split(',')[12])
        self.event_predicitons_list.append(str(elem).split(',')[13])
        self.event_predicitons_list.append(str(elem).split(',')[14])
        self.event_predicitons_list.append(str(elem).split(',')[15])
        self.event_predicitons_list.append(str(elem).split(',')[16])
        self.event_predicitons_list.append(str(elem).split(',')[17])
        for i in range(len(self.event_predicitons_list)):
            if "over15goals" in str(self.event_predicitons_list[i]).split(":")[0]:
                if float(re.sub(r'"', '', str(self.event_predicitons_list[i]).split(":")[1])) >= 50:
                    self.event_predicitons_list[i] = "Peste 1.5"
                    self.event_predicitons_list.append("Peste 1")
                    self.event_predicitons_list.append("Peste 1.25")
                else:
                    self.event_predicitons_list[i] = "Sub 1.5"
                    self.event_predicitons_list.append("Sub 1.75")
                    self.event_predicitons_list.append("Sub 2")
                    self.event_predicitons_list.append("Sub 2.25")
            elif "over25goals" in str(self.event_predicitons_list[i]).split(":")[0]:
                if float(re.sub(r'"', '', str(self.event_predicitons_list[i]).split(":")[1])) >= 50:
                    self.event_predicitons_list[i] = "Peste 2.5"
                    self.event_predicitons_list.append("Peste 2")
                    self.event_predicitons_list.append("Peste 2.25")
                    self.event_predicitons_list.append("Peste 1.75")
                else:
                    self.event_predicitons_list[i] = "Sub 2.5"
                    self.event_predicitons_list.append("Sub 2.75")
                    self.event_predicitons_list.append("Sub 3")
                    self.event_predicitons_list.append("Sub 3.25")
            elif "over35goals" in str(self.event_predicitons_list[i]).split(":")[0]:
                if float(re.sub(r'"', '', str(self.event_predicitons_list[i]).split(":")[1])) >= 50:
                    self.event_predicitons_list[i] = "Peste 3.5"
                    self.event_predicitons_list.append("Peste 3.25")
                    self.event_predicitons_list.append("Peste 3")
                    self.event_predicitons_list.append("Peste 2.75")
                else:
                    self.event_predicitons_list[i] = "Sub 3.5"
                    self.event_predicitons_list.append("Sub 3.75")
                    self.event_predicitons_list.append("Sub 4")

    def visit_sport_sites(self):
        match self.counter:
            case 0:
                print("setez nr de site-uri")
                self.no_of_sites_to_visit = random.randint(1, len(self.list_sport_sites))
                print("Number of sites to visit = " + str(self.no_of_sites_to_visit))
                self.scroll_counter = 0
                self.sites_counter = 0
                self.counter += 1
                self.random_time = random.randint(4135740, 4135750)
                self.seconds_counter = 0
            case 1:
                # visit sport sites
                print("vizitez site")
                if self.sites_counter < self.no_of_sites_to_visit:
                    driver.get(self.list_sport_sites[random.randint(0, len(self.list_sport_sites) - 1)])
                    time.sleep(random.randint(4, 8))
                    try:
                        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Da, accept')]").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass
                    try:
                        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Accept all')]").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass
                    try:
                        driver.find_element(by=By.ID, value="onetrust-accept-btn-handler").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass

                    try:
                        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'ACCEPTA TOT')]").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass
                    self.counter += 1
                else:
                    self.end_of_function()
            case 2:
                # scroll down page
                print("citesc site")
                for i in range(5):
                    driver.execute_script("window.scrollTo(0, window.scrollY +600)")
                    time.sleep(random.randint(8, 20))
                self.sites_counter += 1
                self.counter += 1
                """self.timer += 1
                if self.timer / self.random_time == 1:
                    self.timer = 0
                    self.seconds_counter += 1
                if self.seconds_counter == 5:
                    print("citesc site")
                    self.seconds_counter = 0
                    if self.scroll_counter < 5:
                        driver.execute_script("window.scrollTo(0, window.scrollY +600)")
                        self.scroll_counter += 1
                    else:
                        self.counter += 1
                        self.sites_counter += 1
                        self.scroll_counter = 0"""
            case 3:
                if self.sites_counter < self.no_of_sites_to_visit:
                    self.counter = 1
                else:
                    self.random_time = random.randint(362661, 401540)
                    self.end_of_function()

    @staticmethod
    def visit_site_b():
        driver.get(required_env("SITE_B_URL"))

    def get_live_events(self):
        match self.counter:
            case 0:
                print("Get live events")
                driver.get(required_env("SITE_B_URL"))
                self.counter += 1
                self.seconds_counter = 0
                self.liveEvents = []
                self.clicked_container = 0
            case 1:
                self.wait_seconds(6, 12)
            case 2:
                print("check_popup")
                self.check_for_popup()
                self.activitatea_de_joc()
                self.counter += 1
            case 3:
                self.wait_seconds(3, 5)
            case 4:
                self.accept_gdpr()
            case 5:
                self.activitatea_de_joc()
                driver.find_element(by=By.CLASS_NAME, value="icon-wrapper.icon-prefix.sportsbook").click()
                self.counter += 1
            case 6:
                self.wait_seconds(12, 18)
            case 7:
                self.activitatea_de_joc()
                driver.find_element(by=By.XPATH, value="//*[@title='Fotbal']").click()
                self.counter += 1
            case 8:
                self.wait_seconds(6, 8)
            case 9:
                self.activitatea_de_joc()
                driver.find_element(by=By.XPATH, value="//*[@id='rightPanel']/div[1]/div/a[2]").click()
                self.counter += 1
            case 10:
                self.wait_seconds(3, 6)
            case 11:
                self.activitatea_de_joc()
                try:
                    driver.find_element(by=By.CLASS_NAME,
                                        value=site_b_selector("@UI-navicon__sport-icon.@UI-navicon__sport-icon--small."
                                              "@UI-navicon__sport-icon--football")).click()
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()
            case 12:
                self.wait_seconds(3, 6)
            case 13:
                # print("Sunt aici")
                self.activitatea_de_joc()
                try:
                    collapsiblecontainer = driver.find_elements(by=By.CLASS_NAME, value="CollapsibleContainer__HeaderWrapper-sc-14bpk80-1.iunwi")
                    for i in range(len(collapsiblecontainer)):
                        try:
                            collapsiblecontainer[i].click()
                        except exceptions.StaleElementReferenceException:
                            pass
                        time.sleep(random.randint(1, 3))
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()
            case 14:
                self.activitatea_de_joc()
                eventLinks = []
                eventlinks = driver.find_elements(by=By.CLASS_NAME, value=site_b_selector("@UI-event-item__link"))
                # print(eventLinks)
                for i in eventlinks:
                    try:
                        eventLinks.append(i.get_attribute("href"))
                    except NoSuchElementException:
                        pass
                for i in range(len(eventLinks)):
                    self.liveEvents.append(eventLinks[i])
                self.repeat_try_make_bets = len(self.liveEvents)
                self.end_of_function()

    @staticmethod
    def activitatea_de_joc():
        try:
            driver.find_element(by=By.CLASS_NAME, value="_1etkxf1").click()
            time.sleep(2)
        except NoSuchElementException:
            pass

    def login_site_b(self, username, password):
        match self.counter:
            case 0:
                driver.get(required_env("SITE_B_URL"))
                self.counter += 1
            case 1:
                self.wait_seconds(3, 6)
            case 2:
                self.accept_gdpr()
            case 3:
                self.activitatea_de_joc()
                try:
                    driver.find_element(by=By.CLASS_NAME, value="css-h33w7b").click()
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()
            case 4:
                self.wait_seconds(3, 6)
            case 5:
                self.activitatea_de_joc()
                try:
                    driver.find_element(by=By.CLASS_NAME, value="css-182et88.e8wsl0z0").click()
                    time.sleep(2)
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()
            case 6:
                self.wait_seconds(2, 4)
            case 7:
                self.activitatea_de_joc()
                for character in username:
                    driver.find_element(by=By.CLASS_NAME, value="css-182et88.e8wsl0z0").send_keys(character)
                    time.sleep(random.uniform(0.3, 1))
                self.counter += 1
            case 8:
                self.wait_seconds(4, 7)
            case 9:
                self.activitatea_de_joc()
                try:
                    driver.find_element(by=By.CLASS_NAME, value="css-3dcbho.e8wsl0z0").click()
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()
            case 10:
                self.wait_seconds(2, 4)
            case 11:
                self.activitatea_de_joc()
                for character in password:
                    driver.find_element(by=By.CLASS_NAME, value="css-3dcbho.e8wsl0z0").send_keys(character)
                    time.sleep(random.uniform(0.3, 1))
                driver.find_element(by=By.CLASS_NAME, value="css-3dcbho.e8wsl0z0").send_keys(Keys.ENTER)
                self.counter += 1
            case 12:
                self.wait_seconds(4, 7)
            case 13:
                if self.check_login:
                    self.counter = 4
                    self.what_to_to = self.try_to_make_bet
                    self.check_login = False
                else:
                    self.end_of_function()

    def try_to_make_bets(self, live_events: list, username, password, procent_de_pariere_min, procent_de_pariere_max):
        match self.counter:
            case 0:
                if len(live_events) > 0:
                    self.meciextras = ""
                    self.counter += 1
                    self.event_list_position = random.randint(0, len(live_events) - 1)
                    print(self.event_list_position)
                else:
                    self.go_to_sport_sites()
            case 1:
                driver.get(live_events[self.event_list_position])
                self.counter += 1
            case 2:
                self.wait_seconds(12, 25)
            case 3:
                # get team names
                self.activitatea_de_joc()
                try:
                    self.meciextras = driver.find_element(by=By.CLASS_NAME,
                                                          value="fc699").get_attribute("innerText").split(" - ")[0]
                except NoSuchElementException:
                    pass
                try:
                    self.meciextras = driver.find_element(by=By.CLASS_NAME,
                                                          value="_236f4").get_attribute("innerText").split(" - ")[0]
                except NoSuchElementException:
                    pass
                # check if match is in predictions dictionary
                print(self.meciextras)
                if self.meciextras and self.meciextras in self.predictions:
                    print("meciul este in lista de predictii")
                    self.counter += 1
                else:
                    del self.liveEvents[self.event_list_position]
                    print("meciul nu este in lista de predictii")
                    self.end_of_function()
            case 4:
                self.make_asian_bets(username, password, procent_de_pariere_min, procent_de_pariere_max)
            case 5:
                self.wait_seconds(5, 8)
            case 6:
                self.make_over_goals_bets(username, password, procent_de_pariere_min, procent_de_pariere_max)
            case 7:
                self.wait_seconds(5, 8)
            case 8:
                del self.liveEvents[self.event_list_position]
                self.end_of_function()

    def make_asian_bets(self, username, password, procent_de_pariere_min, procent_de_pariere_max):
        match self.bets_counter:
            case 0:
                self.activitatea_de_joc()
                try:
                    driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Linii Asiatice')]").click()
                    print("am apasat 'Linii asiatice'")
                    self.bets_counter += 1
                except NoSuchElementException:
                    self.counter += 1
            case 1:
                self.wait_seconds_in_bets(2, 4)
            case 2:
                self.activitatea_de_joc()
                listeAsiatice = driver.find_elements(by=By.CLASS_NAME,
                                                     value=site_b_selector("@UI-outcomes-list__toggler-toggle-button"))
                if len(listeAsiatice) > 0:
                    ActionChains(driver).move_to_element(listeAsiatice[1]).click(listeAsiatice[1]).perform()
                self.bets_counter += 1
            case 3:
                self.wait_seconds_in_bets(2, 4)
            case 4:
                self.activitatea_de_joc()
                buttons = driver.find_elements(by=By.CLASS_NAME, value="sc-dkrFOg.erQOWi")
                button_clicked = False
                for i in range(len(buttons)):
                    for j in range(len(self.predictions[self.meciextras])):
                        if str(self.predictions[self.meciextras][j]).split(" ")[0] + "\n" + \
                                str(self.predictions[self.meciextras][j]).split(" ")[1] in buttons[i].get_attribute("innerText"):
                            buttons[i].click()
                            self.prediction_to_remove = self.predictions[self.meciextras][j]
                            self.bets_counter += 1
                            button_clicked = True
                            break
                    if button_clicked:
                        break
                if not button_clicked:
                    self.counter += 1
                    self.bets_counter = 0
            case 4:
                self.placebet(username, password, procent_de_pariere_min, procent_de_pariere_max)
                if self.placed_bet:
                    self.bets_counter = 0
                    self.counter += 1

    def make_over_goals_bets(self, username, password, procent_de_pariere_min, procent_de_pariere_max):
        match self.bets_counter:
            case 0:
                self.activitatea_de_joc()
                print("Pun pariu Peste/Sub goluri")
                try:
                    # driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Toate')]").click()
                    driver.find_element(by=By.CLASS_NAME, value=site_b_selector("@UI-filter-menu__option.@UI-filter-menu__option--selected")).click()
                except NoSuchElementException:
                    self.counter += 1
                    pass
            case 1:
                self.wait_seconds_in_bets(6, 10)
            case 2:
                buttons = driver.find_elements(by=By.CLASS_NAME, value="sc-dkrFOg.erQOWi")
                button_clicked = False
                for i in range(len(buttons)):
                    for j in range(len(self.predictions[self.meciextras])):
                        self.activitatea_de_joc()
                        if str(self.predictions[self.meciextras][j]).split(" ")[0] + "\n" + \
                                str(self.predictions[self.meciextras][j]).split(" ")[1] in buttons[i].get_attribute("innerText"):
                            buttons[i].click()
                            self.prediction_to_remove = self.predictions[self.meciextras][j]
                            self.bets_counter += 1
                            button_clicked = True
                            break
                    if button_clicked:
                        break
                if not button_clicked:
                    self.counter += 1
                    self.bets_counter = 0
            case 3:
                self.placebet(username, password, procent_de_pariere_min, procent_de_pariere_max)
                if self.placed_bet:
                    self.bets_counter = 0
                    self.counter += 1

    def placebet(self, username, password, procent_de_pariere_min, procent_de_pariere_max):
        print("pun pariu")
        match self.placebet_counter:
            case 0:
                # check if user is loged in or get balance
                self.activitatea_de_joc()
                try:
                    self.balance = driver.find_element(by=By.CLASS_NAME, value="text.total-amount").get_attribute("innerText").split('.')[0]
                    self.placebet_counter += 1
                    self.procent_de_pariere = random.randint(procent_de_pariere_min, procent_de_pariere_max)
                except NoSuchElementException:
                    self.login_site_b(username, password)

            case 1:
                self.activitatea_de_joc()
                casutaBet = driver.find_element(by=By.CLASS_NAME,
                                                value=site_b_selector("mod-@UI-stake-input.mod-@UI-js-stake-input"))
                ActionChains(driver).move_to_element(casutaBet).click(casutaBet).perform()
                time.sleep(2)
                casutaBet.send_keys(str((int(self.procent_de_pariere) * int(self.balance)) / 1000))
                time.sleep(1)

                try:
                    self.activitatea_de_joc()
                    butonPariaza = driver.find_element(by=By.CLASS_NAME, value=site_b_selector("mod-@UI-betslip__place-bet-btn"))
                    while butonPariaza.get_attribute("innerText") == "Aprobati modificarea cotelor":
                        ActionChains(driver).move_to_element(butonPariaza).click(butonPariaza).perform()
                        time.sleep(3)
                    ActionChains(driver).move_to_element(butonPariaza).click(butonPariaza).perform()
                    time.sleep(7)
                    time_now = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')).split(" ")[1]
                    try:
                        if driver.find_element(by=By.CLASS_NAME, value="_10724").get_attribute(
                                "innerText") == "Fonduri insuficiente":
                            driver.find_element(by=By.CLASS_NAME, value="_7986f").click()
                            print("Fonduri insuficiente la ora: " + time_now)
                            self.placebet_counter = 0
                            self.go_to_sport_sites()
                    except NoSuchElementException:
                        print("Am pariat la ora: " + time_now)
                        self.placed_bet = True
                        self.predictions[self.meciextras].remove(self.prediction_to_remove)
                except NoSuchElementException:
                    self.end_of_function()

    def wait_seconds(self, min_sec: int, max_sec: int):
        time.sleep(random.randint(min_sec, max_sec))
        self.counter += 1
        """self.timer += 1
        print(self.timer)
        if self.timer / self.random_time == 1:
            self.timer = 0
            self.seconds_counter += 1
        if self.seconds_counter >= random.randint(min_sec, max_sec):
            self.seconds_counter = 0
            self.counter += 1"""

    def wait_seconds_in_bets(self, min_sec: int, max_sec: int):
        time.sleep(random.randint(min_sec, max_sec))
        self.bets_counter += 1
        """self.timer += 1
        if self.timer / self.random_time == 1:
            self.timer = 0
            self.seconds_counter += 1
        if self.seconds_counter >= random.randint(min_sec, max_sec):
            self.seconds_counter = 0
            self.bets_counter += 1"""

    def accept_gdpr(self):
        # self.gdpr_timer += 1
        # if self.gdpr_timer == 1:
        try:
            driver.find_element(by=By.ID, value="onetrust-accept-btn-handler").click()
            # self.gdpr_timer += 1
            # self.random_time = random.randint(4135740, 4135750)
            self.counter += 1
            time.sleep(random.randint(3, 6))
        except NoSuchElementException:
            self.counter += 1
            pass

        """if self.gdpr_timer / self.random_time == 1:
            self.gdpr_timer = 2
            self.seconds_counter += 1
        if self.seconds_counter >= random.randint(3, 6):
            self.seconds_counter = 0
            self.gdpr_timer = 0
            self.counter += 1"""

    def go_to_sport_sites(self):
        self.counter = 0
        self.what_to_to = self.visit_sport

    def main_loop(self, username, password, procent_de_pariere_min, procent_de_pariere_max):
        match self.what_to_to:
            case 0:
                self.extract_predictions()
            case 1:
                self.visit_sport_sites()
                # self.what_to_to += 1
            case 2:
                self.login_site_b(username, password)
            case 3:
                self.get_live_events()
            case 4:
                self.try_to_make_bets(self.liveEvents, username, password, procent_de_pariere_min,
                                      procent_de_pariere_max)
            case 5:
                if len(self.liveEvents) > 0:
                    self.what_to_to = self.try_to_make_bet
                else:
                    self.what_to_to += 1
            case 6:
                if '08:00:00' < datetime.datetime.now().strftime('%H:%M:%S') and not self.predictions_extracted:
                    self.__init__()
                    self.what_to_to = self.start_day
                if datetime.datetime.now().strftime('%H:%M:%S') < '08:00:00':
                    self.predictions_extracted = False
                if '08:00:00' < datetime.datetime.now().strftime('%H:%M:%S') < '23:34:32':
                    self.visit_sport_sites()
                    self.what_to_to = self.get_live_event


class SiteA:
    def __init__(self):
        self.site_url = required_env("SITE_A_URL")
        self.current_match_index = None
        self.selected_match_hrefs = None
        self.used_predictions = None
        self.live_multiple_bet_login = False
        self.multiple_bet_login = False
        self.live_bet_login = False
        self.oldtime = time.time()
        self.list_sport_sites: list = ["https://www.espn.com/", "https://www.eurosport.ro/",
                                       "https://www.cbssports.com/", "https://www.digisport.ro/",
                                       "https://www.sport.ro/", "https://www.gsp.ro/", "https://www.fanatik.ro/",
                                       "https://www.fanatik.ro/",
                                       "https://as.ro/"]
        self.predictions_list: list = []
        self.predictions_extracted = False
        self.all_predictions_extracted = False
        self.start_day = 0
        self.event_predicitons_list: list = []
        self.counter = 0
        self.no_of_sites_to_visit = 0
        self.sites_counter = 0
        self.run_while = False
        self.scroll_counter = 0
        self.timer = 0
        self.random_time = random.randint(362661, 401540)
        self.seconds_counter = 0
        self.function_to_execute = "do_nothing"
        self.liveEvents = []
        self.clicked_container = 0
        self.gdpr_timer = 0
        self.what_to_to = 0
        self.visit_sport = 1
        self.event_list_position = 0
        self.lovitura_de_start = "0"
        self.time_now = "0"
        self.bets_counter = 0
        self.meciextras = ""
        self.predictions = {}
        self.placebet_counter = 0
        self.check_login = False
        self.check_login_all = False
        self.check_login_multiple = False
        self.balance = 0
        self.prediction_to_remove = ""
        self.placed_bet = False
        self.over_goals_counter = 0
        self.repeat_try_make_bets = 0
        self.try_to_make_bet = 5
        self.try_to_placebet = 4
        self.get_live_event = 3
        self.procent_de_pariere = 30
        self.oldtime = time.time()
        self.live_matchList = []
        self.all_matchList = []
        self.homeTeam = ""
        self.awayTeam = ""
        self.forced_login = False
        self.forced_login_all = False
        self.all_day_matches = []
        self.firstbet = False
        self.start_time = 32400
        self.end_time = 84972
        self.total_interval_to_bet = 52472
        self.multiple_bets_per_day = random.randint(4, 10)
        self.interval_de_pariere_multiplu = int(self.total_interval_to_bet / self.multiple_bets_per_day)
        self.no_of_matches_on_ticket = 0
        self.cota_de_pariere = 0
        self.no_of_matches_added = 0
        self.multiple_counter = 0
        self.used_bets = {}
        self.number_of_live_bets_on_ticket = 0
        self.live_bets_placed = 0
        self.used_live_matches = []
        self.multiple_live_bets = random.randint(3, 6)
        self.multiple_live_bets_placed = 0
        self.forced_login_multiple_live_bets = False
        self.meciuri_negasite_in_predictii = 0
        self.firstrun = True
        self.predictions_initialized = False
        self.meciuri_negasite_de_vizitat = random.randint(16, 27)

        # apelăm direct inițializarea predicțiilor
        self.initialize_predictions()

    def initialize_predictions(self):
        if not self.predictions_initialized:
            from prepare_history_data import download_csvs, load_csvs
            from live_predictions import generate_league_predictions

            # descarcă CSV-urile dacă nu există
            download_csvs()
            print("Finish CSV\n")
            df_combined = load_csvs()
            print("CSV combined\n\n")
            leagues = df_combined['League'].unique()
            print("League combined\n\n")
            for league in leagues:
                df_league = df_combined[df_combined['League'] == league]
                preds = generate_league_predictions(df_league)
                self.predictions.update(preds)
            print("Finished predicts\n")
            self.predictions_initialized = True
            print("Predicții generate la inițializare.")
            # # Salvare predictions_dict în JSON
            # timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # filename = f"predictions_backup_{timestamp}.json"
            #
            # with open(filename, "w", encoding="utf-8") as f:
            #     json.dump(self.predictions, f, ensure_ascii=False, indent=4)

            # print(f"Predictions salvate în fișierul: {filename}")
            self.end_of_function()

    def wait_seconds(self, min_sec: int, max_sec: int):
        time.sleep(random.randint(min_sec, max_sec))
        self.counter += 1

    def parse_statistics(self, statistics_text: str):
        """
        Parsează blocul brut de statistici într-un dicționar.
        Returnează dict {nume_stat: (valoare_home, valoare_away)}.
        """
        lines = [l.strip() for l in statistics_text.splitlines() if l.strip()]
        stats = {}
        i = 0
        while i < len(lines):
            line = lines[i]

            # detectăm o cheie (linie care NU e doar cifră sau procent)
            if not line.replace("%", "").isdigit() and ":" not in line:
                key = line
                values = []

                j = i + 1
                while j < len(lines) and (lines[j].replace("%", "").isdigit() or ":" in lines[j]):
                    val = lines[j].replace("%", "").strip()
                    if val.isdigit():
                        values.append(int(val))
                    j += 1

                # completăm lipsurile (dacă e doar 1 valoare, punem 0 la cealaltă)
                if len(values) == 1:
                    values = (values[0], 0)
                elif len(values) >= 2:
                    values = (values[0], values[1])
                else:
                    values = (0, 0)

                stats[key] = values
                i = j
            else:
                i += 1
        print("Stats  is : {stats}\n")
        return stats

    def extract_live_data(self):
        """
        Extrage datele live pentru un meci:
        - echipele
        - scorul
        - statistici (cartonașe, cornere, posesie etc.)
        Returnează (home, away, score_home, score_away, stats_dict)
        """
        try:
            # Titlul meciului (ex: "Real Madrid vs Villarreal")
            match_title = driver.find_element(
                by=By.CLASS_NAME,
                value="mb-auto.mt-auto.text-primary.pr-2"
            ).get_attribute("innerText").strip()

            if not match_title or " vs " not in match_title:
                return "none", "none", "none", "none", {}

            home, away = [x.strip() for x in match_title.split(" vs ")]

            # Scorul live
            try:
                score_text = driver.find_element(
                    by=By.CLASS_NAME,
                    value="score-class"  # <- verifică clasa reală pentru scor
                ).get_attribute("innerText").strip()

                score_parts = score_text.split("-")
                score_home = int(score_parts[0].strip())
                score_away = int(score_parts[1].strip())
            except Exception:
                score_home, score_away = 0, 0

            # Statistici live
            stats_dict = {}
            try:
                stats_elements = driver.find_elements(
                    by=By.CLASS_NAME,
                    value="stat-class"  # <- verifică clasa reală pentru statistici
                )

                for elem in stats_elements:
                    try:
                        text = elem.get_attribute("innerText").strip()
                        # ex: "POSESIA MINGII\n55%\n45%"
                        lines = [l.strip() for l in text.split("\n") if l.strip()]
                        if len(lines) >= 3:
                            stat_name = lines[0]
                            val_home = int(lines[1].replace("%", "").strip())
                            val_away = int(lines[2].replace("%", "").strip())
                            stats_dict[stat_name] = (val_home, val_away)
                    except Exception:
                        continue
            except Exception:
                stats_dict = {}

            # Fallback: completăm cu valori default pentru lipsuri
            defaults = {
                "CARTONAȘE": (0, 0),
                "LOVITURI DE COLȚ": (0, 0),
                "POSESIA MINGII": (50, 50),
                "ȘUTURI PE POARTĂ": (0, 0),
                "LOVITURI LIBERE": (0, 0),
            }
            for key, val in defaults.items():
                if key not in stats_dict:
                    stats_dict[key] = val

            return home, away, score_home, score_away, stats_dict

        except Exception as e:
            print(f"[EROARE extract_live_data] {e}")
            return "none", "none", "none", "none", {}

    # def extract_live_data(self):
    #     """
    #     Extragere scor și statistici de pe pagina de live match.
    #     Returnează tuple: (home_team, away_team, score_home, score_away, stats_dict)
    #     """
    #     # Extragem numele echipelor
    #     meciextras = driver.find_element(by=By.CLASS_NAME, value="mb-auto.mt-auto.text-primary.pr-2").get_attribute(
    #         "innerText")
    #     home_team = meciextras.split(" vs ")[0].strip()
    #     away_team = meciextras.split(" vs ")[1].strip()
    #
    #     # Extragem scorul
    #     try:
    #         score_text = driver.find_element(by=By.XPATH,
    #                                          value='//*[@id="sportradar"]/div/div/div/div/div/div/div/div[2]/div[1]/div/div/div[2]/div[2]/div[2]').get_attribute(
    #             "innerText")
    #         score_lines = [line for line in score_text.splitlines() if line.strip().isdigit()]
    #         score_home, score_away = int(score_lines[0]), int(score_lines[1])
    #
    #         # Extragem statistici
    #         statistics_text = driver.find_element(by=By.XPATH,
    #                                               value='//*[@id="content1"]/div[2]/div/div/div/div/div/div[2]').get_attribute(
    #             "innerText")
    #         stats_dict = self.parse_statistics(statistics_text)  # parse_statistics din functii.py
    #     except NoSuchElementException:
    #         score_home, score_away, stats_dict = ("none", "none", "none")
    #         print("stats = " + stats_dict)
    #
    #     return home_team, away_team, score_home, score_away, stats_dict

    def update_predictions_for_match(self, home_team_input, away_team_input, score_home, score_away, stats_dict):
        """
        Actualizează predicțiile pentru un meci specific.
        Folosește fuzzy matching pentru a evita mismatch-ul echipelor.
        """
        # Creăm o listă temporară cu toate meciurile din predicții
        matches_df = pd.DataFrame([{'HomeTeam': k[0], 'AwayTeam': k[1]} for k in self.predictions.keys()])

        # Fuzzy match echipe
        home_team = process.extractOne(home_team_input, matches_df['HomeTeam'].unique())[0]
        away_team = process.extractOne(away_team_input, matches_df['AwayTeam'].unique())[0]

        # Actualizăm predicțiile folosind datele live
        updated_data = update_match_live(
            self.predictions,
            home_team,
            away_team,
            score_home=score_home,
            score_away=score_away,
            yellow_cards_home=stats_dict.get("CARTONAȘE", (0, 0))[0],
            yellow_cards_away=stats_dict.get("CARTONAȘE", (0, 0))[1],
            corners_home=stats_dict.get("LOVITURI DE COLȚ", (0, 0))[0],
            corners_away=stats_dict.get("LOVITURI DE COLȚ", (0, 0))[1],
            possession_home=stats_dict.get("POSESIA MINGII", (50, 50))[0],
            possession_away=stats_dict.get("POSESIA MINGII", (50, 50))[1],
            shots_on_target_home=stats_dict.get("ȘUTURI PE POARTĂ", (0, 0))[0],
            shots_on_target_away=stats_dict.get("ȘUTURI PE POARTĂ", (0, 0))[1],
            free_kicks_home=stats_dict.get("LOVITURI LIBERE", (0, 0))[0],
            free_kicks_away=stats_dict.get("LOVITURI LIBERE", (0, 0))[1]
        )

        return updated_data

    @staticmethod
    def is_youth_match(home_team, away_team):
        youth_suffixes = ["U19", "U20", "U21", "U18", "U17", "(F)", "(T)", "(R)"]
        for suffix in youth_suffixes:
            if suffix in home_team or suffix in away_team:
                return True
        return False

    def log_unmatched_match(self, home, away):
        with open("meciuri_fara_predictii.log", "a") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | {home} vs {away}\n")

    def find_match_in_predictions(self, home_name, away_name, threshold=70):
        """Caută o potrivire fuzzy în predicții fără inversarea echipelor și fără normalizare."""

        best_match = None
        best_score = 0

        for key in self.predictions.keys():
            home_pred, away_pred = key

            # calculăm scorurile fuzzy între echipe
            score_home = fuzz.token_sort_ratio(home_name, home_pred)
            score_away = fuzz.token_sort_ratio(away_name, away_pred)
            avg_score = (score_home + score_away) / 2

            if avg_score > best_score:
                best_score = avg_score
                best_match = key

        # acceptăm doar potrivirile bune (ambele echipe peste prag)
        if best_match and best_score >= threshold:
            # print(f"Potrivire fuzzy: {home_name} vs {away_name} ↔ {best_match} (score={best_score:.1f})")
            return best_match
        else:
            # print(f"Nicio potrivire fuzzy bună pentru {home_name} vs {away_name} (max={best_score:.1f})")
            self.log_unmatched_match(home_name, away_name)
            return None

    def end_of_function(self):
        self.counter = 0
        self.what_to_to += 1

    @staticmethod
    def conectare_simultana():
        try:
            if driver.find_element(by=By.CLASS_NAME, value="UOWHydxf8N799ddkqKfv.DTcxRd9Anyr7T0Fu2Dj2 nQyYnAoVRlyXs0PCS2kG"):
                driver.find_element(by=By.CLASS_NAME, value="lgqiZrfs_yKvFhA_LJ3W.ZDtvLoILpfc3vvX_TUZJ").click()
        except NoSuchElementException:
            pass

    @staticmethod
    def login_stats_site():
        username = os.environ.get("STATS_USERNAME")
        password = os.environ.get("STATS_PASSWORD")
        if not username or not password:
            raise RuntimeError(
                "Set STATS_USERNAME and STATS_PASSWORD in .env (see .env.example)."
            )

        try:
            driver.get(required_env("STATS_SITE_URL"))
            time.sleep(5)
            driver.find_element(by=By.CLASS_NAME, value="white.dBlock.linkBtn.dropDownMenu").click()
            time.sleep(2)
            driver.find_element(by=By.ID, value="username").click()
            time.sleep(1)
            for character in username:
                driver.find_element(by=By.ID, value="username").send_keys(character)
                # driver.find_element(by=By.CLASS_NAME, value="JwHSmjKp31hKtQ2IlhMo.aZUYEwdsDNr8rfFCLmPq").send_keys(character)
                time.sleep(random.uniform(0.3, 1))
            for character in password:
                driver.find_element(by=By.ID, value="password").send_keys(character)
                # driver.find_element(by=By.CLASS_NAME, value="JwHSmjKp31hKtQ2IlhMo.aZUYEwdsDNr8rfFCLmPq").send_keys(character)
                time.sleep(random.uniform(0.3, 1))
            driver.find_element(by=By.ID, value='password').send_keys(Keys.ENTER)
        except NoSuchElementException:
            pass

    def login_site_a(self, username, password):
        match self.counter:
            case 0:
                print("login site A")
                driver.get(self.site_url)
                self.counter += 1
            case 1:
                self.wait_seconds(3, 6)
            case 2:
                self.accept_gdpr()
            case 3:
                # self.activitatea_de_joc()
                # print("apas Conectare")
                # elementul = True
                # driver.find_element(by=By.XPATH, value="//button[contains(text(), 'Conectare')]").click()
                try:
                    driver.find_element(by=By.XPATH, value="//button[contains(text(), 'Conectare')]").click()
                    print("Am apasat Conectare")
                    self.counter += 1
                except NoSuchElementException:
                    # self.go_to_sport_sites()
                    if self.forced_login:
                        self.counter = 12
                        self.what_to_to = self.try_to_make_bet
                        self.forced_login = False
                    elif self.forced_login_all:
                        self.counter = 2
                        self.what_to_to = self.try_to_placebet
                        self.multiple_bet_login = False
                    elif self.forced_login_multiple_live_bets:
                        print("Sunt logat si ma duc la case 13 in multiple live bet")
                        self.counter = 13
                        self.what_to_to = 5
                        self.live_multiple_bet_login = False
                        self.forced_login_multiple_live_bets = False
                    else:
                        self.end_of_function()
            case 4:
                self.wait_seconds(3, 6)
            case 5:
                # self.activitatea_de_joc()
                """try:
                    driver.find_element(by=By.XPATH, value='//*[@id="VCG_R6F9kYhuQZ4BPMWm"]/div/div/div/div[2]/div/div/div/form/div[1]/div/div[1]').
                    click()
                    # driver.find_element(by=By.CLASS_NAME, value="JwHSmjKp31hKtQ2IlhMo.aZUYEwdsDNr8rfFCLmPq").click()
                    time.sleep(2)
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()"""
                driver.switch_to.frame(driver.find_element(by=By.CLASS_NAME, value="safe-top.safe-left.safe-right.safe-bottom.z-50"))
                print("am schimbat frame-ul")
                time.sleep(2)
                self.counter += 1
            case 6:
                # self.counter += 1
                self.wait_seconds(2, 4)
            case 7:
                # self.activitatea_de_joc()
                driver.find_element(by=By.NAME, value="username").click()
                time.sleep(1)
                for character in username:
                    driver.find_element(by=By.NAME, value="username").send_keys(character)
                    # driver.find_element(by=By.CLASS_NAME, value="JwHSmjKp31hKtQ2IlhMo.aZUYEwdsDNr8rfFCLmPq").send_keys(character)
                    time.sleep(random.uniform(0.3, 1))
                self.counter += 1
            case 8:
                self.wait_seconds(4, 7)
            case 9:
                # self.activitatea_de_joc()
                try:
                    driver.find_element(by=By.NAME, value='password').click()
                    self.counter += 1
                except NoSuchElementException:
                    self.go_to_sport_sites()
            case 10:
                self.wait_seconds(2, 4)
            case 11:
                # self.activitatea_de_joc()
                for character in password:
                    driver.find_element(by=By.NAME, value='password').send_keys(character)
                    time.sleep(random.uniform(0.3, 1))
                driver.find_element(by=By.NAME, value='password').send_keys(Keys.ENTER)
                print("M-am logat")
                self.counter += 1
            case 12:
                self.wait_seconds(10, 15)
            case 13:
                driver.switch_to.default_content()
                # driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[4]/div/div[1]/button[1]').click()
                try:
                    if driver.find_element(by=By.CLASS_NAME, value="DzZlniTTv89xm1yI7ttw.uj78_tOTUMlOuKc_EB53"):
                        driver.find_element(by=By.CLASS_NAME, value="OdUqUJ8BOQxVCMQtFE6x.fa.fa-times").click()
                except NoSuchElementException:
                    pass
                if self.forced_login:
                    self.counter = 12
                    self.what_to_to = self.try_to_make_bet
                    self.forced_login = False
                elif self.forced_login_all:
                    self.counter = 2
                    self.what_to_to = self.try_to_placebet
                    self.multiple_bet_login = False
                elif self.forced_login_multiple_live_bets:
                    print("m-am logat si ma duc la case 13 din multiple live bets")
                    self.counter = 13
                    self.what_to_to = 5
                    self.live_multiple_bet_login = False
                    self.forced_login_multiple_live_bets = False
                else:
                    self.end_of_function()

    def placebet(self, procent_de_pariere_min, procent_de_pariere_max):
        print("pun pariu")
        match self.placebet_counter:
            case 0:
                print("placebet - cazul 0")
                # check if user is loged in or get balance
                # self.activitatea_de_joc()
                self.check_login = True
                try:
                    self.balance = driver.find_element(by=By.CLASS_NAME,
                                                       value="text-gray-100.text-xl.semibold.text-right").get_attribute("innerText").split(' ')[0]
                    print(self.balance[4:])
                    self.placebet_counter += 1
                    # self.procent_de_pariere = random.randint(int(float(procent_de_pariere_min)), int(float(procent_de_pariere_max)))/100
                    self.check_login = False
                except NoSuchElementException:
                    if self.live_bet_login:
                        self.forced_login = True
                    elif self.multiple_bet_login:
                        self.forced_login_all = True
                    elif self.live_multiple_bet_login:
                        print("live_multiple_bet_login este True")
                        self.forced_login_multiple_live_bets = True
                        print("forced_login_multiple_live_bets setat pe True")
                    self.counter = 3
                    self.what_to_to = 2
                    pass

            case 1:
                print("plasez pariul")
                # verifica daca sunt meciuri suspendate in bilet
                pariu_acceptat = True
                suspendat_exists = False
                time_now = datetime.datetime.now().strptime(str(datetime.datetime.today().time()).split(".")[0], '%H:%M:%S')
                meciuri_plasate = driver.find_elements(by=By.CLASS_NAME,
                                                       value="flex.flex-col.py-4.px-2.mx-2.border-t.border-gray-800")
                print(len(meciuri_plasate))

                for i in range(len(meciuri_plasate)):
                    if "Suspendat" in meciuri_plasate[i].get_attribute("innerText"):
                        suspendat_exists = True
                        print("Exista meci suspendat")
                        break


                #  asteapta 5 minute sau sa isi revina cotele suspendate
                # while suspendat_exists:
                #     print("astept pana isi revin cotele sau 5 minute")
                #     meciuri_plasate = driver.find_elements(by=By.CLASS_NAME,
                #                                            value="flex.flex-col.py-4.px-2.mx-2.border-t.border-gray-800")
                #     time.sleep(random.randint(8, 16))
                #     for i in range(len(meciuri_plasate)):
                #         if "Suspendat" in meciuri_plasate[i].get_attribute("innerText"):
                #             suspendat_exists = True
                #             break
                #         else:
                #             suspendat_exists = False
                #     new_time_now = datetime.datetime.now().strptime(str(datetime.today().time()).split(".")[0],
                #                                            '%H:%M:%S')
                #     if int(str(new_time_now - time_now).split(":")[1][1]) * 60 > 300: # Ia in calcul si ora nu doar minutul
                #         print("Am asteptat 5 minute ca sa isi revina cotele")
                #         suspendat_exists = False
                #     time_now = new_time_now
                # sterge meciurile suspendate din bilet

                while suspendat_exists:
                    print("delete meci suspendat")
                    for i in range(len(meciuri_plasate)):
                        if "Suspendat" in meciuri_plasate[i].get_attribute("innerText"):
                            driver.find_element(by=By.XPATH,
                                                value=f'//*[@id="__layout"]/div/div[4]/div[3]/div/div/div[2]/div/div/div[2]/div/div[{i+1}]/div/div[2]/a/i').click()
                            time.sleep(random.randint(3, 6))
                            suspendat_exists = False
                            break
                    meciuri_plasate = driver.find_elements(by=By.CLASS_NAME,
                                                           value="flex.flex-col.py-4.px-2.mx-2.border-t.border-gray-800")
                    print("Verific daca mai sunt meciuri suspendate in bilet")
                    for i in range(len(meciuri_plasate)):
                        if "Suspendat" in meciuri_plasate[i].get_attribute("innerText"):
                            suspendat_exists = True
                            break
                #  daca mai exista meciuri in bilet introdu suma pentru pariu si apasa butonul de plasare pariu
                if len(driver.find_elements(by=By.CLASS_NAME,
                                            value="flex.flex-col.py-4.px-2.mx-2.border-t.border-gray-800")) > 0:

                    casutaBet = driver.find_element(by=By.CLASS_NAME,
                                                    value="self-center.text-primary-500.w-full.m-0.font-bold.text-center")
                    ActionChains(driver).move_to_element(casutaBet).click(casutaBet).perform()
                    print("am dat click in casuta pentru introducerea sumei")
                    time.sleep(2)
                    casuta_dupaClick = driver.find_element(by=By.CLASS_NAME,
                                                           value="text-white.bg-black.font-bold.rounded.flex.flex-col.place-content-center.h-8.w-full")
                    # ActionChains(driver).move_to_element(casuta_dupaClick).send_keys(
                    #     str(int(self.procent_de_pariere * int(float(self.balance[4:]))))).perform()
                    ActionChains(driver).move_to_element(casuta_dupaClick).send_keys(str(random.randint(7, 10))).perform() #Suma de pariat
                    print("am introdus suma pentru pariere")
                    time.sleep(1)
                    butonPariaza = driver.find_element(by=By.XPATH,
                                                       value='//*[@id="__layout"]/div/div[5]/div[3]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/a')
                    while "Acceptă" in butonPariaza.get_attribute("innerText"):
                        ActionChains(driver).move_to_element(butonPariaza).click(butonPariaza).perform()
                        print("Am aprobat modificarea cotelor.")
                        time.sleep(4)
                        butonPariaza = driver.find_element(by=By.XPATH,
                                                           value='//*[@id="__layout"]/div/div[5]/div[3]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/a')
                        print(butonPariaza.get_attribute("innerText"))
                    butonPariaza = driver.find_element(by=By.XPATH,
                                                       value='//*[@id="__layout"]/div/div[5]/div[3]/div/div/div[2]/div/div/div[3]/div/div/div[2]/div[2]/a')
                    if "Câștig -" not in butonPariaza.get_attribute("innerText") and "Plasează pariul" in butonPariaza.get_attribute("innerText"):
                        ActionChains(driver).move_to_element(butonPariaza).click(butonPariaza).perform()
                        print("Am apasat butonul de plasare pariu.")
                        print(butonPariaza.get_attribute("innerText"))
                        pariu_acceptat = False
                        time.sleep(random.randint(20, 30))
                    elif "Acceptă" in butonPariaza.get_attribute("innerText"):
                        ActionChains(driver).move_to_element(butonPariaza).click(butonPariaza).perform()
                        print("Am apasat butonul de plasare pariu din elif.")
                        print(butonPariaza.get_attribute("innerText"))
                        time.sleep(1)
                        try:
                            ActionChains(driver).move_to_element(butonPariaza).click(butonPariaza).perform()
                        except NoSuchElementException:
                            pass
                        pariu_acceptat = False
                        time.sleep(random.randint(20, 30))
                    else:
                        print("'Castig -' inca se gaseste in buton. fa ceva in legatura cu asta")
                        # sterge toate meciurile din bilet si ia-o de la capat
                        meciuri_plasate = driver.find_elements(by=By.CLASS_NAME,
                                                               value="flex.flex-col.py-4.px-2.mx-2.border-t.border-gray-800")
                        print(len(meciuri_plasate))

                        while len(meciuri_plasate) > 0:
                            driver.find_element(by=By.XPATH,
                                                value=f'//*[@id="__layout"]/div/div[4]/div[3]/div/div/div[2]/div/div/div[2]/div/div[1]/div/div[2]/a/i').click()
                            meciuri_plasate = driver.find_elements(by=By.CLASS_NAME,
                                                                   value="flex.flex-col.py-4.px-2.mx-2.border-t.border-gray-800")
                        print("am sters meciurile din ticket")
                        print(len(meciuri_plasate))
                        self.placebet_counter = 0
                        self.counter += 1
                    # verific daca pariul a fost acceptat
                    verificare_pariu_acceptat = 0
                    while not pariu_acceptat:
                        try:
                            print("Verific daca pariul a fost acceptat")
                            driver.find_element(by=By.XPATH,
                                                value='//*[@id="__layout"]/div/div[5]/div[3]/div/div/div[2]/div/div[1]/div[1]/div/div[1]/div[1]/p[1]')
                            pariu_acceptat = True
                            self.placed_bet = True
                            print("elimin selectiile din bilet")
                            driver.find_element(by=By.XPATH, value='//*[@id="__layout"]/div/div[5]/div[3]/div/div/div[2]/div/div[1]/div[2]/a[2]').click()
                            self.live_bets_placed = 0
                            time.sleep(random.randint(5, 9))
                        except NoSuchElementException:
                            pariu_acceptat = False
                            time.sleep(random.randint(20, 30))
                            verificare_pariu_acceptat += 1
                            if verificare_pariu_acceptat > 5:
                                break

                    if pariu_acceptat:
                        self.placebet_counter = 0
                        self.meciuri_negasite_in_predictii = 0
                        # self.counter += 1

                else:
                    print("Nu mai sunt meciuri in bilet -> toate au fost suspendate")
                    self.placebet_counter = 0
                    self.placed_bet = True
                    self.counter += 1
                    # self.end_of_function()

    def go_to_sport_sites(self):
        print("am intrat in go to sport sites")
        self.meciuri_negasite_in_predictii = 0
        self.counter = 0
        self.what_to_to = self.visit_sport

    def extract_predictions(self):
        self.login_stats_site()
        time.sleep(5)
        url = required_env("STATS_SITE_URL").rstrip("/") + "/matches"
        driver.get(url)
        time.sleep(5)
        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Today')]").click()
        time.sleep(6)
        i = 2
        stop_click = False
        try:
            while driver.find_element(by=By.CLASS_NAME, value="ui-show-more-matches") and not stop_click:
                print("butonul 'Load more matches' exista")
                matches_init = driver.find_elements(By.CLASS_NAME, 'team-item')
                # load_more_matches = driver.find_element(by=By.CLASS_NAME, value="ui-show-more-matches")
                ActionChains(driver).move_to_element(driver.find_element(by=By.CLASS_NAME, value="ui-show-more-matches")).perform()
                time.sleep(2)
                driver.execute_script('arguments[0].click()', driver.find_element(by=By.CLASS_NAME, value="ui-show-more-matches"))
                time.sleep(8)
                matches_final = driver.find_elements(By.CLASS_NAME, 'team-item')
                if len(matches_init) == len(matches_final):
                    stop_click = True
        except NoSuchElementException:
            pass

        # time.sleep(8)
        matches = driver.find_elements(By.CLASS_NAME, 'team-item')
        print(f"Număr de meciuri găsite: {len(matches)}")
        meci = 1

        for match in matches:
            teams = match.find_elements(By.CLASS_NAME, 'team-link')
            if len(teams) == 2:
                team_1 = teams[0].text.strip()
                team_2 = teams[1].text.strip()

                # Extragem cotele Over/Under
                print("extrag predictiile Under/Over pentru meciul : " + team_1 + f' Meciul cu numarul: {meci}')
                try:
                    over_1_5 = match.find_element(By.XPATH, f'//*[@id="content"]/div[3]/div[4]/div[4]/ul[1]/div[{i}]/div[2]/div[3]').text.strip()
                    over_2_5 = match.find_element(By.XPATH, f'//*[@id="content"]/div[3]/div[4]/div[4]/ul[1]/div[{i}]/div[2]/div[4]').text.strip()
                    over_0_5 = match.find_element(By.XPATH, f'//*[@id="content"]/div[3]/div[4]/div[4]/ul[1]/div[{i}]/div[2]/div[7]').text.strip()
                except Exception as e:
                    print(f"Eroare la extragerea cotelor pentru {team_1} vs {team_2}: {e}")
                    over_1_5 = over_2_5 = over_0_5 = "N/A"

                # creaza un dictionar cu cheia fiind numele home_team in care adauga o lista cu predictii
                new_list = []
                if float(str(over_1_5.split("%")[0])) >= 70:
                    new_list.append("Peste (1.5)")
                    new_list.append("Peste (1)")
                    new_list.append("Peste (1.25)")
                else:
                    # new_list.append("Sub (1.5)")
                    # new_list.append("Sub (1.25)")
                    new_list.append("Sub (2)")
                    new_list.append("Sub (2.25)")
                if float(str(over_2_5).split("%")[0]) >= 70:
                    new_list.append("Peste (2)")
                    new_list.append("Peste (2.25)")
                    new_list.append("Peste (2.5)")
                    new_list.append("Peste (1.75)")
                else:
                    # new_list.append("Sub (2.5)")
                    new_list.append("Sub (2.75)")
                    new_list.append("Sub (3)")
                    new_list.append("Sub (3.25)")
                # predictii[team_1] = new_list
                self.predictions[team_1] = new_list
                # print(f"{team_1} vs {team_2}")
                # print(f"Over 0.5: {over_0_5}")
                # print(f"Over 1.5: {over_1_5}")
                # print(f"Over 2.5: {over_2_5}")
                # print("-" * 40)
                i += 1
                meci += 1
        print("am extras predictiile")
        self.predictions_extracted = True
        if self.firstrun:
            self.firstrun = False
            self.what_to_to = 7
            self.counter =0
        else:
            self.end_of_function()
        print("Am extras " + str(len(self.predictions)) + " predictii!")


        # print("Astazi sunt: " + str(len(self.predictions)))

    def accept_gdpr(self):
        try:
            driver.find_element(by=By.ID, value="didomi-notice-agree-button").click()
            # self.gdpr_timer += 1
            # self.random_time = random.randint(4135740, 4135750)
            self.counter += 1
            time.sleep(random.randint(3, 6))
        except NoSuchElementException:
            self.counter += 1
            pass

    def visit_sport_sites(self):
        match self.counter:
            case 0:
                print("setez nr de site-uri")
                self.no_of_sites_to_visit = random.randint(1, len(self.list_sport_sites))
                print("Number of sites to visit = " + str(self.no_of_sites_to_visit))
                self.scroll_counter = 0
                self.sites_counter = 0
                self.counter += 1
                self.random_time = random.randint(4135740, 4135750)
                self.seconds_counter = 0
                self.meciuri_negasite_de_vizitat = random.randint(16, 27)
                print(self.meciuri_negasite_de_vizitat)
            case 1:
                # visit sport sites
                print("vizitez site")
                if self.sites_counter < self.no_of_sites_to_visit:
                    try:
                        driver.set_page_load_timeout(30)
                        driver.get(self.list_sport_sites[random.randint(0, len(self.list_sport_sites) - 1)])
                        time.sleep(random.randint(4, 8))
                    except TimeoutException:
                        print("⚠️ Timeout la încărcarea site-ului, încerc altul...")

                    try:
                        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Da, accept')]").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass
                    try:
                        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'Accept all')]").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass
                    try:
                        driver.find_element(by=By.ID, value="onetrust-accept-btn-handler").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass

                    try:
                        driver.find_element(by=By.XPATH, value="//*[contains(text(), 'ACCEPTA TOT')]").click()
                        time.sleep(random.randint(5, 12))
                    except NoSuchElementException:
                        pass
                    self.counter += 1
                else:
                    self.end_of_function()
            case 2:
                # scroll down page
                print("citesc site")
                for i in range(5):
                    driver.execute_script("window.scrollTo(0, window.scrollY +600)")
                    time.sleep(random.randint(8, 20))
                self.sites_counter += 1
                self.counter += 1
            case 3:
                if self.sites_counter < self.no_of_sites_to_visit:
                    self.counter = 1
                else:
                    self.random_time = random.randint(362661, 401540)
                    self.end_of_function()

    @staticmethod
    def log_used_prediction(match_id, prediction):
        log_file = "used_predictions.csv"
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header = ["timestamp", "match", "prediction"]

        # dacă fișierul nu există, îl creăm cu header
        try:
            with open(log_file, "x", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
        except FileExistsError:
            pass

        # scriem linia nouă
        with open(log_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([now, match_id, prediction])

    def get_live_events_and_make_bets(self, procent_de_pariere_min, procent_de_pariere_max):
        match self.counter:
            case 0:
                print("Get live events")
                driver.get(self.site_url)
                self.counter += 1
            case 1:
                self.wait_seconds(6, 12)
            case 2:
                print("check_popup")
                # self.check_for_popup()
                # self.activitatea_de_joc()
                self.counter += 1
            case 3:
                self.wait_seconds(3, 5)
            case 4:
                self.accept_gdpr()
            case 5:
                # self.activitatea_de_joc()
                driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[4]/div/div[1]/button[1]').click()
                # driver.find_element(by=By.CLASS_NAME,
                # value="w-full.py-4.block.focus:outline-none.border-b-2.text-gray-900.border-transparent.hover:border-primary-500.
                # hover:text-primary-500").click()
                 
                self.counter += 1
            case 6:
                self.wait_seconds(12, 18)
            case 7:
                print("case 7 - selectare meci valid din predicții (cu fuzzy)")

                seen_matches = set()  # pentru eliminarea duplicatelor
                valid_matches_elements = []  # lista finală de meciuri valide

                try:
                    eventlinks = driver.find_elements(By.CLASS_NAME, 'flex.justify-between.h-full')

                    for idx in range(len(eventlinks)):
                        try:
                            # re-fetch la fiecare pas pentru a evita elementele stale
                            eventlinks = driver.find_elements(By.CLASS_NAME, 'flex.justify-between.h-full')
                            elem = eventlinks[idx]

                            text = elem.get_attribute("innerText").strip()
                            lines = [l for l in text.split("\n") if l.strip()]
                            if len(lines) < 2:
                                continue

                            home = lines[0].strip()
                            away = lines[1].strip()
                            match_id = f"{home} vs {away}"

                            if match_id in seen_matches:
                                continue
                            seen_matches.add(match_id)

                            # filtrăm direct aici meciurile de tineret sau feminin
                            if self.is_youth_match(home, away):
                                print(f"Sarit peste meci de tineret/feminin: {match_id}")
                                continue

                            # verificăm în predicții folosind fuzzy
                            matched_key = self.find_match_in_predictions(home, away)

                            if matched_key:
                                valid_matches_elements.append((match_id, elem))

                        except StaleElementReferenceException:
                            print("Element stale, reîncerc pentru alt meci...")
                            continue
                        except Exception as e:
                            print(f"Nu am putut procesa elementul: {e}")
                            continue

                    if valid_matches_elements:
                        # alegem random un meci valid
                        match_id, selected_elem = random.choice(valid_matches_elements)
                        try:
                            selected_elem.click()
                            print(f"Am dat click pe meci random valid (fuzzy): {match_id}")
                            time.sleep(random.randint(3, 6))
                            self.counter += 1
                        except StaleElementReferenceException:
                            print(f"Element stale fix la click pentru {match_id}, sar peste.")
                    else:
                        print("Nu există meciuri noi valide în predicții (fuzzy). Merg la alte site-uri.")
                        self.go_to_sport_sites()

                except Exception as e:
                    print(f"[EROARE case 7] {e}")
                    self.end_of_function()
            case 8:
                print("case 8 - extrag meciul curent")
                try:
                    self.meciextras = driver.find_element(
                        by=By.CLASS_NAME,
                        value="mb-auto.mt-auto.text-primary.pr-2"
                    ).get_attribute("innerText").strip()

                    if self.meciextras:
                        self.counter += 1
                        print(self.meciextras)
                        self.homeTeam, self.awayTeam = self.meciextras.split(" vs ")

                        # if self.is_youth_match(self.homeTeam, self.awayTeam):
                        #     print(f"Meci de tineret detectat: {self.homeTeam} vs {self.awayTeam}, sărim peste.")
                        #     self.counter = 0
                        # else:
                        #     self.counter += 1

                        # dacă apare mesajul că nu există cote, resetăm
                        try:
                            if driver.find_element(by=By.CLASS_NAME, value="p-5.text-center.text-gray-700"):
                                self.counter = 0
                        except NoSuchElementException:
                            pass
                    else:
                        self.counter = 0
                except NoSuchElementException:
                    self.counter = 0
            case 9:
                print("case 9 - extrag predicții")
                self.event_predicitons_list = []

                home, away, score_h, score_a, stats = self.extract_live_data()
                if home == "none":
                    print("Nu am putut extrage date pentru " + self.meciextras)
                    self.meciuri_negasite_in_predictii += 1
                    self.counter = 0
                    return

                match_prediction = self.update_predictions_for_match(home, away, score_h, score_a, stats)
                if not match_prediction or 'probs_ou' not in match_prediction:
                    print(f"Nu există predicții valide pentru {home} vs {away}")
                    self.meciuri_negasite_in_predictii += 1
                    self.counter += 1
                    return

                # doar dacă avem predicții valide
                for line, prob_dict in match_prediction['probs_ou'].items():
                    if prob_dict['over'] >= 70:
                        self.event_predicitons_list.append(f"Peste ({line})")
                    elif prob_dict['under'] >= 70:
                        self.event_predicitons_list.append(f"Sub ({line})")

                print(f"Predicții generate pentru {home} vs {away}: {self.event_predicitons_list}")
                self.counter += 1

            case 10:
                # read Odds and place bet
                print("case 10")
                try:
                    # Deschidem secțiunea cu pariuri
                    driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="main_screen"]/div/div[3]/div/div/div[4]/p'
                    ).click() 
                    print(driver.find_element(
                        by=By.XPATH,
                        value='//*[@id="main_screen"]/div/div[3]/div/div/div[4]/p'
                    ).get_attribute("innerText"))

                    time.sleep(3)

                    odds_elements = driver.find_elements(
                        by=By.CLASS_NAME,
                        value="grid.gap-1.items-stretch.grid-cols-2"
                    )

                    if not odds_elements:
                        print(
                            f"[WARN] Nu există cote disponibile pentru {getattr(self, 'homeTeam', '?')} vs {getattr(self, 'awayTeam', '?')}")
                        self.counter = 0
                        return

                    if not isinstance(getattr(self, "used_predictions", None), set):
                        self.used_predictions = set()

                    if not isinstance(getattr(self, "used_live_matches", None), list):
                        self.used_live_matches = []

                    match_id = f"{self.homeTeam} vs {self.awayTeam}"
                    bet_placed = False

                    # extragem textul odds și împărțim pe linii
                    text_lines = odds_elements[0].get_attribute("innerText").split("\n")
                    lines_with_odds = []
                    i = 0
                    while i < len(text_lines) - 1:
                        pred = text_lines[i].strip()
                        try:
                            odd = float(text_lines[i + 1].strip())
                        except ValueError:
                            i += 1
                            continue
                        lines_with_odds.append((pred, odd))
                        i += 2

                    # verificăm fiecare predicție din event_predictions_list
                    for prediction in self.event_predicitons_list:
                        key = (match_id, prediction)
                        if key in self.used_predictions:
                            print(f"Predicția '{prediction}' pentru {match_id} a fost deja folosită, sar peste.")
                            continue

                        for pred_text, odd in lines_with_odds:
                            if prediction == pred_text and 1.70 <= odd <= 2.20:
                                try:
                                    driver.find_element(
                                        by=By.XPATH,
                                        value=f'//*[contains(text(), " {prediction} ")]'
                                    ).click()
                                    print(f"Am plasat pariul: {prediction} la {match_id} (cota {odd})")
                                    time.sleep(2)

                                    # salvăm perechea (meci, predicție)
                                    self.used_predictions.add(key)
                                    # self.used_live_matches.append(match_id)
                                    self.live_bets_placed += 1
                                    self.counter += 1
                                    bet_placed = True

                                    self.log_used_prediction(match_id, prediction)

                                    # închidem popup-ul pariului dacă există
                                    try:
                                        driver.find_element(by=By.CLASS_NAME, value="fa.fa-times").click()
                                        time.sleep(1)
                                    except NoSuchElementException:
                                        pass

                                    break
                                except ElementClickInterceptedException:
                                    print("Nu pot da click - butonul e inactiv (probabil gol). Reiau ciclul.")
                                    self.counter = 0
                                except NoSuchElementException:
                                    pass
                        if bet_placed:
                            break

                    if not bet_placed:
                        print(
                            f"Nicio predicție disponibilă cu cota 1.70-2.20 pentru {match_id}. Trec la următorul pas.")
                        self.counter = 13
                        time.sleep(2)

                except NoSuchElementException:
                    self.counter = 0

            case 11:
                self.live_bet_login = True
                if self.forced_login:
                    # self.placebet(procent_de_pariere_min, procent_de_pariere_max)
                    self.forced_login = False
                    self.live_bet_login = False
                    self.counter += 1
                else:
                    self.counter += 1
            case 12:
                if self.placed_bet:
                    self.placed_bet = False
                    self.counter += 1
                else:
                    self.placebet(procent_de_pariere_min, procent_de_pariere_max)
            case 13:
                # print("Verific daca a trecut o ora de la ultima apelare a predictiilor live")
                # if time.time() - self.oldtime >= 3660:
                #     self.oldtime = time.time()
                #     self.get_fixtures_live_all()
                self.end_of_function()

    def get_live_events_and_make_multiple_bets_on_ticket(self, procent_de_pariere_min, procent_de_pariere_max):
        match self.counter:

            case 0:
                print("Încep pariurile multiple pe ticket")
                self.number_of_live_bets_on_ticket = random.randint(3, 6)
                self.live_bets_placed = 0
                self.placed_bet = False
                self.used_live_matches = []
                self.selected_match_hrefs = []
                self.current_match_index = 0
                self.counter += 1

            case 1:
                print("Get live events")
                driver.get(self.site_url)
                self.counter += 1

            case 2:
                self.wait_seconds(6, 12)

            case 3:
                print("check_popup")
                # self.check_for_popup()
                self.counter += 1

            case 4:
                self.wait_seconds(3, 5)

            case 5:
                self.accept_gdpr()

            case 6:
                driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[4]/div/div[1]/button[1]').click()
                self.counter += 1

            case 7:
                print("case 7 - selectare meciuri multiple valide (cu fuzzy)")
                seen_matches = set()
                valid_matches_elements = []

                try:
                    eventlinks = driver.find_elements(By.CLASS_NAME, 'flex.justify-between.h-full')

                    for idx in range(len(eventlinks)):
                        try:
                            # re-fetch la fiecare pas pentru a evita elementele stale
                            eventlinks = driver.find_elements(By.CLASS_NAME, 'flex.justify-between.h-full')
                            elem = eventlinks[idx]

                            text = elem.get_attribute("innerText").strip()
                            lines = [l for l in text.split("\n") if l.strip()]
                            if len(lines) < 2:
                                continue

                            home = lines[0].strip()
                            away = lines[1].strip()
                            match_id = f"{home} vs {away}"

                            if match_id in seen_matches:
                                continue
                            seen_matches.add(match_id)

                            # filtrăm direct aici meciurile de tineret sau feminin
                            if self.is_youth_match(home, away):
                                print(f"Sarit peste meci de tineret/feminin: {match_id}")
                                continue

                            # verificăm în predicții folosind fuzzy
                            matched_key = self.find_match_in_predictions(home, away)

                            if matched_key:
                                valid_matches_elements.append((match_id, elem))

                        except StaleElementReferenceException:
                            print("Element stale, reîncerc pentru alt meci...")
                            continue
                        except Exception as e:
                            print(f"Nu am putut procesa elementul: {e}")
                            continue

                    if valid_matches_elements:
                        num_bets = min(self.number_of_live_bets_on_ticket, len(valid_matches_elements))
                        self.selected_match_hrefs = random.sample(valid_matches_elements, num_bets)
                        print(f"Meciuri selectate pentru bilet: {[m[0] for m in self.selected_match_hrefs]}")
                        self.current_match_index = 0
                        self.counter += 1
                    else:
                        print("Nu există meciuri valide. Merg la alte site-uri.")
                        # self.go_to_sport_sites()
                        self.end_of_function()

                except Exception as e:
                    print(f"[EROARE case 7] {e}")
                    # self.go_to_sport_sites()
                    self.end_of_function()

            case 8:
                print("case 8 - vizitarea meciurilor selectate")
                try:
                    if self.current_match_index < len(self.selected_match_hrefs):
                        match_id, href = self.selected_match_hrefs[self.current_match_index]
                        driver.get(href)
                        print(f"Vizitez meciul {match_id}")
                        time.sleep(random.randint(3, 6))
                        self.current_match_index += 1
                        self.counter += 1
                    else:
                        self.current_match_index = 0
                        self.counter = 11  # mergem la plasarea biletului

                except Exception as e:
                    print(f"[EROARE case 8] {e}")
                    self.counter = 7

            case 9:
                print("case 9 - extrag predicții pentru meciul curent")
                self.event_predicitons_list = []

                home, away, score_h, score_a, stats = self.extract_live_data()
                if home == "none" or stats == "none":
                    print(f"Nu am putut extrage date pentru {self.meciextras}")
                    self.meciuri_negasite_in_predictii += 1
                    self.counter = 7
                    return

                match_prediction = self.update_predictions_for_match(home, away, score_h, score_a, stats)
                if not match_prediction or 'probs_ou' not in match_prediction:
                    print(f"Nu există predicții valide pentru {home} vs {away}")
                    self.meciuri_negasite_in_predictii += 1
                    self.counter = 7
                    return

                for line, prob_dict in match_prediction['probs_ou'].items():
                    if prob_dict['over'] >= 70:
                        self.event_predicitons_list.append(f"Peste ({line})")
                    elif prob_dict['under'] >= 70:
                        self.event_predicitons_list.append(f"Sub ({line})")

                print(f"Predicții generate pentru {home} vs {away}: {self.event_predicitons_list}")
                self.counter += 1

            case 10:
                print("case 10 - plasare pariuri pe meciul curent")
                try:
                    driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[3]/div/div/div[4]/p').click()
                    time.sleep(2)

                    odds_elements = driver.find_elements(by=By.CLASS_NAME, value="grid.gap-1.items-stretch.grid-cols-2")
                    if not odds_elements:
                        print(f"[WARN] Nu există cote disponibile pentru {self.homeTeam} vs {self.awayTeam}")
                        self.counter = 7
                        return

                    for prediction in self.event_predicitons_list:
                        try:
                            if prediction in odds_elements[0].get_attribute("innerText"):
                                driver.find_element(by=By.XPATH,
                                                    value=f'//*[contains(text(), " {prediction} ")]').click()
                                print(f"Am plasat pariul: {prediction} la {self.homeTeam} vs {self.awayTeam}")
                                self.live_bets_placed += 1
                                self.used_live_matches.append(self.homeTeam)
                                time.sleep(1)
                                try:
                                    driver.find_element(by=By.CLASS_NAME, value="fa.fa-times").click()
                                    time.sleep(1)
                                except NoSuchElementException:
                                    pass
                                break
                        except Exception:
                            continue

                    if self.live_bets_placed < self.number_of_live_bets_on_ticket:
                        self.counter = 8  # mergem la următorul meci
                    else:
                        self.counter += 1

                except NoSuchElementException:
                    self.counter = 8

            case 11:
                print("case 11 - plasare bilet")
                if self.placed_bet:
                    self.placed_bet = False
                    self.counter += 1
                else:
                    self.placebet(procent_de_pariere_min, procent_de_pariere_max)

            case 12:
                print("case 12 - finalizare")
                self.live_bets_placed = 0
                self.multiple_live_bets_placed += 1
                self.used_live_matches = []
                self.selected_match_hrefs = []
                self.current_match_index = 0
                self.end_of_function()

    @staticmethod
    def minute_passed(oldepoch):
        if time.time() - oldepoch >= 3600:
            return True
        return None

    def extract_all_day_matches_and_place_bet(self):
        match self.counter:
            case 0:
                print("extrage toate meciurile care se joaca astazi")
                driver.get(self.site_url)
                self.counter += 1
            case 1:
                self.wait_seconds(3, 8)
            case 2:
                print("check_popup")
                # self.check_for_popup()
                # self.activitatea_de_joc()
                self.counter += 1
            case 3:
                self.wait_seconds(3, 5)
            case 4:
                self.accept_gdpr()
            case 5:
                all_buttons = driver.find_elements(by=By.CLASS_NAME, value="truncate.pl-2.flex-grow")
                all_buttons[0].click()
                self.counter += 1
            case 6:
                self.wait_seconds(3, 7)
            case 7:
                driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[3]/nav/button[1]').click()
                time.sleep(random.randint(3, 7))
                eventlinks = driver.find_elements(by=By.CLASS_NAME, value="h-full.flex.flex-row.items-center")
                if len(eventlinks) > 0:
                    eventlinks[random.randint(0, len(eventlinks) - 1)].click()
                    time.sleep(random.randint(3, 8))
                    self.counter += 1
                else:
                    self.go_to_sport_sites()
                    self.end_of_function()
            case 8:
                print("extrag meciul")
                self.meciextras = driver.find_element(by=By.CLASS_NAME, value="mb-auto.mt-auto.text-primary.pr-2").get_attribute("innerText")
                print(self.meciextras)
                if self.meciextras:
                    print(self.meciextras[1:])
                    self.homeTeam = self.meciextras[1:].split(" vs ")[0]
                    self.awayTeam = self.meciextras.split(" vs ")[1]
                    self.counter += 1
                    try:
                        if driver.find_element(by=By.CLASS_NAME, value="p-5.text-center.text-gray-700"):
                            self.counter = 0
                    except NoSuchElementException:
                        pass
                else:
                    self.counter = 0
            case 9:
                print("apas butonul de goluri")
                driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[3]/div/div[2]/div[5]/p').click()
            case 10:
                self.wait_seconds(3, 7)
            case 11:
                self.event_predicitons_list = []
                if self.homeTeam in self.predictions.keys():
                    self.event_predicitons_list = self.predictions[self.homeTeam]
            case 12:
                driver.find_element(by=By.XPATH, value='//*[@id="main_screen"]/div/div[3]/div/div/div[4]/p').click()
                time.sleep(2)
                odds = driver.find_elements(by=By.CLASS_NAME, value="grid.gap-1.items-stretch.grid-cols-2")
                for i in range(len(self.event_predicitons_list)):
                    if self.event_predicitons_list[i] in odds[0].get_attribute("innerText"):
                        try:
                            driver.find_element(by=By.XPATH, value='//*[contains(text(), " ' + self.event_predicitons_list[i] + ' ")]').click()
                            self.no_of_matches_added += 1
                            self.counter = 0
                            time.sleep(2)
                            try:
                                driver.find_element(by=By.CLASS_NAME, value="fa.fa-times").click()
                                time.sleep(1)
                            except NoSuchElementException:
                                pass
                            time.sleep(random.randint(2, 4))
                            # self.placebet(procent_de_pariere_min, procent_de_pariere_max)
                            break
                        except NoSuchElementException:
                            pass
            #     self.counter += 1
            # case 13:
            #     self.end_of_function()

    def reset_for_multiple_bet(self):
        self.firstbet = True
        # self.multiple_bet(procent_de_pariere_min, procent_de_pariere_max)
        self.multiple_bets_per_day -= 1
        self.start_time = datetime.datetime.now().time().hour * 3600 + datetime.datetime.now().time().minute * 60 + datetime.datetime.now().time().second
        self.interval_de_pariere_multiplu = int((self.interval_de_pariere_multiplu - self.start_time) / self.multiple_bets_per_day)
        self.end_of_function()

    def check_if_multiple_bet_is_needed(self):
        # functia verifica daca este necesar sa se plaseze un pariu multiplu
        # intr-o rulare de 24h(ON+OFF) SW va plasa intre 4 si 6 pariuri cu meciuri multiple
        # plasarea de pariu multiplu va fi facuta la intervale de timp random pe parcursul unui cicle de rulare
        print("verific daca este necesar un pariu multiplu")
        time_now = datetime.datetime.now().time().hour * 3600 + datetime.datetime.now().time().minute * 60 + datetime.datetime.now().time().second
        if time_now - self.start_time < self.interval_de_pariere_multiplu and not self.firstbet:
            self.reset_for_multiple_bet()
        elif time_now - self.start_time > self.interval_de_pariere_multiplu and not self.firstbet:
            self.reset_for_multiple_bet()
        elif self.firstbet:
            if time_now - self.start_time > self.interval_de_pariere_multiplu:
                self.reset_for_multiple_bet()
            elif time_now - self.start_time < random.randint(self.start_time, self.interval_de_pariere_multiplu):
                self.reset_for_multiple_bet()
            else:
                self.what_to_to += 1
                self.end_of_function()
        else:
            self.what_to_to += 1
            self.end_of_function()

    def multiple_bet(self, procent_de_pariere_min, procent_de_pariere_max):
        # functia va plasa un pariu multiplu
        # biletul trebuie sa contina intre 4 si 10 meciuri
        # biletele jucate nu trebuie sa contina aceleasi meciuri
        match self.multiple_counter:
            case 0:
                self.no_of_matches_on_ticket = random.randint(3, 8)
                self.cota_de_pariere = random.randint(50, 60)
                self.multiple_counter += 1
            case 1:
                if self.no_of_matches_added < self.no_of_matches_on_ticket:
                    self.extract_all_day_matches_and_place_bet()
                else:
                    self.multiple_counter += 1
            case 2:
                self.multiple_bet_login = True
                if self.forced_login_all:
                    # self.placebet(procent_de_pariere_min, procent_de_pariere_max)
                    self.forced_login_all = False
                    self.multiple_bet_login = False
                    self.multiple_counter += 1
                else:
                    self.multiple_counter += 1
                    # self.placebet(procent_de_pariere_min, procent_de_pariere_max)
            case 3:
                if self.placed_bet:
                    self.placed_bet = False
                    self.multiple_counter += 1
                else:
                    self.placebet(procent_de_pariere_min, procent_de_pariere_max)
            case 4:
                self.multiple_counter = 0
                self.end_of_function()

    def main_loop(self, username, password, procent_de_pariere_min, procent_de_pariere_max):
        match self.what_to_to:
            case 0:
                print("start case00000000000000000\n\n")
                # self.what_to_to += 1
                self.predictions_initialized = False
                # apelăm direct inițializarea predicțiilor
                self.initialize_predictions()
                print("11111111111111111111111111111111111\n")
                self.extract_predictions()
            case 1:
                self.visit_sport_sites()
                print("Vizitez site-urile de sport")
                self.what_to_to += 1
            case 2:
                print("login7777777777777777777777777777777777777")
                self.login_site_a(username, password)
                # self.what_to_to += 1
            case 3:
                # self.check_if_multiple_bet_is_needed()
                self.what_to_to += 1
            case 4:
                # self.multiple_bet(procent_de_pariere_min, procent_de_pariere_max)
                self.what_to_to += 1
            case 5:
                self.get_live_events_and_make_bets(procent_de_pariere_min, procent_de_pariere_max)
                # self.get_live_events_and_make_multiple_bets_on_ticket(procent_de_pariere_min, procent_de_pariere_max)
                # self.what_to_to += 1
            case 6:
                # if self.multiple_live_bets_placed < self.multiple_live_bets:
                #     self.get_live_events_and_make_multiple_bets_on_ticket(procent_de_pariere_min, procent_de_pariere_max)
                # else:
                #     self.what_to_to += 1
                self.what_to_to += 1
            case 7:
                # now = datetime.now().time()
                now = datetime.datetime.now().time()

                if now > datetime.time(12, 0, 0) and not self.predictions_initialized:
                    print("Reset și reinițializare după ora 12.")
                    self.__init__()
                    self.what_to_to = self.start_day

                elif now < datetime.time(12, 0, 0):
                    print("E mai devreme de ora 12. Aștept...")
                    self.predictions_initialized = False
                    self.what_to_to = 7
                    time.sleep(60)  # verifică din minut în minut

                elif datetime.time(12, 0, 0) < now < datetime.time(23, 0, 0):
                    print("Interval activ (12-22). Sunt in bucla zilnică.")
                    self.what_to_to = 2

                elif now > datetime.time(23, 0, 0):
                    print("După 23:00. Botul intră în standby până mâine.")
                    self.what_to_to = 7
                    time.sleep(300)  # doarme 5 minute în standby

