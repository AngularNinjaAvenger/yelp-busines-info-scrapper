import requests, openpyxl, bs4, re, time,json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
class Gen_Clients:
    def __init__(self):
        self.loaded = False
        self.facebook_result = []
        self.twitter_result = []
        self.linkedin_result = []
        self.email_result = []
        self.browser = None
        self.lastStopped = 0
        self.offset=0
        self.last_offset_temp = 0
        self.options={
            "facebook":1,
            "twitter":1,
            "email":1
        }
    def generate(self):
        # chromedriver = 'C:/users/angular_nija_avenger/downloads/chromedriver'
        # browser = webdriver.Chrome(chromedriver)
        # self.browser = browser
        result = {
        	"res":[]
        }
        self.country=input("Enter the country:  ")
        self.state=input("Enter the State:  ")
        self.nitch=input("Enter the Nitch:  ")
        get_last_stopped=input("last stopped:  ")
        try:
            self.lastStopped = int(get_last_stopped)
        except:
            print("no last time good")
        
        self.offset = 0
        try:
            while self.offset <= 999:
                time.sleep(5)
                print(f"....{self.offset}")
                business = self.get_business()
                for index in business:
                    business={
                    "name":index["name"],
                    "url":index["url"],
                    "review_count":index["review_count"],
                    "rating":index["rating"],
                    "phone_number":index["phone"],
                    "image_url":index["image_url"],
                    "phone_number":index["display_phone"],
                    "location":index["location"]["city"]
                    }
                    result["res"].append(business)
                self.offset+=50
        except:
            print("business not up to 1000")
        
        
        email = self.get_email()
        twitter = self.get_twitter()
        facebook = self.get_facebook()
        linkedin = self.get_linkedin()
        for i in range(len(result["res"])):
            if i < self.lastStopped and self.lastStopped > 1:
                if not self.loaded:
                    self.load()
                    self.loaded = True
                    i = self.lastStopped
            business = result["res"][i]
            yelp_url = business["url"]
            print(yelp_url)
            try:
                print("checking if business has a website")
                url = self.get_website_url(yelp_url)
            except:
                print("they dont hacve a website keep them in another sheet")
            if url:
                business["website"]=url
                print("found thier website adding it to thier info")
            else:
                """
                PUT PEOPLE THAT DONT HAVE THIER WEBSITE IN ANOTHER SPREAD SHEET    
                """
                continue
            bus = business["website"]
            website = bus
            print(f"{website}  <---this is thier website")
            website_code = str(self.get_site_code_bs4(website))
            print("gotten thier website code")
            if len(website_code)<100 and type(website_code) == str:
                print("thier website code is too small let try sel again")
                website_code = self.get_site_code_sel(website)
            
            f_s = facebook.search(website_code)
            t_s  = twitter.search(website_code)
            e_s = email.search(website_code)
            l_s = linkedin.search(website_code)
            print("searching forr thier social links we regex")
            if f_s and f_s.group(0):
                business["contact_mf"] = "FACEBOOK"
                business["contact_df"] = f_s.group(0)
                self.facebook_result.append(business)
            if t_s and t_s.group(0):
                business["contact_mt"] = "TWITTER"
                business["contact_dt"] = t_s.group(0)
                self.twitter_result.append(business)
            if e_s and e_s.group(0):
                business["contact_me"] = "EMAIL"
                business["contact_de"] = e_s.group(0)
                self.email_result.append(business)
            if l_s and l_s.group(0):
                business["contact_ml"] = "LINKEDIN"
                business["contact_dl"] = l_s.group(0)
                self.linkedin_result.append(business)
            print(len(self.facebook_result),"<----facebook")
            print(len(self.twitter_result),"<----twitter")
            print(len(self.email_result),"<----email")
            print(len(self.linkedin_result),"<----linkedin")
            print(f"{i} <--- this is the index")
            if i % 20 == 0 and i > 1:
                print(" ")
                print(f"THIS IS THE LAST TIMETHAT IT WAS FIELD TO THE SHEET {i}")
                print(" ")
                self.fill_sheet()
        self.fill_sheet()
    def load(self):
        self.facebook_result = pd.DataFrame.read_excel(f"fb_{self.country}_{self.state}_{self.nitch}_leads.xlsx","Sheet1")
        self.twitter_result = pd.DataFrame.read_excel(f"tw_{self.country}_{self.state}_{self.nitch}_leads.xlsx","Sheet1")
        self.email_result = pd.DataFrame.read_excel(f"em_{self.country}_{self.state}_{self.nitch}_leads.xlsx","Sheet1")
        self.linkedin_result = pd.DataFrame.read_excel(f"ln_{self.country}_{self.state}_{self.nitch}_leads.xlsx","Sheet1")

    def fill_sheet(self):
        self.country
        self.state
        self.nitch
        f = pd.DataFrame(self.facebook_result)
        t = pd.DataFrame(self.twitter_result)
        e = pd.DataFrame(self.email_result)
        l = pd.DataFrame(self.linkedin_result)
        f_r = f[["name","url","review_count","rating","phone_number","image_url","phone_number","location","contact_mf","contact_df"]]
        t_r = t[["name","url","review_count","rating","phone_number","image_url","phone_number","location","contact_mt","contact_dt"]]
        e_r = e[["name","url","review_count","rating","phone_number","image_url","phone_number","location","contact_me","contact_de"]]
        l_r = l[["name","url","review_count","rating","phone_number","image_url","phone_number","location","contact_me","contact_de"]]
        f_r.to_excel(f"fb_{self.country}_{self.state}_{self.nitch}_leads.xlsx",sheet_name="Sheet1")
        t_r.to_excel(f"tw_{self.country}_{self.state}_{self.nitch}_leads.xlsx",sheet_name="Sheet1")
        e_r.to_excel(f"em_{self.country}_{self.state}_{self.nitch}_leads.xlsx",sheet_name="Sheet1")
        l_r.to_excel(f"ln_{self.country}_{self.state}_{self.nitch}_leads.xlsx",sheet_name="Sheet1")
        print("DONE")
    def get_business(self):
        url = "https://api.yelp.com/v3/businesses/search"
        api_key = "jIyTUl-rkQSMkMTQOMfhDi50RnBGFgQ8tGsnVV_GSRbST7A9gyGdRuOdF_kNuYSIKh2Iq3ofjwbDazExWARnNbW5T8W0XZb1dw3mrXd1BS1IMm-RSZYMQj6S2h1DXXYx"
        print("sending request")
        res = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key,
            },
            params={
                "term": self.nitch,
                "location": self.state,
                "limit": 50,
                "offset":self.offset,
                "sortby": "best_match",  # best_match, rating, review_count
            },
        )
        return res.json()["businesses"]
    def get_site_code_sel(self,site):
        print("trying with sel")
        x = self.browser.get('https://' + site)
        delay = 5 # seconds
        try:
            myElem = WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#section-title > div > h1')))
            return self.browser.page_source
        except TimeoutException:
            if self.browser.page_source:
                return self.browser.page_source
            return "no code found"

    def get_site_code_bs4(self,site):
        print("trying to get thier website code")
        url= 'https://' + site
        try:
            res = requests.get(url,{"accepts":"text/html"})
            soup = bs4.BeautifulSoup(res.text,'html.parser')
            store = soup.select("html")
            if store:
                print("gotten with bs4")
                return store[0]
            else:
                return False
        except:
            print("couldnotfind with bs4 want tot try selenium")
            return self.get_site_code_sel(site)

    def get_website_url(self,url):
        res = requests.get(url,{"accepts":"text/html"})
        soup = bs4.BeautifulSoup(res.text,'html.parser')
        try:

            store = soup.select("#wrap > div.main-content-wrap.main-content-wrap--full > div > div.lemon--div__373c0__1mboc.spinner-container__373c0__N6Hff.border-color--default__373c0__2oFDT > div.lemon--div__373c0__1mboc.u-space-t3.u-space-b6.border-color--default__373c0__2oFDT > div > div > div.lemon--div__373c0__1mboc.stickySidebar--heightContext__373c0__133M8.tableLayoutFixed__373c0__12cEm.arrange__373c0__UHqhV.u-space-b6.u-padding-b4.border--bottom__373c0__uPbXS.border-color--default__373c0__2oFDT > div.lemon--div__373c0__1mboc.stickySidebar--fullHeight__373c0__1szWY.arrange-unit__373c0__1piwO.arrange-unit-grid-column--4__373c0__3oeu6.border-color--default__373c0__2oFDT > div > div.lemon--div__373c0__1mboc.stickySidebar__373c0__3PY1o.border-color--default__373c0__2oFDT > section:nth-child(3) > div > div:nth-child(1) > div > div.lemon--div__373c0__1mboc.arrange-unit__373c0__1piwO.arrange-unit-fill__373c0__17z0h.border-color--default__373c0__2oFDT > a")
            url = store[0].text
            if "/" in url:
                url = url[0:url.find("/")]
            return url
        except:
            return False
    def get_email(self):
        client_email = re.compile(u"([a-z0-9!#$%&'*+\/=?^_`{|.}~-]+@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)", re.IGNORECASE)
        return client_email
    def get_twitter(self):
        twitter_search = re.compile(r"twitter.com/\w+", re.IGNORECASE)
        return twitter_search
    def get_facebook(self):
        facebook_search = re.compile(r"facebook.com/\w+", re.IGNORECASE)
        return facebook_search
    def get_linkedin(self):
        linkedin_search = re.compile(r"linkedin.com/company/\w+", re.IGNORECASE)
        return linkedin_search
 

gen = Gen_Clients()
# gen.fill_correct_spread_sheet(store)
print("""
WELCOME TO YELP LEAD GET READY TO GENERATE LEADS FOR YOUR BUSINESS
""")
print(gen.generate())
