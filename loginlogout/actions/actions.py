from gevent.subprocess import value
from pyrsistent import optional
from rasa_sdk.forms import REQUESTED_SLOT, FormAction
from rasa_sdk import Tracker, Action, FormValidationAction
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime, date
from rasa_sdk.events import SlotSet, EventType
from spacy.vocab import Vocab
from rasa_sdk.types import DomainDict
from spacy.language import Language
from rasa_sdk.events import FollowupAction, AllSlotsReset
# from rasa.core.trackers import DialogueStateTracker
import datetime as dt
import parsedatetime as pdt
from datetime import date, timedelta
from urlvalidator import URLValidator, ValidationError
from rasa_sdk.events import UserUtteranceReverted
import calendar
import requests
import dateparser
import pprint
import json
import xlrd
import re
import time
# from cdifflib import CSequenceMatcher

global affirm_deny_button,add_TTE_form_slot
affirm_deny_button = [{"title":"Yes","payload":"yes"},{"title":"No","payload":"no"}]
global notify_button
notify_button = [{"title":"Request for New Task","payload":"request for new task"}]
add_TTE_form_slot = []


global EMP_ID
cal = pdt.Calendar()
EMP_ID = 0         #### please uncomment it after testing it shoulb be 0
# EMP_ID = 3           ############## delete this after testing 
global Training_list_form_slot
Training_list_form_slot = []
global wrong_attempt
wrong_attempt = 0
global wrong_trainees_attempt,wrong_trainees_for_request_attempt,wrong_number_of_trainee_for_request
global wrong_number_of_trainee_for_request_attempt,wrong_ordinal1_attempt,wrong_ordinal2_attempt, wrong_status_attempt, wrong_training_type_attempt
wrong_status_attempt = 0
wrong_trainees_for_request_attempt = 0
wrong_training_type_attempt = 0
wrong_trainees_attempt = 0
wrong_number_of_trainee_for_request_attempt = 0
wrong_number_of_trainee_attempt = 0
wrong_ordinal1_attempt = 0
wrong_ordinal2_attempt = 0
global wrong_emp_code_count
wrong_emp_code_count = 0
global wrong_password_attempt
wrong_password_attempt = 0
global wrong_other_emp_code_attempt
wrong_other_emp_code_attempt = 0
global wrong_start_date_attempt, wrong_end_date_attempt, wrong_leave_type_attempt, wrong_hand_over_Employee
wrong_start_date_attempt = 0
wrong_end_date_attempt = 0
wrong_leave_type_attempt = 0
wrong_hand_over_Employee = 0
global wrong_name2_attempt
wrong_name2_attempt = 0
global wrong_separate_detail_attempt
wrong_separate_detail_attempt = 0
wrong_other_emp_code_attempt = 0
wrong_separate_detail_attempt = 0
global wrong_emp_code1_attempt
wrong_emp_code1_attempt = 0
global wrong_ordinal_attempt, wrong_command_attempt
wrong_ordinal_attempt = 0
wrong_command_attempt = 0
global wrong_num_of_month_attempt, wrong_payslip_month_attempt, wrong_payslip_months_attempt
wrong_num_of_month_attempt = 0
wrong_payslip_month_attempt = 0
wrong_payslip_months_attempt = 0
val1 = 0
other_emp_code = []
LIST_LR_ID = []
global emp_code_collect_form_slots
emp_code_collect_form_slots = []
lr_id_slot = []
id = ['lr_id1']
leave_days = 0
count = 0
# list of required slots
required_slots_list = ["start_date",
                       "end_date",
                       "leave_type",
                       "purpose",
                       "hand_over_Employee",
                       "knowledge_summary"
                       ]

# "http://mindsconnect.omfysgroup.com" #Prod
# mindsconnect_url = "http://103.109.13.198/MINDSCONNECT" # https://uat-java.omfysgroup.com/MINDSCONNECT/
API_URL_Django = "http://13.127.186.145:8000"
API_URL_Flask = "http://43.231.254.81:5888"
employee_last_name_globally = ""
# mindsconnect_url = "http://uat.omfysgroup.com/MINDSCONNECT"
# mindsconnect_url = "http://uat.omfysgroup.com/MINDSCONNECT_API"
mindsconnect_url = "https://demo.omfysgroup.com/mindsconnectleapi"
project_module_url = "http://uat.omfysgroup.com/project_mngt"
# --------------------------------------------------------------- Project Module ----------------------------------------------------------------
# maintasks = ["deployment of nova using docker",'hr da skill development in nova', 'marketing digital assistant alan development', 'project management da skill in nova']
# s1 = "project managemnt da skill maintask"
def get_best_match(task_predictedBy_rasa,dictonary_of_predefindtask_name_id):
#   if any(exe in task_predictedBy_rasa for exe in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]):
#     project_id = "miscellaneous task"
#     selected_project_name = "Miscellaneous Tasks"
#     return project_id , selected_project_name
#   else:
    list_of_predefind_taskId = list(dictonary_of_predefindtask_name_id.values())  
    list_of_predefindtask = list(dictonary_of_predefindtask_name_id.keys())
    task_predictedBy_rasa = task_predictedBy_rasa  
    confidence_percent =[]
    for task in list_of_predefindtask:
        s = CSequenceMatcher(lambda x: x == " ",task_predictedBy_rasa.lower(),task.lower())
        confidence_percent.append(round(s.ratio()*100, 2))
    print ("confidence percentage with tasks", confidence_percent)
    #   max_match_index = confidence_percent.index(max(confidence_percent)) if max(confidence_percent) >70 else ''
    max_match_index = confidence_percent.index(max(confidence_percent)) 
    task_name = list_of_predefindtask[max_match_index] 
    task_id = list_of_predefind_taskId[max_match_index]
    print(confidence_percent.index(max(confidence_percent)))  ####### get index of max percentage
    print(list_of_predefindtask[max_match_index])
    return task_id, task_name

class UserLoginForm(FormValidationAction):
    
    def name(self):
        return "validate_user_login_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside validate user login form required slot")
        global login_slot
        login_slot = ["emp_code","password"]
        return login_slot

    def validate_emp_code(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of emp_code ', value)
        #print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        response = requests.get(
            '{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, value))

        print('emp code response is ', response.json())
        global wrong_emp_code_count
        data = response.json()
        
        if data != None:
            
            global EMP_ID
            EMP_ID = str(data["jd"]['emp_id']['emp_id'])
            print('EMP_ID from validate ', EMP_ID)

            global employee_first_name_globally
            employee_first_name_globally = str(data["jd"]['emp_id']['emp_first_name'])
            print('Employee first name ', str(data["jd"]['emp_id']['emp_first_name']))

            global employee_last_name_globally
            employee_last_name_globally = str(data["jd"]['emp_id']['emp_last_name'])
            print('Employee last name ', str(data["jd"]['emp_id']['emp_last_name']))
            return {'emp_code': value}

        else:
            dispatcher.utter_template('utter_wrong_emp_code', tracker)
            return {"emp_code": None}

    def validate_password(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        #print('validate value of password  ', value)
        #print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        global wrong_password_attempt, login_slot

        response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, tracker.get_slot('emp_code'), value))
        data = response.json()
        print("login data;",data)
        if data != None :
            try:
                if data["errorCode"]==208 and data['errorMsg'] == "Failed." :

                    #print("password not matched")
                    wrong_password_attempt = wrong_password_attempt + 1
                    # dispatcher.utter_template('utter_wrong_password', tracker)
                    dispatcher.utter_message("You have entered wrong password")
                    return {"password": None}
            except:
                print("I am in except loop password matched")
                wrong_password_attempt = 0
                return {"password": value}
                
        elif wrong_password_attempt < 3:
            print("wrong_password_attempt", wrong_password_attempt)
            wrong_password_attempt = wrong_password_attempt + 1
            dispatcher.utter_message("You have entered wrong password")
            return {"password": None}
        else:
            login_slot = []
            wrong_password_attempt = 0
            dispatcher.utter_message("Login failed. You reached to maximum login limit.")
            return self.deactivate()

class ActionUserLogin(Action):
    
    def name(self):
        return "action_user_login_form_submit"

    def run(self, dispatcher, tracker, domain):
        
        global login_slot
        global EMP_ID,EMP_name,EMP_last_name
        
        try:
            
            print("Inside user login submit")
            emp_code = tracker.get_slot('emp_code')
            password = tracker.get_slot('password')
            response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, tracker.get_slot('emp_code'),tracker.get_slot('password')))
            data = response.json() 
            if len(login_slot)> 0 and data != None:
                response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, tracker.get_slot('emp_code')))
                data = response.json()
                EMP_name = str(data["jd"]['emp_id']['emp_first_name'])
                EMP_last_name = str(data["jd"]['emp_id']['emp_last_name'])
                print(EMP_name)
                global email_id1
                email_id1 = str(data["jd"]['emp_id']['email'])
                dispatcher.utter_message(f"employee code is {emp_code} and password is {password}")
                dispatcher.utter_message("Hi {} ".format(EMP_name))
                dispatcher.utter_template('utter_help_user', tracker)
                return []
            
            else:
            
                dispatcher.utter_template("utter_greet",tracker)
                return [SlotSet('emp_code', None), SlotSet('password', None)]
        
        except:
        
            dispatcher.utter_template("utter_greet",tracker)
            return [SlotSet('emp_code',None),SlotSet('password',None)]
        

class ActionRestart(Action):
    
    def name(self):
        return "action_restart"

    def run(self, dispatcher, tracker, domain):

        intent = tracker.latest_message['intent'].get('name')
        print(intent,"-------------")
        if intent == "logout":
            print("Inside action restart")
            dispatcher.utter_message("Successfully logged out!")
            return [AllSlotsReset()] 
        elif intent == "restart":
            print("Mohini here")
            dispatcher.utter_template('utter_greet',tracker)
            return [AllSlotsReset()]  

# while visiting to the main menu check for login credentials
class ActionCheckLoggedForMainMenu(Action):
    def name(self):
        return 'action_check_logged_for_main_menu'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        #print("employee code is", emp_code)
        #print("password is", password)

        intent = tracker.latest_message['intent'].get('name')

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            try:
                if emp_code  == " " and password  == " ":
                    raise Exception('I know Python!')

                if emp_code is None and password is None:
                    raise Exception('I know Python!')
                print("below if statement")
                dispatcher.utter_template("utter_help_user_after_loggedin", tracker)
                
 
            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]