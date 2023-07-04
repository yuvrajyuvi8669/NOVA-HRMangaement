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
import logging #library to store logs
from cdifflib import CSequenceMatcher

##-------------------------------------------logging--------------------------------------------

logger = logging.getLogger(__name__)

# Create handlers
stream_handler = logging.StreamHandler(stream=open('file.log', 'a'))
c_handler = logging.StreamHandler(stream=open('file.log', 'a'))
f_handler = logging.StreamHandler(stream=open('file.log', 'a'))
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(lineno)d - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

##-------------------------------------------logging end-------------------------------------------------


global affirm_deny_button,add_TTE_form_slot,EMP_ID
affirm_deny_button = [{"title":"Yes","payload":"yes"},{"title":"No","payload":"no"}]
global notify_button
notify_button = [{"title":"Request for New Task","payload":"request for new task"}]
add_TTE_form_slot = []
cal = pdt.Calendar()
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

# "http://mindsconnect.omfysgroup.com"
# "http://10.0.0.25:8088/MINDS_CONNECT"
# "http://43.231.254.81/MINDS_CONNECT"
# http://43.231.254.81/MINDSCONNECT
# http://106.201.234.246/MINDSCONNECT
# http://103.109.13.198/MINDSCONNECT
# http://103.109.13.198/OLD_MINDSCONNECT
# mindsconnect_url = "http://103.109.13.198/MINDSCONNECT" # https://uat-java.omfysgroup.com/MINDSCONNECT/
# http://43.231.254.81:8000
API_URL_Django = "http://13.127.186.145:8000"
# "http://13.127.186.145:8000"
# "http://43.231.254.81:8888"
# "http://127.0.0.1:8000"
API_URL_Flask = "http://43.231.254.81:5888"
# "http://127.0.0.1:5000"
# employee_first_name_globally = ""
employee_last_name_globally = ""
# UAT Project Module
# http://103.109.13.198/project-management/
# "http://103.109.13.198/project_mngt"
# "http://uat-java.omfysgroup.com/project_mngt"
# project_module_url = "http://103.109.13.198/project_mngt" # old public ip
# project_module_url = "http://103.119.160.114/project_mngt"
# mindsconnect_url ="http://103.119.160.114/MINDSCONNECT" #"http://103.109.13.198/MINDSCONNECT" # https://uat-java.omfysgroup.com/MINDSCONNECT/
# mindsconnect_url = "http://uat.omfysgroup.com/MINDSCONNECT"
mindsconnect_url = "http://uat.omfysgroup.com/MINDSCONNECT_API"
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
    # print ("confidence percentage with tasks", confidence_percent)
    print("confidence percentage with tasks", confidence_percent)
    #   max_match_index = confidence_percent.index(max(confidence_percent)) if max(confidence_percent) >70 else ''
    max_match_index = confidence_percent.index(max(confidence_percent)) 
    task_name = list_of_predefindtask[max_match_index] 
    task_id = list_of_predefind_taskId[max_match_index]
    # print(confidence_percent.index(max(confidence_percent)))  ####### get index of max percentage
    print(confidence_percent.index(max(confidence_percent)))  ####### get index of max percentage
    # print(list_of_predefindtask[max_match_index])
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
        # print("Inside validate user login form required slot")
        print("Inside validate user login form required slot")
        global login_slot
        login_slot = ["emp_code","password"]
        return login_slot

    def validate_emp_code(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        # print('validate value of emp_code ', value)
        print('validate value of emp_code ', value)
        # print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        response = requests.get(
            '{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, value))

        # print('emp code response is ', response.json())
        global wrong_emp_code_count

        if response.json() != None:
            data = response.json()
            global EMP_ID
            EMP_ID = str(data['emp_id']['emp_id'])
            # print('EMP_ID from validate ', EMP_ID)
            print('EMP_ID from validate ', EMP_ID)

            global employee_first_name_globally
            employee_first_name_globally = str(data['emp_id']['emp_first_name'])
            # print('Employee first name ', str(data['emp_id']['emp_first_name']))
            print('Employee first name ', str(data['emp_id']['emp_first_name']))

            global employee_last_name_globally
            employee_last_name_globally = str(data['emp_id']['emp_last_name'])
            # print('Employee last name ', str(data['emp_id']['emp_last_name']))
            print('Employee last name ', str(data['emp_id']['emp_last_name']))
            return {'emp_code': value}

        else:
            dispatcher.utter_template('utter_wrong_emp_code', tracker)
            return {"emp_code": None}

    def validate_password(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        # print('validate value of password  ', value)
        print('validate value of password  ', value)
        # print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        global wrong_password_attempt, login_slot

        response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, tracker.get_slot('emp_code'), value))
        data = response.json()
        # print("login data;",data)
        if data != None :
            try:
                if data["errorCode"]==208 and data['errorMsg'] == "Failed." :
                    # print("password not matched")
                    print("password not matched")
                    wrong_password_attempt = wrong_password_attempt + 1
                    dispatcher.utter_template('utter_wrong_password', tracker)
                    return {"password": None}
            except:
                # print("I am in except loop password matched")
                print("I am in except loop password matched")
                wrong_password_attempt = 0
                return {"password": value}
                
        elif wrong_password_attempt < 3:
            # print("wrong_password_attempt", wrong_password_attempt)
            print("wrong_password_attempt", wrong_password_attempt)
            wrong_password_attempt = wrong_password_attempt + 1
            dispatcher.utter_template('utter_wrong_password', tracker)
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
            # print("Inside user login submit")
            print("Inside user login submit")

            response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, tracker.get_slot('emp_code'),tracker.get_slot('password')))
            if len(login_slot)> 0 and response.json() != None:
                response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, tracker.get_slot('emp_code')))
                data = response.json()
                EMP_name = str(data['emp_id']['emp_first_name'])
                EMP_last_name = str(data['emp_id']['emp_last_name'])
                # print(EMP_name)
                print(EMP_name)
                # global email_id1
                # email_id1 = str(data['emp_id']['email'])
                dispatcher.utter_message("Hi {} ".format(EMP_name))
                dispatcher.utter_template('utter_help_user', tracker)
                return []
            else:
                dispatcher.utter_template("utter_greet",tracker)
                return [SlotSet('emp_code', None), SlotSet('password', None)]
        except:
            dispatcher.utter_template("utter_greet",tracker)
            return [SlotSet('emp_code',None),SlotSet('password',None)]
 
class ActionSetlogin(Action):

    def name(self):
        return 'action_set_login_slots'

    def run(self, dispatcher, tracker, domain):
        global EMP_ID
        txt = tracker.latest_message['text']
        x = re.findall("OMI-[0-9]{4}", txt)
        y = re.split("password is ", txt)
        
        print(x[0],y[-1])
        emp_code = x[0]
        password = y[-1]
        response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, emp_code))
        data = response.json()
        EMP_name = str(data['emp_id']['emp_first_name'])
        EMP_last_name = str(data['emp_id']['emp_last_name'])
        EMP_ID = str(data['emp_id']['emp_id'])
        # print(EMP_name)
        print(EMP_name)
        print("setting employee code is", emp_code)
        # print("setting employee code is", emp_code)
        # print("password is", password)
        print("password is", password)
        return [SlotSet('emp_code',emp_code),SlotSet('password',password)]
    
class ActionCheckLoggedForProjectManagement(Action):

    def name(self):
        return 'action_check_logged_for_project_management'

    def run(self, dispatcher, tracker, domain):
        # emp_code = 'OMI-1036'
        # password = 'Omfys@123'
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        # print("employee code is", emp_code)
        print("employee code is", emp_code)
        # print("password is", password)
        print("password is", password)

        intent = tracker.latest_message['intent'].get('name')

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            try:

                if emp_code  == " " and password  == " ":
                    raise Exception('I know Python!')

                if emp_code is None and password is None:
                    raise Exception('I know Python!')

           
                response = requests.get("{}/projects/{}/completed".format(project_module_url,tracker.get_slot('emp_code')))
                data = response.json()
                print(data)
                # print(data)
                print(len(data))
                # print(len(data))
                project = len(data) 
                # print(project)
                print(project)
                             
                buttons = []

                try:
                    if data['errorCode'] == 105:
                        
                        buttons.append({"title": "Completed Projects",
                                        "payload": "Completed Projects",
                                        "badge": "{}".format(data['errorDesc'])
                                        })
                     
                except:
                    buttons.append({"title": "Completed Projects",
                                           "payload": "Completed Projects",
                                           "notifications": "{}".format(project)})
                    
                response1 = requests.get(
                    "{}/projects/{}/ongoing".format(mindsconnect_url,tracker.get_slot('emp_code')))
                # print(response1)
                print(response1)
                data1 = response1.json()
                # print(data1)
                print(data1)
                # print(len(data1))
                print(len(data1))
                project1 = len(data1)
                
                try:
                    if (data1['errorCode'] == 105):
                        buttons.append({"title": "Ongoing Project",
                                                                   "payload": "Ongoing Project",
                                                                   "badge": "{}".format(data1['errorDesc'])})

                       
                    elif (data1['errorCode'] == 109):
                        buttons.append({"title": "Ongoing Project",
                                        "payload": "Ongoing Project",
                                        "badge": "{}".format(data1['errorDesc'])})
                        
                except:
                    buttons.append({"title": "Ongoing Projects",
                                    "payload": "Ongoing Projects",
                                    "notifications": "{}".format(project1)})
                    
                response_pending_projects = requests.get("{}/projects/{}/pending".format(mindsconnect_url,tracker.get_slot('emp_code')))
                data_pending_projects = response_pending_projects.json()
                # print(data_pending_projects )
                # print(len(ddata_pending_projects ))
                print(len(ddata_pending_projects ))
                num_pending_project = len(data_pending_projects ) 
                print(num_pending_project,'num_pending_project')
                             
                buttons = []

                try:
                    if data['errorCode'] == 105:
                        buttons.append({"title": "Pending Projects",
                                        "payload": "Pending Projects",
                                        "badge": "{}".format(data['errorDesc'])
                                        })
                     
                except:
                    buttons.append({"title": "Pending Projects",
                                           "payload": "Pending Projects",
                                           "notifications": "{}".format(num_pending_project)})
                    
                response_approved_projects = requests.get("{}/projects/{}/approved".format(mindsconnect_url,tracker.get_slot("emp_code")))
                print(response_approved_projects ,"approved_projects ")
                # data_approved_projects  = response_approved_projects.json()
                print(data_approved_projects)
                print(len(data_approved_projects))
                length_of_approved_projects = len(data_approved_projects)
                
                try:
                    if (data_requestes_training['errorCode'] == 400):
                        buttons.append({"title": "Approved Projects",
                                                                   "payload": "Approved Projects",
                                                                   "badge": "{}".format(data_approved_projects['errorDesc'])})
                        
                        buttons.append({"title": "Home",
                                                                   "payload": "Home",
                                                                   })
                       
                    elif (data_requestes_training['errorCode'] == 109):
                        buttons.append({"title": "Approved Projects",
                                                                   "payload": "Approved Projects",
                                                                   "badge": "{}".format(data_approved_projects['errorDesc'])})
                        
                        buttons.append({"title": "Home",
                                        "payload": "Home"})
                        
                except:

                    buttons.append({"title": "Approved Projects",
                                                                   "payload": "Approved Projects",
                                    "notifications": "{}".format(length_of_approved_projects)})
                   
                    buttons.append({"title": "Home",
                                    "payload": "Home"})
               
                     
                print("below if statement")
                dispatcher.utter_button_message("Would you like to move forward? Please choose feature",buttons)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

            return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class CompletedprojectsAction(Action):
    
    def name(self) -> Text:
        return "action_show_completed_projects"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
        ) -> List[Dict[Text, Any]]:
        user_message = tracker.get_intent_of_latest_message
        print(user_message,"message from user")
        
        return []
    
class OngoingprojectsAction(Action):
    
    def name(self) -> Text:
        return "action_show_ongoing_projects"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
        ) -> List[Dict[Text, Any]]:
        
        user_message = tracker.get_intent_of_latest_message
        print(user_message,"message from user")
        
        return []
    
class PendingprojectsAction(Action):
    
    def name(self) -> Text:
        return "action_show_pending_projects"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any],
        ) -> List[Dict[Text, Any]]:
        user_message = tracker.get_intent_of_latest_message
        print(user_message,"message from user")
        
        return []

class ProjectsForm(FormValidationAction):

    def name(self):
        return "validate_projects_form"

    @staticmethod
    async def required_slots(tracker: Tracker) -> List[Text]:
        print("Inside required slot")
        global Projects_form_slot
        Projects_form_slot = ["project_type","resources"]
        return Projects_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("slot mapping")

        return {
            "project_type": [
                self.from_entity(entity="project_type"),
                self.from_text(intent="approved_projects"),
                self.from_text(intent="pending_projects"),
                self.from_text(intent="ongoing_projects"),
                self.from_text(intent="completed_projects"),
                self.from_text()
            ],
            "resources": [
                self.from_entity(entity="resources"),
                self.from_text(intent="data"),
                self.from_text()
            ]
        }

    def validate_project_type(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of emp_code ', value)
        
        print('emp code response is ', response.json())
        global wrong_count

        if value in ['completed','pending','approved','ongoing']:
            wrong_attempt = 0
            return {'project_type': value}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message('action_check_logged_for_project_management', tracker)
            return {"project_type": None}
        else:
            global Projects_form_slot
            Projects_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit.")
            return self.deactivate()
        
    def validate_resources(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of resources', value)
        print('emp code from tracker', tracker.get_slot('emp_code'))
        global wrong_attempt
        global name_of_employee
        global valid
        valid = "false"
        
        u = value.upper()
        print(u.rfind('OMI-'))
        try:
            if u.title() in name_of_employee:
                print(u.title()," u.title()")
                # print("name_of_employee[u.title()]",name_of_employee[u.title()])
                valid = "true"
        except:
            valid = "flase"
            print("No name")
        if valid == "true":
            wrong_attempt = 0
            return {"resources": name_of_employee[u.title()]}
        elif u.rfind('OMI-') == 0:
            print("inside if validate other employee code")
            wrong_attempt = 0
            return {"resources": u}
        else:
            response = requests.get("{}/empDetails?empdata={}".format(mindsconnect_url, value))
            data = response.json()
            print(len(data))
            len1 = (len(data))
            name_of_employee = {}
            try:
                if len(data) > 1:
                    buttons = []
                    if len(data[0]) is 11:
                       
                        for number in range(len1):
                            name_of_employee.update({"{} {}".format(data[number]['emp_first_name'],data[number]['emp_last_name']):data[number]['emp_code']})
                            buttons.append({"title": data[number]['emp_first_name']+" "+
                                                                       data[number]['emp_last_name'],
                                        "payload": ""+data[number]['emp_code']})
                        dispatcher.utter_button_message("Could you please select appropriate name of employee?", buttons)
                        # dispatcher.utter_message("please enter employee code of colleague for whom you want to know about ")
                        return {"resources": None}
                elif len(data) is 1:
                    wrong_attempt = 0
                    return {"resources": data[0]['emp_code']}
                else:
                    dispatcher.utter_message('Could you please re-enter the name/employee code of resource?')
                    return {"resources": None}
            except:
                
                if wrong_attempt < 3:
                    wrong_attempt = wrong_attempt + 1
                    dispatcher.utter_message(data['errorDesc'])
                    return {"resources": value}
                else:
                    global Projects_form_slot
                    Projects_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("You reached to maximum limit of attempt")
                    return self.deactivate()
                
class ActionProjectsForm(Action):
    
    def name(self):
        return "action_projects_form_submit"

    def run(self, dispatcher, tracker, domain):
        global Projects_form_slot
        
        try:
            if len(Projects_form_slot)> 0:
                gt= {}
                
                global projects_by_serial_number
                projects_by_serial_number = {}
                # projects_by_project_code = {}
                       
                response_projects = requests.get("{}/projects/{}/{}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("project_type")))
                # print(response_projects)
                data_response_projects = response_projects.json()
                # print(data_response_projects)

                try:
                    if data_response_projects['errorCode']=='105':
                        dispatcher.utter_message(data_response_projects['errorDesc'])
                        dispatcher.utter_template("utter_continue_projects",tracker)
                        return [SlotSet('project_type', None), SlotSet('resources', None)]
                        
                except:
        
                    for each_project in range(0,len(data_response_projects)):
            
                        # projects_by_project_code.append({"{}":{"pr_code":"{}"}})
                        projects_by_serial_number.append({"{}".format(each_project+1):"{}".format(data[each_project]["pr_code"])})
                        gt.append({
                            "type": "List",
                            "sub-type": "Project",
                            "title": "Following are {} Projects.".format(tracker.get_slot('project_type')),
                            "number": each_project,
                            "links":
                                [
                                {
                                    "text": "{}. {} : {} project under {}".format(each_project+1,data[each_project]["pr_code"], data[each_project]["project_manager"]),
                                    "href": "{}".format(data[each_project]["pr_code"]),
                                }
                            ]
                        })
                    print(gt)
        
                    dispatcher.utter_custom_json(gt)
                    return [FollowupAction("action_show_projects_details"),SlotSet('project_type', None), SlotSet('resources', None)]

            else:
                dispatcher.utter_template("utter_continue_projects",tracker)
                return [SlotSet('project_type', None), SlotSet('resources', None)]
        except:
            dispatcher.utter_template("utter_continue_projects",tracker)
            return [SlotSet('project_type', None), SlotSet('resources', None)]
                

class ProjectsDetailsForm(FormValidationAction):
    
    def name(self):
        return "validate_show_projects_details_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        print("Inside required slot")
        global show_projects_details_form_slot
        show_projects_details_form_slot = ["pr_code"]
        return show_projects_details_form_slot
    
    def validate_pr_code(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of pr_code', value)
        global projects_by_serial_number, wrong_attempt
               
        try:
            if value in projects_by_serial_number.keys():
                response_project_details = requests.get("{}/project_details/{}/{}".format(mindsconnect_url,tracker.get_slot("emp_code"),projects_by_serial_number[value]))
                # print(response_project_details)
                data_response_project_details = response_response_project_details.json()
                # print(data_response_project_details)
                return {"pr_code": projects_by_serial_number[value]}
            else:
                response_project_details = requests.get("{}/project_details/{}/{}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("pr_code")))
                # print(response_project_details)
                data_response_project_details = response_response_project_details.json()
                # print(data_response_project_details)
                return {"pr_code": value}
                
        except:
            
            if wrong_attempt < 3:
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_message('action_check_logged_for_project_management', tracker)
                return {"pr_code": None}
            else:
                global show_projects_details_form_slot
                show_projects_details_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("You reached to maximum limit.")
                return self.deactivate()
            
class ActionProjectDetails(Action):
    
    def name(self):
        return "action_show_projects_details_form_submit"

    def run(self, dispatcher, tracker, domain):
        
        global show_projects_details_form_slot
        
        try:    
            if len(show_projects_details_form_slot)> 0:
                response_project_details = requests.get("{}/project_details/{}/{}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("pr_code")))
                # print(response_project_details)
                data_response_project_details = response_response_project_details.json()
                # print(data_response_project_details)

                try:
                    if data_response_projects['errorCode']=='105':
                        dispatcher.utter_message(data_response_projects['errorDesc'])
                        dispatcher.utter_template("utter_continue_projects",tracker)
                        return [SlotSet('pr_code', None)]
                        
                except:
                       
                    dispatcher.utter_message("Following are project details:")
                    return [FollowupAction("action_show_projects_details"),SlotSet('pr_code', None),]

            else:
                dispatcher.utter_template("utter_continue_projects",tracker)
                return [SlotSet('pr_code', None)]
        
        except:
            dispatcher.utter_template("utter_continue_projects",tracker)
            return [SlotSet('pr_code', None)]
                
                
#--------------------------------------------------------------add TTE ----------------------------------------------------------------
global selected_project_id, selected_maintask_id, selected_subtask_id, selected_subsubtask_id,task_selection_confirmation_flag,selected_project_name,selected_main_task_name
global selected_sub_task_name,selected_sub_sub_task_name, selected_activity_name, selected_task_status, selected_start_time,selected_end_time
task_selection_confirmation_flag = ''
selected_project_id, selected_maintask_id, selected_subtask_id, selected_subsubtask_id = '','','',''
selected_project_name,selected_main_task_name,selected_sub_task_name,selected_sub_sub_task_name = "NA","NA","NA","NA"
selected_activity_name, selected_task_status, selected_start_time,selected_end_time = 'NA','NA','NA','NA'

def change_time_format(fetched_time):
  try:
    pattern = "\d{1,2}[.:]{0,1}\d{0,2}\s{0,1}[am,pm,PM,AM,Pm,Am]{2}"
    fetched_time = re.findall(pattern,fetched_time)[-1]
    extension = ['am','pm']
    removed_am_pm = [fetched_time.lower().replace(i,'') for i in extension if i in fetched_time.lower()] 
    std_time_format = removed_am_pm[-1].replace('.',':').replace(',',':').strip()
    std_time_format = std_time_format if ":" in std_time_format else std_time_format + ':00' if len(std_time_format)== 2 else '0'+std_time_format + ':00'
    if fetched_time.lower()[-2:] == 'pm':
        std_time_format = str(int(std_time_format[:2])+12) + std_time_format[2:] if ':' not in (std_time_format[:2]) else str(int(std_time_format[:1])+12) + std_time_format[1:]  
    else:
        std_time_format
    print(std_time_format)
    return std_time_format
  except:
      std_time_format = None
      return std_time_format

def confirm_tte_details_html_format(selected_project_name,selected_main_task_name,selected_sub_task_name,selected_sub_sub_task_name,activity_name,status,start_time,end_time):
    tb = []
    tb.append({
                "type": "table",
                "title": " TTE Details",
                "table_row_head":
                                [
                                    {
                                        "title": "Project Name"
                                        
                                    },
                                    {
                                        "title": "Main Task"
                                        
                                    },
                                    {
                                        "title": "Sub Task"
                                        
                                    },
                                    {
                                        "title": "Sub Sub Task"
                                        
                                    },
                                    {
                                        "title": "Activity"
                                    },
                                    {
                                        "title": "Start Time"
                                    },
                                    {
                                        "title": "End Time"
                                    },
                                    {
                                        "title": "Task Status"
                                    }
                                ],

                            "row_data":
                                [
                                    {
                                        "title": selected_project_name
                                        
                                    },
                                    {
                                        "title": selected_main_task_name
                                        
                                    },
                                    {
                                        "title": selected_sub_task_name
                                        
                                    },
                                    {
                                        "title": selected_sub_sub_task_name
                                        
                                    },
                                    {
                                        "title": activity_name
                                    },
                                    {
                                        "title": start_time
                                    },
                                    {
                                        "title": end_time
                                    },
                                    {
                                        "title": status
                                    }
                                ]
                    })
    # print(tb)
    return tb
    # TTE_details = """
    # <html>
    #     <head></head>
    #     <body>
    #         <table border=3 style=font-size:10px table-layout=auto cellspacing=0.5 cellpadding=0 >
    #             <caption><b>TTE Details</b></caption>
    #             <tr>
    #                 <td>Project Name</td>
    #                 <td>{}</td>		
    #             </tr>
    #             <tr>
    #                 <td>Main Task</td>
    #                 <td>{}</td>		
    #             </tr>
    #             <tr>
    #                 <td>Sub Task</td>
    #                 <td>{}</td>
    #             </tr>
    #                 <tr>
    #                 <td>Sub Sub Task</td>
    #                 <td>{}</td>
    #             </tr>
    #             <tr>
    #                 <td>Activity</td>
    #                 <td>{}</td>		
    #             </tr>
    #             <tr>
    #                 <td>Start Time</td>
    #                 <td>{}</td>				        
    #             </tr>
    #             <tr>
    #                 <td>End Time</td>
    #                 <td>{}</td>		
    #             </tr>
    #             <tr>
    #                 <td>Task Status</td>
    #                 <td>{}</td>		
    #             </tr>

    #         </table>
    #     </body>
    # </html>""".format(selected_project_name,selected_main_task_name,selected_sub_task_name,selected_sub_sub_task_name,activity_name,start_time,end_time,status)
    # return TTE_details


def get_miscellaneous_task():
    
    global EMP_ID,project_num 
    project_num = 0
    
    misc_url = "{}/api/project/getmisctask?empid={}".format(project_module_url,EMP_ID)
    
    response = requests.get(misc_url)
    print(response.status_code)
    response_misc_list = response.json()

    # if response_misc_list['errorCode'] == '204':
    #     total_tasks_by_srNo = {}
    #     total_tasks_by_name = {}
    #     misc_task_name_list = []

    #     return misc_task_name_list,total_tasks_by_srNo, total_tasks_by_name
    
    num_of_tasks = len(response_misc_list)

    # print(response_misc_list)
    
    title = [{"more_link": "{}".format(misc_task['own_task_desc']) ,
                  "hover": "Start Date:{}<br>End Date:{}<br>Actual Start Date:{}<br>Actual End Date:{}<br>Task Type:{}<br>Status:{}".format(date_convert(misc_task['planned_start_date']), date_convert(misc_task['planned_completion_date']),date_convert(misc_task['actual_start_date']),date_convert(misc_task['actual_completion_date']),misc_task['own_task_type']['task_type_name'], misc_task['own_task_status']),
                  "link_href": misc_task['own_task_code']}  for pr_num, misc_task in enumerate(response_misc_list)]
    # print(title)
    
    total_tasks_by_srNo = {}
    total_tasks_by_name = {}
    misc_task_name_list = []
    
    if num_of_tasks > 0:		

        taskscode_by_SRNo = dict(enumerate([tasks['own_task_code'] for tasks in response_misc_list],1))
        taskscode_by_name = {tasks['own_task_desc']:tasks['own_task_code'] for tasks in response_misc_list}

        total_tasks_by_srNo = {**total_tasks_by_srNo,**taskscode_by_SRNo}
        total_tasks_by_name = {**total_tasks_by_name, **taskscode_by_name}

    else:
        total_tasks_by_srNo = {}
        total_tasks_by_name = {}
        print("misc tasks are not available")
    for display_details in title:
            project_num = project_num + 1
            misc_task_name_list.append({
                "type": "List",
                
                "title": "Following projects are available:",
                
                "number": "{}".format(project_num),
                "links": 
                [
                    {
                    "display_text": "more",
                    "more_link": "{}. {}".format(project_num,display_details["more_link"]),
                    "hover": display_details["hover"],
                    "link_href": display_details["link_href"]
                }
            ]})
    # print(misc_task_name_list)
        # return approved_projectId_by_SRNo, approved_projectId_by_name
    return misc_task_name_list,total_tasks_by_srNo, total_tasks_by_name

def date_convert(provided_date):
    try:
        formated_date = dt.datetime.strptime(provided_date,"%Y-%m-%dT%X.%f%z").strftime("%d/%m/%Y")
        
    except:
        if provided_date == None:
            formated_date = "NA"
    return formated_date

def get_project_list(url):
        
    response = requests.get(url)
    print(response.status_code)
    data = response.json() if response.status_code == 200 else {} 
    if data:
        # print("data",data)
        try:
            if data["errorCode"] == '204':  ## condition to check if data is available or not but response status code is 200
                # return "Projects are not available"	
                projectList_with_details = []
                task_keys = []
                return projectList_with_details, task_keys
        except:	
            try:
                if url.count("mtasks?")>0 : ## will check for maintask url
                    print("i am in maintask")
                    # planned_start_date = ["" if "plannedStartDate" not in projects else projects["plannedStartDate"] for projects in data]
                    maintask_with_details = [list(projects.values()) for projects in data]
                    task_keys = [list(projects.keys()) for projects in data][0]
                    print(maintask_with_details, task_keys)
                    return maintask_with_details, task_keys
                if "mainTaskId=" in url : ## will check for subtask url and sub_subtask
                    if "mainTaskId=" and "subTaskId=" in url : ## for sub_subtask url
                        print("i am in subsubtask")
                        # planned_start_date = ["" if "plannedStartDate" not in projects else projects["plannedStartDate"] for projects in data]
                        sub_subtask_with_details = [list(projects.values()) for projects in data]
                        task_keys = [list(projects.keys()) for projects in data][0]
                        print(sub_subtask_with_details, task_keys)
                        return sub_subtask_with_details, task_keys
                    else:
                        print("i am in subtask")
                        # planned_start_date = ["" if "plannedStartDate" not in projects else projects["plannedStartDate"] for projects in data]
                        subtask_with_details = [list(projects.values()) for projects in data]
                        task_keys = [list(projects.keys()) for projects in data][0]
                        print(subtask_with_details, task_keys)
                        return subtask_with_details, task_keys
                if "projectStatus=" in url: ### for project url
                    # print(data)
                    print("I am in Project list")
                    # project_name_list = [[projects["projectName"],projects["projectCode"]] if "projectName" in projects else ''  for projects in data ]
                    projectList_with_details = [list(projects.values()) for projects in data]
                    task_keys = [list(projects.keys()) for projects in data][0]
                    # projectId_by_SRNo = dict(enumerate([ projects[0] for projects in projectList_with_details],1))
                    # projectId_by_name = {projects[2]:projects[0] for projects in projectList_with_details}
                    # print(projectId_by_SRNo, projectId_by_name)
                    # print(projectList_with_details, task_keys)
                    # p1 = [ projects[0] for projects in projectList_with_details]
                    # p2 = dict(enumerate([ projects[0] for projects in projectList_with_details], len(p1)+1))
                    # # p3 = dict(enumerate(p1+p2,1))
                    # print(p1, p2)
                    return projectList_with_details, task_keys

            except:
                print("I am in exception loop")
                return "Something went wrong!! will come back to you"
    else:
        return "Something went wrong!! Please check network connection"

# print(get_project_list(url))
# projectList_with_details, task_keys = get_project_list(url)
# num = 0
# title = [{"more_link": "{}. {}:{}-{} training".format(num+1, projects[1], projects[2], projects[8]) ,"hover": "Start Date:{}<br>End Date:{}<br>Project Manager:{}<br>Status:{}".format(projects[6], projects[7], projects[5], projects[10]),"link_href": projects[0]} for projects in projectList_with_details ],

# # "hover": "Start Date:{}<br>End Date:{}<br>Project Manager:{}<br>Status:{}".format(projects[6], projects[7], projects[5], projects[10]),
# # "link_href": projects[0]) for projects in projectList_with_details[0:]}
# print(title)
def map_project_id_name(project_list):
        
    total_projects_by_srNo = {}
    total_projects_by_name = {}
    
    num_of_projects = len(project_list)
    if num_of_projects>0:
        projectId_by_SRNo = dict(enumerate([projects[0] for projects in project_list],1))
        projectId_by_name = {projects[2]:projects[0] for projects in project_list}
        print(projectId_by_SRNo, projectId_by_name)
        total_projects_by_srNo = {**total_projects_by_srNo,**projectId_by_SRNo}
        print(total_projects_by_srNo)
        total_projects_by_name = {**total_projects_by_name, **projectId_by_name}
        print(total_projects_by_name)
        # return total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name
    else:
        total_projects_by_srNo = {}
        total_projects_by_name = {}
        print("projects are not available")
        # return approved_projectId_by_SRNo, approved_projectId_by_name
    return total_projects_by_srNo, total_projects_by_name

def map_main_task_by_name_srno(task_list):
        
    total_tasks_by_srNo = {}
    total_tasks_by_name = {}
    
    num_of_task= len(task_list)
    if num_of_task > 0:
        tasksId_by_SRNo = dict(enumerate([tasks[0] for tasks in task_list],1))
        tasksId_by_name = {tasks[1]:tasks[0] for tasks in task_list}
        print(tasksId_by_SRNo , tasksId_by_name)
        total_tasks_by_srNo = {**total_tasks_by_srNo,**tasksId_by_SRNo}
        print(total_tasks_by_srNo)
        total_tasks_by_name = {**total_tasks_by_name, **tasksId_by_name}
        print(total_tasks_by_name)
        # return total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name
    else:
        total_tasks_by_srNo = {}
        total_tasks_by_name = {}
        print("projects are not available")
        # return approved_projectId_by_SRNo, approved_projectId_by_name
    return total_tasks_by_srNo, total_tasks_by_name

def Project_list_display():
    global EMP_ID
    ongoing_url = "{}/api/projects?projectStatus=Ongoing&empId={}".format(project_module_url,EMP_ID)
    approved_url = "{}/api/projects?projectStatus=Approved&empId={}".format(project_module_url,EMP_ID)

    response_project_list_approved, task_keys = get_project_list(approved_url)
    response_project_list_ongoing, task_keys = get_project_list(ongoing_url)
    
    num_of_approved_project = len(response_project_list_approved)
    num_of_ongoing_projects = len(response_project_list_ongoing) 
    
    print(response_project_list_approved)
    print(response_project_list_ongoing)
    
    total_project_details = []
    total_project_details= total_project_details + response_project_list_approved + response_project_list_ongoing
    
    total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name = map_project_id_name(total_project_details) 
    # ongoing_projects_by_srNo, ongoing_projects_by_name = map_project_id_name(response_project_list_ongoing) 

    # total_projects_ongoing_approved_by_srNo = {**total_projects_ongoing_approved_by_srNo,**approved_projects_by_srNo, **ongoing_projects_by_srNo}
    print(total_projects_ongoing_approved_by_srNo)
    # total_projects_ongoing_approved_by_name = {**total_projects_ongoing_approved_by_name, **approved_projects_by_name, **ongoing_projects_by_name}
    print(total_projects_ongoing_approved_by_name)

    project_name_list = []
    project_num = 0

    title = [{"more_link": "{}:{}-{}".format(projects[1], projects[2], projects[8]) ,
                  "hover": "Start Date:{}<br>End Date:{}<br>Project Manager:{}<br>Status:{}".format(date_convert(projects[6]), date_convert(projects[7]), projects[5], projects[10]),
                  "link_href": projects[0]}  for project_num, projects in enumerate(total_project_details)]
    print(title)
    num_project = len(total_projects_ongoing_approved_by_srNo)
    print("Number of projects",num_project)
    for display_details in title:
            project_num = project_num + 1
            project_name_list.append({
                "type": "List",
                
                "title": "Followling projects are available for task and time entry and update task status:<br><br> Select one of the choices below <br><t><t>  (i) Click on the selected link <br><t><t>  (ii) Provide serial number <br><t><t>  (iii) Provide project name <br> ex: SSC-2021-1:Minds Connect-V1 reply by middle name i.e Minds Connect.",
                
                "number": "{}".format(project_num),
                "links": 
                [
                    {
                    "display_text": "more",
                    "more_link": "{}. {}".format(project_num,display_details["more_link"]),
                    "hover": display_details["hover"],
                    "link_href": display_details["link_href"]
                }
            ]})
    project_num = project_num + 1
    project_name_list.append({
                "type": "List",
                
                "title": "Followling projects are for task and time entry:<br><br>Select one of the choices below <br><t><t>  i) Click on the selected link <br><t><t>  ii)Provide serial number <br><t><t>  iii)Provide project name <br> ex: SSC-2021-1:Minds Connect-V1 reply by middle name i.e Minds Connect.",
               
                "number": "{}".format(project_num),
                "links": 
                [
                    {
                    "display_text": "more",
                    "more_link": "{}. Miscellaneous Projects".format(project_num),
                    #"hover": display_details["hover"],
                    "link_href": "miscellaneous task"
                }
            ]})
               

    return project_name_list, total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name

def main_task_list_display(project_id):
    global EMP_ID

    # emp_id fullName = emp_details()
    print("calling maintask list display function")
    print("project_value", project_id, "employee Id", EMP_ID)
    main_task_url = "{}/api/project/mtasks?projectId={}&empId={}".format(project_module_url,project_id,EMP_ID)
    print("maintask url", main_task_url)
    response_main_task_list, task_keys = get_project_list(main_task_url)
    num_of_tasks = len(response_main_task_list)
    print("geting tasks ",response_main_task_list)
   
    total_main_task_by_srNo, total_main_task_by_name = map_main_task_by_name_srno(response_main_task_list) 
    # ongoing_projects_by_srNo, ongoing_projects_by_name = map_project_id_name(response_project_list_ongoing) 

    # total_projects_ongoing_approved_by_srNo = {**total_projects_ongoing_approved_by_srNo,**approved_projects_by_srNo, **ongoing_projects_by_srNo}
    print("total_main_task_by_srNo",total_main_task_by_srNo)
    # total_projects_ongoing_approved_by_name = {**total_projects_ongoing_approved_by_name, **approved_projects_by_name, **ongoing_projects_by_name}
    print("total_main_task_by_name", total_main_task_by_name)

        
    task_name_list = []
    task_num = 0
          
    title = [{"more_link": "{} Status: {}".format(tasks[1], tasks[3]) ,
                  "hover": "Start Date:{}<br>End Date:{}<br>Actual Start Date:{}<br>Actual End Date:{}<br>Task Type:{}<br>Status:{}".format(date_convert(tasks[6]), date_convert(tasks[7]), date_convert(tasks[8]), date_convert(tasks[9]),tasks[2], tasks[3]),
                  "link_href": tasks[0]}  for task, tasks in enumerate(response_main_task_list)]
    
    print(title)
    num_task = len(total_main_task_by_srNo)
    print("Number of tasks",num_task)
    for display_details in title:
            task_num = task_num + 1
            task_name_list.append({
                "type": "List",
                "title": "Following main tasks are available for task and time entry:",
                "number": "{}".format(task_num),
                "links": 
                [
                    {
                    "display_text": "more",
                    "more_link": "{}. {}".format(task_num,display_details["more_link"]),
                    "hover": display_details["hover"],
                    "link_href": display_details["link_href"]
                }
            ]})
           
    return task_name_list, total_main_task_by_srNo, total_main_task_by_name


def sub_task_list_display(project_id, main_task_id):
    
    global EMP_ID
    sub_task_url = "{}/api/project/mtask/stasks?projectId={}&empId={}&mainTaskId={}".format(project_module_url,project_id,EMP_ID,main_task_id)

    response_sub_task_list, task_keys = get_project_list(sub_task_url)
    
    num_of_tasks = len(response_sub_task_list)
    
    print(response_sub_task_list)
   
    total_sub_task_by_srNo, total_sub_task_by_name = map_main_task_by_name_srno(response_sub_task_list) 
    # ongoing_projects_by_srNo, ongoing_projects_by_name = map_project_id_name(response_project_list_ongoing) 

    # total_projects_ongoing_approved_by_srNo = {**total_projects_ongoing_approved_by_srNo,**approved_projects_by_srNo, **ongoing_projects_by_srNo}
    print(total_sub_task_by_srNo)
    # total_projects_ongoing_approved_by_name = {**total_projects_ongoing_approved_by_name, **approved_projects_by_name, **ongoing_projects_by_name}
    print(total_sub_task_by_name)    
    task_name_list = []
    task_num = 0
          
    title = [{"more_link": "{} Status: {}".format(tasks[1], tasks[3]) ,
                  "hover": "Start Date:{}<br>End Date:{}<br>Actual Start Date:{}<br>Actual End Date:{}<br>Task Type:{}<br>Status:{}".format(tasks[6], tasks[7], tasks[8], tasks[9],tasks[2], tasks[3]),
                  "link_href": tasks[0]}  for task, tasks in enumerate(response_sub_task_list)]
    
    print(title)
    num_task = len(total_sub_task_by_srNo)
    print("Number of tasks",num_task)
    for display_details in title:
            task_num = task_num + 1
            task_name_list.append({
                "type": "List",
                "title": "Following subtasks are available for task and time entry:",
                "number": "{}".format(task_num),
                "links": 
                [
                    {
                    "display_text": "more",
                    "more_link": "{}. {}".format(task_num,display_details["more_link"]),
                    "hover": display_details["hover"],
                    "link_href": display_details["link_href"]
                }
            ]})
           
    

    return task_name_list, total_sub_task_by_srNo, total_sub_task_by_name


def sub_sub_task_list_display(project_id, main_task_id,sub_task_id):
    
    global EMP_ID
    sub_sub_task_url = "{}/api/project/mtask/sstasks?projectId={}&empId={}&mainTaskId={}&subTaskId={}".format(project_module_url,project_id,EMP_ID,main_task_id,sub_task_id)

    response_sub_sub_task_list, task_keys = get_project_list(sub_sub_task_url)
    
    num_of_tasks = len(response_sub_sub_task_list)
    
    print(response_sub_sub_task_list)
   
    total_sub_sub_task_by_srNo, total_sub_sub_task_by_name = map_main_task_by_name_srno(response_sub_sub_task_list) 
    # ongoing_projects_by_srNo, ongoing_projects_by_name = map_project_id_name(response_project_list_ongoing) 

    # total_projects_ongoing_approved_by_srNo = {**total_projects_ongoing_approved_by_srNo,**approved_projects_by_srNo, **ongoing_projects_by_srNo}
    print(total_sub_sub_task_by_srNo)
    # total_projects_ongoing_approved_by_name = {**total_projects_ongoing_approved_by_name, **approved_projects_by_name, **ongoing_projects_by_name}
    print(total_sub_sub_task_by_name)
    
    task_name_list = []
    task_num = 0
          
    title = [{"more_link": "{} Status: {}".format(tasks[1], tasks[3]) ,
                  "hover": "Start Date:{}<br>End Date:{}<br>Actual Start Date:{}<br>Actual End Date:{}<br>Task Type:{}<br>Status:{}".format(date_convert(tasks[6]), date_convert(tasks[7]), date_convert(tasks[8]), date_convert(tasks[9]),tasks[2], tasks[3]),
                  "link_href": tasks[0]}  for task, tasks in enumerate(response_sub_sub_task_list)]
    
    print(title)
    num_task = len(total_sub_sub_task_by_srNo)
    print("Number of tasks",num_task)
    for display_details in title:
            task_num = task_num + 1
            task_name_list.append({
                "type": "List",
                "title": "Following sub-subtasks are available for task and time entry:",
                "number": "{}".format(task_num),
                "links": 
                [
                    {
                    "display_text": "more",
                    "more_link": "{}. {}".format(task_num,display_details["more_link"]),
                    "hover": display_details["hover"],
                    "link_href": display_details["link_href"]
                }
            ]})
           

    return task_name_list, total_sub_sub_task_by_srNo, total_sub_sub_task_by_name


class ActionCheckLoggedForProjectManagement(Action):
    
    def name(self):
        return 'action_check_logged_for_tte'

    def run(self, dispatcher, tracker, domain):
        # emp_code = 'OMI-1036'
        # password = 'Omfys@123'
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

        intent = tracker.latest_message['intent'].get('name')

        if emp_code is None or password is None:
        
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
            return [SlotSet('emp_code', emp_code), SlotSet('password',password)]
        
        else:

            try:

                if emp_code  == " " and password  == " ":
                    raise Exception('I know Python!')

                if emp_code is None and password is None:
                    raise Exception('I know Python!')
                    
                global EMP_ID, resources_project
                return true
                
            except Exception:
                print("Inside except block : action_check_login")
                # dispatcher.utter_template("utter_service_failed_login_message", tracker)
                button = []
                button.append({
                    "title":"Login",
                    "payload":"Login"
                })
                dispatcher.utter_message(buttons= button, text="Apologize for incovinience Could you please login to get the tasks assigned to you?")

            return [SlotSet('emp_code', emp_code), SlotSet('password', password)]

class ActionDisplayProjectListForTTE(Action):
    
    def name(self):
        return 'action_display_project_list'

    def run(self, dispatcher, tracker, domain):
        start_T, end_T = None, None
        try:
            start_T = next(tracker.get_latest_entity_values(entity_type="time",entity_role="start_time"))
            end_T = next(tracker.get_latest_entity_values(entity_type="time",entity_role="end_time"))
            print("end time fetching from role endtime ", end_T)
            print("start time fetching from role endtime ",start_T )
        except:
            try: 
                start_T = next(tracker.get_latest_entity_values(entity_type="start_time"))
                end_T = next(tracker.get_latest_entity_values(entity_type="end_time"))
            except:
                print("User has not mentioned time")
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        # print("employee code is", emp_code)
        # print("password is", password)
        confidence = tracker.latest_message['intent'].get('confidence')
        # print(confidence,"confidence")
        prediction = tracker.latest_message
        entity_type = prediction['entities']
        # print('entity_type',entity_type)
        activity_name = tracker.get_slot("activity_name") if tracker.get_slot("activity_name") else "NA"
        status = tracker.get_slot("task_status") if tracker.get_slot("task_status") else "NA"
        start_time = tracker.get_slot("start_time") if tracker.get_slot("start_time") else "NA"
        end_time = tracker.get_slot("end_time") if tracker.get_slot("end_time") else "NA"
        # print (f'Inside action display project list: activity name {activity_name},task status {status},start time {start_time},end time {end_time}')
        project = tracker.get_slot("project_name") if tracker.get_slot("project_name") else "NA"
        maintask = tracker.get_slot("main_task_name") if tracker.get_slot("main_task_name") else "NA"
        subtask = tracker.get_slot("sub_task_name") if tracker.get_slot("sub_task_name") else "NA"
        subsubtask = tracker.get_slot("sub_sub_task_name") if tracker.get_slot("sub_sub_task_name") else "NA"
        project, maintask ,subtask, subsubtask= project , maintask ,subtask , subsubtask 
        print("Inside action display project list:project:{},maintask:{},subtask:{},subsubtask:{}".format(project,maintask,subtask,subsubtask))
        # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Project: <b>{project}</b><br>\nMain Task: <b>{maintask}</b><br>\nSub Task: <b>{subtask}</b><br>\nSub Sub Task: <b>{subsubtask}</b><br>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
 
        global add_TTE_form_slot,task_selection_confirmation_flag,selected_project_id,selected_project_name
        selected_project_id = ""
        selected_project_name = ""
        task_selection_confirmation_flag = ""
        try:
            
            project_name_list, total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name = Project_list_display()

            if project_name_list != []:
        
                if tracker.get_slot("project_name") != None:
                    if any(exe not in tracker.get_slot("project_name")for exe in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]):
                        print("Inside try of project list display action")
                        add_TTE_form_slot = ["project_id"]
                        value = tracker.get_slot("project_name") if tracker.get_slot("project_name") else value[0]
                        print("Value[0]", value[0])
                        print("project name if slot project_id is set ,value", value[0])
                        project_id, project_name = get_best_match(value[0], total_projects_ongoing_approved_by_name)
                        print("project_id, project_name feched by best match function inside try",project_id, project_name)
                        selected_project_id = project_id
                        selected_project_name = project_name
                        task_selection_confirmation_flag = "Confirming selected project name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Project: <b>{project_name}</b> for TTE?')
                        print("Before slot project id set to be none -------------actions")
                    else:
                        selected_project_id = "miscellaneous task"
                        selected_project_name = "miscellaneous task"
                        task_selection_confirmation_flag = ""                        
                        print("Inside try of project list display action miscelleneous project selected ")
                else:
                    print("Inside try of project list display action ")
                    add_TTE_form_slot = ["project_id"]
                    dispatcher.utter_custom_json(project_name_list)
                    # dispatcher.utter_message("Could you please let me know that which projects would you like to see?")
                    
            else:
                add_TTE_form_slot = []
                dispatcher.utter_message("It seems that projects are not assigned to you yet.")
                dispatcher.utter_template("utter_continue_projects",tracker)
           
        except:
            add_TTE_form_slot = []
            dispatcher.utter_message("It seems that projects are not assigned to you yet.")
            dispatcher.utter_template("utter_continue_projects",tracker)
        return [SlotSet('start_time',start_T),SlotSet('end_time',end_T)]

class addTTEForm(FormValidationAction):
    
    def name(self):
        return "validate_add_tte_form"
    
    # @staticmethod
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required add_tte_form slot")
        global add_TTE_form_slot
        print(add_TTE_form_slot)
        return add_TTE_form_slot
        
    # def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
    #     print("slot mapping")

    #     return {
    #         "project_id": [
    #             self.from_text()
    #         ],
    #         "main_task_name": [
                
    #             self.from_text()
    #         ],
    #         "sub_task_name": [
                
                
    #             self.from_text()
    #         ],
    #         "sub_sub_task_name": [
                
    #             self.from_text()
    #         ]
    #     }
    
    def validate_project_id(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        
        print('validate value of project_id ', value)
        
        global wrong_attempt, EMP_ID, resources_project, add_TTE_form_slot,notify_button, selected_project_id, selected_project_name,affirm_deny_button,task_selection_confirmation_flag

        affirm_deny_button = [{"title":"Yes","payload":"yes"},{"title":"No","payload":"no"}]
        project_name_list, total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name = Project_list_display()
        num_project = len(project_name_list)
        print("total_projects_ongoing_approved_by_name.keys()",total_projects_ongoing_approved_by_name.keys())
        current_intent = tracker.get_intent_of_latest_message()
        print("Checking intent inside project id validation:",current_intent)
        
        if value.lower() in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]:
            task_selection_confirmation_flag = ""

        try:
            
            if task_selection_confirmation_flag == "Confirming selected project name" and selected_project_id:
            
                current_intent = tracker.get_intent_of_latest_message()
                print("Inside task_selection_confirmation_flag = Confirming selected project name")
                task_selection_confirmation_flag = ''
            
                if current_intent == "affirm":
                    value = str(selected_project_id)
                    print("Inside affirm path of task_selection_confirmation_flag value:",value)
                    # return value
                
                elif current_intent == "deny":
                    print("Inside deny path of task_selection_confirmation_flag value:", value)
                    task_selection_confirmation_flag = "Confirming selected project name after deny"
                    project_name_list, total_projects_ongoing_approved_by_srNo, total_projects_ongoing_approved_by_name = Project_list_display()
                    dispatcher.utter_custom_json(project_name_list)
                    return {"project_id":None}
            
            else:

                print(task_selection_confirmation_flag,"task_selection_confirmation_flag")

                try:

                    if int(value):

                        print("Checking int value  -------------------------------------------------------------------------------------------------")
                except:
                    if value in total_projects_ongoing_approved_by_srNo.values():
                        print("checking project code ------------------------------", value) 
                    elif value == "miscellaneous task":
                        print("checking project code ------------------------------", value) 
                        project_id = "miscellaneous task"
                        selected_project_name = "Miscellaneous Tasks"
                        misc_task_name_list,total_tasks_by_srNo, total_tasks_by_name = get_miscellaneous_task()
                        if misc_task_name_list != []:
                            dispatcher.utter_custom_json(misc_task_name_list)
                            add_TTE_form_slot.append("main_task_id")
                        else:
                            dispatcher.utter_message("Miscellaneous tasks are not yet allocated.")
                        return {"project_id":project_id}
                    elif task_selection_confirmation_flag == "Confirming selected project name after deny":
                    
                        print("after denial of selected main task confirming from list")
                        task_selection_confirmation_flag = ""
                        project_id, project_name = get_best_match(value, total_projects_ongoing_approved_by_name)
                        print("project_id, project_name feched by best match function inside try",project_id, project_name)
                        selected_project_id = project_id
                        selected_project_name = project_name
                        task_selection_confirmation_flag = "Confirming selected project name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Project: <b>{project_name}</b> for TTE?')
                        print("Before slot project id set to be none")
                        value = None
                        return {"project_id":None}
                    
                    else:
                        value = tracker.get_slot("project_name") if tracker.get_slot("project_name") else value 
                        print("project name if slot project_id is set ,value", value)
                        if any(exe in value for exe in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]):
                            project_id = "miscellaneous task"
                            selected_project_name = "Miscellaneous Tasks"
                            misc_task_name_list,total_tasks_by_srNo, total_tasks_by_name = get_miscellaneous_task()
                            if misc_task_name_list != []:
                                dispatcher.utter_custom_json(misc_task_name_list)
                                add_TTE_form_slot.append("main_task_id")
                            else:
                                dispatcher.utter_message("Miscellaneous tasks are not yet allocated.")
                            return {"project_id":project_id}    

                        if value.lower() in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"] or value in total_projects_ongoing_approved_by_name.keys() or 0 < int(value) <= num_project or int(value) in total_projects_ongoing_approved_by_srNo.values():
                            if any(exe in value for exe in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]):
                                project_id = "miscellaneous task"
                                selected_project_name = "Miscellaneous Tasks"
                                misc_task_name_list,total_tasks_by_srNo, total_tasks_by_name = get_miscellaneous_task()
                                if misc_task_name_list != []:
                                    dispatcher.utter_custom_json(misc_task_name_list)
                                    add_TTE_form_slot.append("main_task_id")
                                else:
                                    dispatcher.utter_message("Miscellaneous tasks are not yet allocated.")
                                return {"project_id":project_id}    
                            if any(exe not in value for exe in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]):
                                project_id, project_name = get_best_match(value[0], total_projects_ongoing_approved_by_name)
                                print("project_id, project_name feched by best match function inside try",project_id, project_name)
                                selected_project_id = project_id
                                selected_project_name = project_name
                                task_selection_confirmation_flag = "Confirming selected project name"
                                dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Project: <b>{project_name}</b> for TTE?')
                                print("Before slot project id set to be none")
                                value = None
                                return {"project_id":None}
                            else:
                                print("value contains miscelleneous task")
                                return {"project_id":"miscellaneous task"}
        except:
            print("No any project name fetched by text")
            print("original value of project name slot:", value)

        if value.lower() in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"] or value in total_projects_ongoing_approved_by_name.keys() or 0 < int(value) <= num_project or int(value) in total_projects_ongoing_approved_by_srNo.values():
            if value in total_projects_ongoing_approved_by_name.keys():
                project_id = total_projects_ongoing_approved_by_name[value]
                selected_project_name = value
            elif any(exe in value for exe in ["miscellaneous task","misc task","miscellaneous","miscelleneous tasks", "miscellaneous tasks"]) or int(value) == num_project:
                misc_task_name_list,total_tasks_by_srNo, total_tasks_by_name = get_miscellaneous_task()
                if misc_task_name_list != []:
                    dispatcher.utter_custom_json(misc_task_name_list)
                    add_TTE_form_slot.append("main_task_id")
                else:
                    dispatcher.utter_message("Miscellaneous tasks are not yet allocated.")
                project_id = "miscellaneous task"
                selected_project_name = "Miscellaneous Tasks"
            
            elif int(value) in total_projects_ongoing_approved_by_srNo.values():
                project_id = value
                selected_project_name = list(total_projects_ongoing_approved_by_name.keys())[list(total_projects_ongoing_approved_by_name.values()).index(int(project_id))]
            
            else:
                project_id = total_projects_ongoing_approved_by_srNo[int(value)]
                selected_project_name = list(total_projects_ongoing_approved_by_name.keys())[list(total_projects_ongoing_approved_by_name.values()).index(int(project_id))]
            
            wrong_attempt = 0
            
            try:
                
                task_name_list, total_main_task_by_srNo, total_main_task_by_name = main_task_list_display(project_id)
                
                if task_name_list != []:
                
                    if tracker.get_slot("main_task_name") != None:
                
                        global selected_main_task_id, selected_main_task_name

                        selected_main_task_name = ""
                        task_selection_confirmation_flag = ""
                        selected_main_task_id = ""
                        print("Inside try of maintask fetched from text ")
                        add_TTE_form_slot.append("main_task_id")
                        print("Inside try of main task name fetch action")
                        val = tracker.get_slot("main_task_name") if tracker.get_slot("main_task_name") else [None]
                        print("Main task name if slot main task name is in paragraph is set ,value", val[0])
                        main_task_id, main_task_name = get_best_match(val[0], total_main_task_by_name)
                        print("Main task id, Main task_name feched by best match function inside try",main_task_id, main_task_name)
                        selected_main_task_id = main_task_id
                        selected_main_task_name = main_task_name
                        task_selection_confirmation_flag = "Confirming selected main task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Main task: <b>{main_task_name}</b> for TTE?')
                        print("Before slot main task id set to be none -------------actions")
                        # return []
                    
                    else:
                        print("inside else of maintask validation will set herer")
                        add_TTE_form_slot.append("main_task_id")
                        print("add_TTE_form_slot",add_TTE_form_slot)
                        dispatcher.utter_custom_json(task_name_list)
                        dispatcher.utter_button_message(buttons=notify_button,text=None)  #### uncomment after testing
                else:
                
                    dispatcher.utter_message("Tasks are not yet allocated to this project.")
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    # "sub_task_name","sub_sub_task_name"
            except:
                
                dispatcher.utter_message("Tasks are not included further.")
                dispatcher.utter_button_message(buttons=notify_button,text=None)
            
            return {'project_id': project_id}
        
        elif wrong_attempt < 3:
            
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            # dispatcher.utter_message('action_check_logged_for_project_management', tracker)
            dispatcher.utter_message("Please provide me correct value so that I can provide you main task list.")
            
            try:
            
                if project_name_list != []:
                    dispatcher.utter_custom_json(project_name_list)
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    # dispatcher.utter_message("Could you please let me know that which projects would you like to see?")
            
                    return {"project_id": None}
            
                else:
            
                    add_TTE_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("It seems that projects are not assigned to you yet.")
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    return {"project_id": None}, self.deactivate()
                    
            except:
            
                add_TTE_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("It seems that projects are not yet assigned to you.")
                dispatcher.utter_button_message(buttons=notify_button,text=None)
            
                return {"project_id": None}, self.deactivate()
            
        else:
            
            add_TTE_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit.")
            return self.deactivate()
            
    def validate_main_task_id(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of main_task_id', value)
        global wrong_attempt, EMP_ID, resources_project, add_TTE_form_slot,notify_button,task_selection_confirmation_flag,selected_main_task_id,selected_main_task_name
        try:
            project_id = tracker.get_slot("project_id")
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------ first check in main task",intent_name)
            if intent_name == 'request_for_task':
                pass
            elif project_id == "miscellaneous task":
                task_name_list, total_main_task_by_srNo, total_main_task_by_name = get_miscellaneous_task()
                num_tasks = len(task_name_list)
            else:
                task_name_list, total_main_task_by_srNo, total_main_task_by_name = main_task_list_display(project_id)
                num_tasks = len(task_name_list)
        except:
            task_name_list, total_main_task_by_srNo, total_main_task_by_name =  get_miscellaneous_task()
            num_tasks = len(task_name_list)

        try:
            if task_selection_confirmation_flag == "Confirming selected main task name" and selected_main_task_id:
                
                current_intent = tracker.get_intent_of_latest_message()
                print("Inside task_selection_confirmation_flag = Confirming selected main task name")
                task_selection_confirmation_flag = ''
                
                if current_intent == "affirm":
                    value = str(selected_main_task_id)
                    print("Inside affirm path of task_selection_confirmation_flag value:",value)
                    # return value
                elif current_intent == "deny":
                    print("Inside deny path of task_selection_confirmation_flag value:", value)
                    if project_id == "miscellaneous task":
                        task_name_list, total_main_task_by_srNo, total_main_task_by_name = get_miscellaneous_task()
                        num_tasks = len(task_name_list)
                        dispatcher.utter_custom_json(task_name_list)
                        selected_main_task_id = ""
                        selected_main_task_name = ""
                        return {"main_task_id":None}
                    else:
                        task_name_list, total_main_task_by_srNo, total_main_task_by_name = main_task_list_display(project_id)
                        dispatcher.utter_custom_json(task_name_list)
                        dispatcher.utter_button_message(buttons=notify_button,text=None)
                        selected_main_task_id = ""
                        task_selection_confirmation_flag = "Confirming selected main task name after deny"
                        selected_main_task_name = ""
                        return {"main_task_id":None}
            
            else:
                print("Inside else")
                try:
                    if int(value):
                        print("Checking int value----------------------------------------------------------------------------------")
                except:
                    if value in total_main_task_by_srNo.values():
                        print("checking main task code ------------------------------", value)
                    elif task_selection_confirmation_flag == "Confirming selected main task name after deny":
                        print("after denial of selected main task confirming from list")
                        task_selection_confirmation_flag = ""
                        main_task_id, main_task_name = get_best_match(value, total_main_task_by_name)
                        print("main_task_id,main_task_name feched by best match function inside try",main_task_id, main_task_name)
                        selected_main_task_id = main_task_id
                        selected_main_task_name = main_task_name
                        task_selection_confirmation_flag = "Confirming selected main task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Main Task: <b>{main_task_name}</b> for TTE?')
                        return {"main_task_id":None}
                    else:
                        value = tracker.get_slot("main_task_name") if tracker.get_slot("main_task_name") else value[0]
                        print("main_task_name if slot main_task_id is set ,value", value[0])
                        main_task_id, main_task_name = get_best_match(value[0], total_main_task_by_name)
                        print("main_task_id,main_task_name feched by best match function inside try",main_task_id, main_task_name)
                        selected_main_task_id = main_task_id
                        selected_main_task_name = main_task_name
                        task_selection_confirmation_flag = "Confirming selected main task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Main Task: <b>{main_task_name}</b> for TTE?')
                        print("Before slot project id set to be none")
                        return {"main_task_id":None}
                
        except:
            print("No any project name fetched by text")
            print("original value of project name slot:", value)
        try:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name----------------- try check in main task-",intent_name)

            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                wrong_attempt = 0
                return [SlotSet("main_task_id",None),SlotSet("main_task_name",None)]

            elif value in total_main_task_by_name.keys() or value in total_main_task_by_srNo.values() or 0 < int(value) <= num_tasks or int(value) in total_main_task_by_srNo.values():
                
                print("directly validating maintask value ",value)
                wrong_attempt = 0
                
                print(total_main_task_by_name,"total_main_task_by_name")
                print(total_main_task_by_srNo,"total_main_task_by_srNo")

                if value in total_main_task_by_name.keys():
                    main_task_id = total_main_task_by_name[value]
                    selected_main_task_name = value
                    print("main task id if", main_task_id)
                    print("main task id if", selected_main_task_name )
                elif int(value) in total_main_task_by_srNo.values():
                    main_task_id = value
                    print("main task id elif1", main_task_id)
                    
                    try:
                        
                        selected_main_task_name = list(total_main_task_by_name.keys())[list(total_main_task_by_name.values()).index(int(main_task_id))]
                        print(selected_main_task_name, list(total_main_task_by_name.keys()))
                    except:
                        selected_main_task_name = value
                        project_id = "miscellaneous task"
                elif int(value) in total_main_task_by_srNo.values():
                    main_task_id = value
                    print("main task id elif2", main_task_id)
                    selected_main_task_name = list(total_main_task_by_name.keys())[list(total_main_task_by_name.values()).index(int(main_task_id))]
                    print(" selected_main_task_name ",  selected_main_task_name )
                else:
                    main_task_id = total_main_task_by_srNo[int(value)]
                    print("main task id else", main_task_id)
                    try:
                        selected_main_task_name = list(total_main_task_by_name.keys())[list(total_main_task_by_name.values()).index(int(main_task_id))]
                    except:
                        selected_main_task_name = value
                        project_id = "miscellaneous task"

                if project_id == "miscellaneous task": 
                    print("miscalleneous project tasks")
            
                else:
                    try:
                        sub_task_name_list, total_sub_task_by_srNo, total_sub_task_by_name = sub_task_list_display(project_id,main_task_id)
                
                        if sub_task_name_list != []:
                
                            if tracker.get_slot("sub_task_name") != None:

                                print("sub_task by initial text______________________________",tracker.get_slot("sub_task_name"))
                                global selected_sub_task_id,selected_sub_task_name
                                selected_sub_task_name =""
                                add_TTE_form_slot.append("sub_task_id")
                                selected_sub_task_id = ""
                                val = tracker.get_slot("sub_task_name") if tracker.get_slot("sub_task_name") else [None]
                                print("sub_task_name if slot sub_task_id is set ,value", val[0])
                                sub_task_id, sub_task_name = get_best_match(val[0], total_sub_task_by_name)
                                print("sub_task_id,sub_task_name feched by best match function inside try",sub_task_id, sub_task_name)
                                selected_sub_task_id = sub_task_id
                                selected_sub_task_name = sub_task_name
                                task_selection_confirmation_flag = "Confirming selected sub task name"
                                dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Sub Task: <b>{sub_task_name}</b> for TTE?')
                                print("Before slot project id set to be none ==============")
                                # return []
                    
                            else:
                                add_TTE_form_slot.append("sub_task_id")
                                dispatcher.utter_custom_json(sub_task_name_list)
                                dispatcher.utter_button_message(buttons=notify_button,text=None)
                        else:
                            dispatcher.utter_message("Subtasks are not yet allocated to this main task.")
                            # dispatcher.utter_button_message(buttons=notify_button,text=None)
                    except:
                        dispatcher.utter_message("Subtasks are not yet allocated to this main task.")
                        if project_id != "Miscelleneous task":
                            dispatcher.utter_button_message(buttons=notify_button,text=None)
                        else:
                            print("no sub task available to miscelleneous task")
                return {'main_task_id': main_task_id}
            
            elif wrong_attempt < 3:
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                # dispatcher.utter_message('action_check_logged_for_project_management', tracker)
                dispatcher.utter_message("Please provide me correct value so that I can provide you main task list.")
                try:
                    if task_name_list != []:
                        dispatcher.utter_custom_json(task_name_list)
                        dispatcher.utter_message(buttons=notify_button,text=None)
                        return {"main_task_id": None}
                    else:
                        add_TTE_form_slot = []
                        wrong_attempt = 0
                        dispatcher.utter_message("It seems that main tasks are not yet assigned to you.")
                        dispatcher.utter_button_message(buttons=notify_button,text=None)
                        return {"main_task_id": None}, self.deactivate()
                except:
                    add_TTE_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("It seems that main taks are not yet assigned to you.")
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    return {"main_task_id": None}, self.deactivate()
            else:
                add_TTE_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("You reached maximum limit.")
                return self.deactivate()
        except:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                wrong_attempt = 0
                return []
            else:
                dispatcher.utter_message("Something went wrong. Please provide me correct information.")
                return {"main_task_id": None}
    
    def validate_sub_task_id(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of sub_task_id', value)
        
        global wrong_attempt, EMP_ID, resources_project, add_TTE_form_slot,notify_button,selected_sub_task_id,task_selection_confirmation_flag,selected_sub_task_name
        
        project_id = tracker.get_slot("project_id")
        main_task_id = tracker.get_slot("main_task_id")
        task_name_list, total_sub_task_by_srNo, total_sub_task_by_name = sub_task_list_display(project_id,main_task_id)
               
        num_tasks = len(task_name_list)
        
        try:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------ first check in main task",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                return[SlotSet("sub_task_id",None),SlotSet("sub_task_name",None)]
        
            elif task_selection_confirmation_flag == "Confirming selected sub task name" and selected_sub_task_id:
        
                current_intent = tracker.get_intent_of_latest_message()
                print("Inside task_selection_confirmation_flag = Confirming selected sub task name")
                task_selection_confirmation_flag = ''
        
                if current_intent == "affirm":
                    value = str(selected_sub_task_id)
                    print("Inside affirm path of task_selection_confirmation_flag value:",value)
                    # return value
                elif current_intent == "deny":
                    print("Inside deny path of task_selection_confirmation_flag value:", value)
                    task_name_list, total_sub_task_by_srNo, total_sub_task_by_name = sub_task_list_display(project_id,main_task_id)
                    dispatcher.utter_custom_json(task_name_list)
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    task_selection_confirmation_flag = "Confirming selected sub task name after denial"
                    return {"sub_task_id":None}
            else:

                try:

                    if int(value):
                        print("Checking int value----------------------------------------------------------------------------------")
                except:
                    if task_selection_confirmation_flag == "Confirming selected sub task name after denial":
                        task_selection_confirmation_flag = ""
                        print("Confirming sub task after denial")
                        sub_task_id, sub_task_name = get_best_match(value, total_sub_task_by_name)
                        print("main_task_id,main_task_name feched by best match function inside try",sub_task_id, sub_task_name)
                        selected_sub_task_id = sub_task_id
                        selected_sub_task_name = sub_task_name
                        task_selection_confirmation_flag = "Confirming selected sub task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Sub Task: <b>{sub_task_name}</b> for TTE?')
                        return {"sub_task_id":None}
                    else:
                        value = tracker.get_slot("sub_task_name") if tracker.get_slot("sub_task_name") else value[0]
                        print("sub_task_name if slot main_task_id is set ,value", value[0])
                        sub_task_id, sub_task_name = get_best_match(value[0], total_sub_task_by_name)
                        print("main_task_id,main_task_name feched by best match function inside try",sub_task_id, sub_task_name)
                        selected_sub_task_id = sub_task_id
                        selected_sub_task_name = sub_task_name
                        task_selection_confirmation_flag = "Confirming selected sub task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Sub Task: <b>{sub_task_name}</b> for TTE?')
                        print("Before slot project id set to be none")
                        return {"sub_task_id":None}
        except:
            print("No any project name fetched by text")
            print("original value of project name slot:", value)

        try:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                wrong_attempt = 0
                return [SlotSet("sub_task_id",None),SlotSet("sub_task_name",None)]            
            elif value in total_sub_task_by_name.keys() or 0 < int(value) <= num_tasks or int(value) in total_sub_task_by_srNo.values():
                if value in total_sub_task_by_name.keys():
                    sub_task_id = total_sub_task_by_name[value]
                    selected_sub_task_name = value
                elif int(value) in total_sub_task_by_srNo.values():
                    sub_task_id = value
                    selected_sub_task_name = list(total_sub_task_by_name.keys())[list(total_sub_task_by_name.values()).index(int(sub_task_id))]
                else:
                    sub_task_id = total_sub_task_by_srNo[int(value)]
                    selected_sub_task_name = list(total_sub_task_by_name.keys())[list(total_sub_task_by_name.values()).index(int(sub_task_id))]
                wrong_attempt = 0
                try:
                    sub_sub_task_name_list, total_sub_sub_task_by_srNo, total_sub_sub_task_by_name = sub_sub_task_list_display(project_id,main_task_id,sub_task_id)
                    if sub_sub_task_name_list !=[]:
            
                        global selected_sub_sub_task_id,selected_sub_sub_task_name
                        
                        selected_sub_sub_task_name = ""
                        selected_sub_sub_task_id = ""
                        task_selection_confirmation_flag = ""
                        
                        if tracker.get_slot("sub_sub_task_name") != None:
                        
                            print("Inside try of subsubtask fetched from text ")
                            add_TTE_form_slot.append("sub_sub_task_id")
                            val = tracker.get_slot("sub_sub_task_name") if tracker.get_slot("sub_sub_task_name") else 'NA'
                            print("sub_sub_task_name if slot sub_sub_task_id is set ,value", val[0])
                            sub_sub_task_id, sub_sub_task_name = get_best_match(value[0], total_sub_sub_task_by_name)
                            print("sub_sub_task_id,sub_sub_task_name feched by best match function inside try",sub_sub_task_id, sub_sub_task_name)
                            selected_sub_sub_task_id = sub_sub_task_id
                            selected_sub_sub_task_name = sub_sub_task_name
                            task_selection_confirmation_flag = "Confirming selected sub sub task name"
                            dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Sub SubTask: <b>{sub_sub_task_name}</b> for TTE?')
                            print("Before slot sub sub id set to be none +++++++++++++++++++++++")
                            # return []
                        
                        else:                            
                        
                            dispatcher.utter_custom_json(sub_sub_task_name_list)
                            dispatcher.utter_button_message(buttons=notify_button,text=None)
                            add_TTE_form_slot.append("sub_sub_task_id")
                    else:
                       
                        dispatcher.utter_message("Sub SubTask are not yet allocated to this SubTask.")
                        # dispatcher.utter_button_message(buttons=notify_button,text=None)
                                            
                    # "sub_task_name","sub_sub_task_name"
                except:
                    
                    dispatcher.utter_message("Sub SubTask are not yet allocated to this SubTask.")
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    
                return {'sub_task_id': sub_task_id}
            
            elif wrong_attempt < 3:
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                # dispatcher.utter_message('action_check_logged_for_project_management', tracker)
                dispatcher.utter_message("Please provide me correct value so that I can provide you subtask list.")
                try:
                    if task_name_list != []:
                        dispatcher.utter_custom_json(task_name_list)
                        dispatcher.utter_button_message(buttons=notify_button,text=None)
                        # dispatcher.utter_message("Could you please let me know that which projects would you like to see?")
                        return {'sub_task_id': None}
                    else:
                        add_TTE_form_slot = []
                        wrong_attempt = 0
                        dispatcher.utter_message("It seems that subtasks are not yet assigned to you.")
                        dispatcher.utter_button_message(buttons=notify_button,text=None)
                        return {"sub_task_id": None}, self.deactivate()
                except:
                    add_TTE_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("It seems that subtasks are not yet assigned to you .")
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    return {"sub_task_id": None}, self.deactivate()
                
            else:
                
                add_TTE_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("You reached maximum limit.")
                return self.deactivate()
        except:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                wrong_attempt = 0
                return []
            else:
                dispatcher.utter_message("Something went wrong. Please provide me correct information.")
                return {"sub_task_id": None}
    
    def validate_sub_sub_task_id(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of sub_sub__task_name', value)
        
        global wrong_attempt, EMP_ID, resources_project, add_TTE_form_slot,notify_button,selected_sub_sub_task_id,task_selection_confirmation_flag
        
        project_id = tracker.get_slot("project_id")
        main_task_id = tracker.get_slot("main_task_id")
        sub_task_id = tracker.get_slot("sub_task_id")
        task_name_list, total_sub_sub_task_by_srNo, total_sub_sub_task_by_name = sub_sub_task_list_display(project_id,main_task_id,sub_task_id)
   
        num_tasks = len(task_name_list)

        try:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------ first check in main task",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                return[SlotSet("sub_sub_task_id",None),SlotSet("sub_sub_task_name",None)]
        
            elif task_selection_confirmation_flag == "Confirming selected sub sub task name" and selected_sub_sub_task_id:
        
                current_intent = tracker.get_intent_of_latest_message()
                print("Inside task_selection_confirmation_flag = Confirming selected sub sub task name")
                task_selection_confirmation_flag = ''
                if current_intent == "affirm":
                    value = str(selected_sub_sub_task_id)
                    print("Inside affirm path of task_selection_confirmation_flag value:",value)
                    # return value
                elif current_intent == "deny":
                    print("Inside deny path of task_selection_confirmation_flag value:", value)
                    dispatcher.utter_custom_json(task_name_list)
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    task_selection_confirmation_flag = "Confirming selected sub sub task name after denial"
                    return {"sub_sub_task_id":None}
            else:
                try:
                    if int(value):
                        print("Checking int value     ----------------------------------------------------------------------------------")
                except:
                    if task_selection_confirmation_flag == "Confirming selected sub sub task name after denial":
                        task_selection_confirmation_flag = ""
                        print("Confirming sub sub task after denial")
                        sub_sub_task_id, sub_sub_task_name = get_best_match(value,total_sub_sub_task_by_name)
                        print("sub sub _task_id,sub sub_task_name feched by best match function inside try",sub_sub_task_id, sub_sub_task_name)
                        selected_sub_sub_task_id = sub_sub_task_id
                        task_selection_confirmation_flag = "Confirming selected sub sub task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Sub SubTask: <b>{sub_sub_task_name}</b> for TTE?')
                        return {"sub_sub_task_id":None}
                    else:
                        value = tracker.get_slot("main_task_name") if tracker.get_slot("main_task_name") else value[0]
                        print("sub sub _task_name if slot sub sub_task_id is set ,value", value[0])
                        sub_sub_task_id, sub_sub_task_name = get_best_match(value,total_sub_sub_task_by_name)
                        print("sub sub _task_id,sub sub_task_name feched by best match function inside try",sub_sub_task_id, sub_sub_task_name)
                        selected_sub_sub_task_id = sub_sub_task_id
                        task_selection_confirmation_flag = "Confirming selected sub sub task name"
                        dispatcher.utter_button_message(buttons=affirm_deny_button,text=f'Have you selected Sub SubTask: <b>{sub_sub_task_name}</b> for TTE?')
                        print("Before slot sub sub task set to be none")
                        return {"sub_sub_task_id":None}
        except:
            print("No any project name fetched by text")
            print("original value of project name slot:", value)
        try:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                wrong_attempt = 0
                return [SlotSet("sub_sub_task_id",None),SlotSet("sub_sub_task_name",None)]            
            elif value in total_sub_sub_task_by_name.keys() or 0 < int(value) <= num_tasks or int(value) in total_sub_sub_task_by_srNo.values():
            
                if value in total_sub_sub_task_by_name.keys():
                    sub_sub_task_id = total_sub_sub_task_by_name[value]
                    selected_sub_sub_task_name = value
                
                elif int(value) in total_sub_sub_task_by_srNo.values():
                    sub_sub_task_id = value
                    selected_sub_sub_task_name = list(total_sub_sub_task_by_name.keys())[list(total_sub_sub_task_by_name.values()).index(int(sub_sub_task_id))]
                else:
                    sub_sub_task_id = total_sub_sub_task_by_srNo[int(value)]
                    selected_sub_sub_task_name = list(total_sub_sub_task_by_name.keys())[list(total_sub_sub_task_by_name.values()).index(int(sub_sub_task_id))]
                wrong_attempt = 0
                return {'sub_sub_task_id': sub_sub_task_id}
            
            elif wrong_attempt < 3:
                
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                # dispatcher.utter_message('action_check_logged_for_project_management', tracker)
                dispatcher.utter_message("Please provide me correct value so that I can provide you subtask list.")
            
                try:
                    dispatcher.utter_custom_json(task_name_list)
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    # dispatcher.utter_message("Could you please let me know that which projects would you like to see?")
                    return {'sub_sub_task_id': None}
                except:
                    add_TTE_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("It seems that Sub SubTask are not yet assigned to you.")
                    dispatcher.utter_button_message(buttons=notify_button,text=None)
                    return {"sub_sub_task_id": None}, self.deactivate()
            else:
                add_TTE_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("You reached maximum limit.")
                dispatcher.utter_button_message(buttons=notify_button,text=None)
                return self.deactivate()
        except:
            intent_name = tracker.get_intent_of_latest_message()
            print("intent_name------------------",intent_name)
            if intent_name == 'request_for_task':
                add_TTE_form_slot.append("task_description")
                wrong_attempt = 0
                return []
            else:
                dispatcher.utter_message("Something went wrong. Please provide me correct information.")
                return {"sub_sub_task_id": None}
    
    def validate_task_description(self, value, dispatcher, tracker,domain):
    
        print('validate value of task description ', value)
        
        global wrong_attempt, EMP_ID, add_TTE_form_slot

        task_description = tracker.get_slot('task_description')
        print('validate value of task description ', task_description)

        if task_description != None:
            wrong_attempt = 0
            return {'task_description': value} 
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("Please provide me all correct value so that I can proceed.")
            return {'task_description': None} 
            
        else:
            add_TTE_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached maximum limit.")
                    # self.deactivate()
            return [SlotSet("project_id",None),SlotSet("main_task_id",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None)]

class ActionTTESubmit(Action):
        
    def name(self):

        return "action_add_tte_form_submit"

    def run(self, dispatcher, tracker, domain):
        
        global add_TTE_form_slot
        print(len(add_TTE_form_slot),"length_of_tte")
        print('action after getting task details')
        return []

# class ActionGetTTE_details(Action):
    
#     def name(self) -> Text:
#         return "action_getTTE_details"

#     def run(self, dispatcher, tracker, domain):
#         global EMP_ID,TTE_entry_to_Database_form_slot,add_TTE_form_slot, employee_first_name_globally, employee_last_name_globally,email_id1, total_tasks_byID_code,tasks_flag

#         TTE_entry_to_Database_form_slot = []
#         current_intent=tracker.latest_message['intent'].get('name')
#         print(current_intent,"in tte details action")

#         print("taskId_by_code", total_tasks_byID_code)

#         if len(add_TTE_form_slot) > 1:
        
#             if tracker.get_slot("task_description"): 

#                 print("Inside notification action submit")
#                 task_description = tracker.get_slot('task_description')
#                 print("Inside notification send loop task_description", task_description)

#                 print(len(add_TTE_form_slot),"length of slots in add tte")

#                 if tasks_flag == "empty":
                
#                     if len(add_TTE_form_slot) == 5:
#                         task_type = "project"
#                         taskid = tracker.get_slot('project_id')
#                         print("task_id",taskid) 
#                     elif len(add_TTE_form_slot) == 6:
#                         task_type = "maintask"
#                         taskid = tracker.get_slot('main_task_name')
#                         print("task_id",taskid) 
#                     elif len(add_TTE_form_slot) == 7:
#                         taskid = tracker.get_slot('main_task_name')
#                         task_type = "subtask"
#                         taskid = tracker.get_slot('sub_task_name')
#                         print("task_id",taskid)                     
#                 else:
#                     if len(add_TTE_form_slot) == 3:
#                         task_type = "project"
#                         taskid = tracker.get_slot('project_id')
#                         print("task_id",taskid) 
#                     elif len(add_TTE_form_slot) == 4:
#                         task_type = "maintask"
#                         taskid = tracker.get_slot('main_task_name')
#                         print("task_id",taskid) 
#                     elif len(add_TTE_form_slot) == 5:
#                         taskid = tracker.get_slot('main_task_name')
#                         task_type = "subtask"
#                         taskid = tracker.get_slot('sub_task_name')
#                         print("task_id",taskid) 
#                 print("task_id",taskid)


#                 mail_details = requests.get("{}/api/project/maildetails?taskid={}&resid={}&tasktype={}".format(project_module_url,taskid,81,task_type))
#                 mail_details_response = mail_details.json()
#                 print ("notification details", mail_details_response)
#                 if tasks_flag == "empty":
#                     tasks_flag = ""
#                     if len(add_TTE_form_slot) == 5:
#                         task_type = "Main Task"
#                         taskid = tracker.get_slot('project_id')
#                     elif len(add_TTE_form_slot) == 6:
#                         print("request main task")
#                         task_type = "Subtask"
#                         taskid = tracker.get_slot('main_task_name')
#                     elif len(add_TTE_form_slot) == 7:
#                         task_type = "Sub-subtask"
#                         taskid = tracker.get_slot('sub_task_name')
            
#                 else:
#                     if len(add_TTE_form_slot) == 3:
#                         task_type = "Main Task"
#                         taskid = tracker.get_slot('project_id')
#                     elif len(add_TTE_form_slot) == 4:
#                         print("request main task")
#                         task_type = "Subtask"
#                         taskid = tracker.get_slot('main_task_name')
#                     elif len(add_TTE_form_slot) == 5:
#                         task_type = "Sub-subtask"
#                         taskid = tracker.get_slot('sub_task_name')
#                 print("taskid 2nd ",taskid)
#                 try:     
#                     ProjectManager_name = mail_details_response["projectmanagerfname"]
#                     ProjectManager_email = mail_details_response["projectmanageremail"]
#                     task_description = f'{task_description}',
#                     resource_name = mail_details_response["resorucefullname"]
#                     resource_email = mail_details_response["resoruceemail"]
#                     resource_empcode = mail_details_response["resorucecode"]
#                     project_code = mail_details_response["projectcode"]
#                     project_name = mail_details_response["projectname"]
#                     task_type = task_type
#                     main_task_name = mail_details_response["maintaskname"]
#                     main_task_code = mail_details_response["maintaskcode"]
#                     sub_task_name = mail_details_response["subtaskname"]
#                     sub_task_code = mail_details_response["subtaskcode"]
#                     sub_subtask_name = mail_details_response["subsubtaskname"]
#                     sub_subtask_code = mail_details_response["subsubtaskcode"]

#                     data1 = {"PM_name": ProjectManager_name,
#                         "PM_email": "reshma.mule@omfysgroup.com",
#                         "task_description":tracker.get_slot("task_description"),
#                         "resource_name": resource_name,
#                         "resource_email": resource_email,
#                         "resource_empcode": resource_empcode,
#                         "project_code": project_code,
#                         "project_name": project_name,
#                         "task_type": task_type ,
#                         "main_task_name": main_task_name,
#                         "main_task_code": main_task_code,
#                         "sub_task_name": sub_task_name,
#                         "sub_task_code": sub_task_code}

#                     print("fetching data from mail", data1)
#                     data1 = {K:v for K , v in data1.items() if v is not None}
#                     print("after removing null values", data1)
#                     # task_description = tracker.get_slot('task_description')
#                     print("Inside notification send loop task_description", task_description)
#                     response = requests.post("http://13.127.186.145:8000/emailsendtopm/", json= data1)
#                     print("mail_send_url_called", response.text)

#                     if response.text == '"Email Sent"':
#                         dispatcher.utter_message("Notification sent successfully !! Your project manager will get back to you soon.")
#                         return {"task_description":None}
#                     else:
#                         dispatcher.utter_message("Something went wrong! Sorry for incovinience. Please try again")
#                     # return [AllSlotsReset()]
#                     return []
#                 except:
#                     print("details not available")
#                     return [] 
#             else:
#                 global tte_forms
#                 tte_forms = []
#                 tte_forms = []
#                 print("TTE_details")
#                 tte_forms.append({
#                             "type":"Form",
#                             "title":"Please fill following details for task and time entry.",
#                             "fields":
#                                 [   
#                                     {
#                                         "field":"Activity",
#                                         "type":"text",
#                                         "name":"activity",
#                                         "placeholder":"Enter your activity"
#                                     },
#                                     {
#                                         "field":"Start Time",
#                                         "type":"time",
#                                         "name":"start_time",
#                                         "placeholder":" Enter task start time"
#                                     },
#                                     {
#                                         "field":"End Time",
#                                         "type":"time",
#                                         "name":"end_time",
#                                         "placeholder":" Enter task end time"
#                                     },
#                                     {
#                                         "field":"Task Status",
#                                         "type":"dropdown",
#                                         "name":"task_status",
#                                         "placeholder":[{"option":"In Progress","value": "InProgress"},
#                                         {"option":"Completed","value": "Completed"},
#                                         {"option":"Hold","value": "Hold"}]
#                                     },
#                                     {
#                                         "field":"Comment",
#                                         "type":"text",
#                                         "name":"comment",
#                                         "placeholder":" Enter comment here"
#                                     }
                                        
#                                     ]   
#                                 })
#             if tracker.get_slot("task_status") or tracker.get_slot("activity_name") or tracker.get_slot("start_time") or tracker.get_slot("end_time"):
#                 TTE_entry_to_Database_form_slot = ["activity_name","start_time","end_time","task_status"]
#             else:
#                 dispatcher.utter_custom_json(tte_forms)
#                 print("form sent")
#                 TTE_entry_to_Database_form_slot = ['tte_data']
#                 print("TTE_entry_to_Database_form_slot ", TTE_entry_to_Database_form_slot) 
#         else:
#             print("Adding slots")
#             TTE_entry_to_Database_form_slot = ['activity_name','task_status','start_time','end_time']
#             # TTE_entry_to_Database_form_slot = []
        
#         return [FollowupAction('TTE_entry_to_Database_form')] 

class ActionGetTTE_details(Action):
    
    def name(self) -> Text:
        
        return "action_getTTE_details"

    def run(self, dispatcher, tracker, domain):
        
        global EMP_ID,TTE_entry_to_Database_form_slot,task_selection_confirmation_flag, add_TTE_form_slot, employee_first_name_globally, employee_last_name_globally,email_id1, total_tasks_byID_code,tasks_flag
        global tasks_flag 
        tasks_flag = ''
        print("INSIDE action get TTE details")
        
        if len(add_TTE_form_slot) > 1:
            if tracker.get_slot("task_description"): 

                print("Inside notification action submit")
                task_description = tracker.get_slot('task_description')
                print("Inside notification send loop task_description", task_description)

                print(len(add_TTE_form_slot),"length of slots in add tte")

                if tasks_flag == "empty":
                    if len(add_TTE_form_slot) == 5:
                        task_type = "project"
                        taskid = tracker.get_slot('project_id')
                        print("task_id",taskid) 
                    elif len(add_TTE_form_slot) == 6:
                        task_type = "maintask"
                        taskid = tracker.get_slot('main_task_id')
                        print("task_id",taskid) 
                    elif len(add_TTE_form_slot) == 7:
                        task_type = "subtask"
                        taskid = tracker.get_slot('sub_task_id')
                        print("task_id",taskid)                     
                else:
                    if len(add_TTE_form_slot) == 3:
                        task_type = "project"
                        taskid = tracker.get_slot('project_id')
                        print("task_id",taskid) 
                    elif len(add_TTE_form_slot) == 4:
                        task_type = "maintask"
                        taskid = tracker.get_slot('main_task_id')
                        print("task_id",taskid) 
                    elif len(add_TTE_form_slot) == 5:
                        task_type = "subtask"
                        taskid = tracker.get_slot('sub_task_id')
                        print("task_id",taskid) 
                print("task_id",taskid)
                mail_details = requests.get("{}/api/project/maildetails?taskid={}&resid={}&tasktype={}".format(project_module_url,taskid,EMP_ID,task_type))
                mail_details_response = mail_details.json()
                print ("notification details", mail_details_response)
                try:
                    if mail_details_response["errorDescription"] == "Details not available":
                        dispatcher.utter_message("Sorry! this task not belongs to you. Please select your task for TTE.")
                        return []
                except:
                    pass

                if tasks_flag == "empty":
                    tasks_flag = ""
                    if len(add_TTE_form_slot) == 5:
                        task_type = "Main Task"
                        taskid = tracker.get_slot('project_id')
                    elif len(add_TTE_form_slot) == 6:
                        print("request main task")
                        task_type = "Sub Task"
                        taskid = tracker.get_slot('main_task_id')
                    elif len(add_TTE_form_slot) == 7:
                        task_type = "Sub Sub Tasks"
                        taskid = tracker.get_slot('sub_task_id')
                else:
                    if len(add_TTE_form_slot) == 3:
                        task_type = "Main Task"
                        taskid = tracker.get_slot('project_id')
                    elif len(add_TTE_form_slot) == 4:
                        print("request main task")
                        task_type = "Sub Task"
                        taskid = tracker.get_slot('main_task_id')
                    elif len(add_TTE_form_slot) == 5:
                        task_type = "Sub Sub Task"
                        taskid = tracker.get_slot('sub_task_id')
                print("taskid 2nd ",taskid)
                try:     
                    ProjectManager_name = mail_details_response["projectmanagerfname"]
                    ProjectManager_email = mail_details_response["projectmanageremail"]
                    task_description = f'{task_description}',
                    resource_name = mail_details_response["resorucefullname"]
                    resource_email = mail_details_response["resoruceemail"]
                    resource_empcode = mail_details_response["resorucecode"]
                    project_code = mail_details_response["projectcode"]
                    project_name = mail_details_response["projectname"]
                    task_type = task_type
                    main_task_name = mail_details_response["maintaskname"]
                    main_task_code = mail_details_response["maintaskcode"]
                    sub_task_name = mail_details_response["subtaskname"]
                    sub_task_code = mail_details_response["subtaskcode"]
                    sub_subtask_name = mail_details_response["subsubtaskname"]
                    sub_subtask_code = mail_details_response["subsubtaskcode"]

                    data1 = {"PM_name": ProjectManager_name,
                        "PM_email": "reshma.mule@omfysgroup.com",
                        "task_description":tracker.get_slot("task_description"),
                        "resource_name": resource_name,
                        "resource_email": resource_email,
                        "resource_empcode": resource_empcode,
                        "project_code": project_code,
                        "project_name": project_name,
                        "task_type": task_type ,
                        "main_task_name": main_task_name,
                        "main_task_code": main_task_code,
                        "sub_task_name": sub_task_name,
                        "sub_task_code": sub_task_code}

                    print("fetching data from mail", data1)
                    data1 = {K:v for K , v in data1.items() if v is not None}
                    print("after removing null values", data1)
                    # task_description = tracker.get_slot('task_description')
                    print("Inside notification send loop task_description", task_description)
                    response = requests.post("http://13.127.186.145:8000/emailsendtopm/", json= data1)
                    print("mail_send_url_called", response.text)

                    if response.text == '"Email Sent"':
                        dispatcher.utter_message("Notification sent successfully !! Your project manager will get back to you soon.")
                        TTE_entry_to_Database_form_slot = []
                        add_TTE_form_slot = []
                        return [SlotSet("task_description",None),SlotSet("project_name",None),SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None),SlotSet("main_task_name",None),SlotSet("main_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_name",None),SlotSet("sub_sub_task_id",None)]
                    else:
                        dispatcher.utter_message("Something went wrong!!! Sorry for incovinience. Please try again")
                    # return [AllSlotsReset()]
                    return []
                except:
                    print("details not available")
                    return [] 
            else:
                global tte_forms
                tte_forms = []
                print("TTE_details")
                
                tte_forms.append({
                            "type":"Form",
                            "title":"Please fill following details for task and time entry.",
                            "fields":
                                [   
                                    {
                                        "field":"Activity",
                                        "type":"text",
                                        "name":"activity",
                                        "placeholder":"Enter your activity"
                                    },
                
                                    {
                                        "field":"Start Time",
                                        "type":"time",
                                        "name":"start_time",
                                        "placeholder":" Enter task start time"
                                    },
                
                                    {
                                        "field":"End Time",
                                        "type":"time",
                                        "name":"end_time",
                                        "placeholder":" Enter task end time"
                                    },
                
                                    {
                                        "field":"Task Status",
                                        "type":"dropdown",
                                        "name":"task_status",
                                        "placeholder":[{"option":"In Progress","value": "In Progress"},
                                        {"option":"Completed","value": "Completed"},
                                        {"option":"Hold","value": "Hold"}]
                                    },
                
                                    {
                                        "field":"Comment",
                                        "type":"text",
                                        "name":"comment",
                                        "placeholder":" Enter comment here"
                                    }
                                        
                                    ]   
                                })

                if tracker.get_slot("task_status") or tracker.get_slot("activity_name") or tracker.get_slot("start_time") or tracker.get_slot("end_time"):
                    TTE_entry_to_Database_form_slot = ["activity_name","start_time","end_time","task_status"]
                      
                else:
                    dispatcher.utter_custom_json(tte_forms)
                    print("form sent")
                    TTE_entry_to_Database_form_slot = ['tte_data']
                    print("TTE_entry_to_Database_form_slot ", TTE_entry_to_Database_form_slot) 
                # else:
                #     print("Adding slots")
                #     TTE_entry_to_Database_form_slot = ['activity_name','task_status','start_time','end_time']
                #     # TTE_entry_to_Database_form_slot = []
                if TTE_entry_to_Database_form_slot:
                    return [FollowupAction('TTE_entry_to_Database_form')] 
                else:
                    return []


class addTTEtodatabaseForm(FormValidationAction):
    
    def name(self):
        
        return "validate_TTE_entry_to_Database_form"
    
    @staticmethod
    async def required_slots(self,slots_mapped_in_domain, dispatcher , tracker):
        print("Inside validate tte details form required slot")
        global TTE_entry_to_Database_form_slot
        return TTE_entry_to_Database_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("slot mapping")
        
        return 
        {
            "task_status": [
                
                self.from_text()
            ],
            "start_time": [
                
                self.from_text()
            ],
            "end_time": [
                
                self.from_text()
            ],
            "activity_name": [
                
                self.from_text()
            ],
            "tte_data": [
                
                self.from_text()
            ]
        }

     
    def validate_activity_name(self, value, dispatcher, tracker,domain):
        
        global task_selection_confirmation_flag, selected_activity_name
        
        # selected_activity_name = ""        
        current_intent = tracker.get_intent_of_latest_message()
        print("intent inzside tte form validation check activiy")
        if current_intent == "Close_TTE_form": ## tring to close the form
            print("tring to close the TTE form")
            return {"activity_name","NA"}

        if tracker.get_slot('task_description'):
            print("Requesting new task")
            return {"activity_name","NA"}
        
        print('validate value of activity_name', value)

        activity = value.replace("activity","").replace("from",'')
        return {"activity_name",activity}

        # if tracker.get_slot("activity_name"):
        #     value = tracker.get_slot("activity_name")
        

    def validate_task_status(self, value, dispatcher, tracker,domain):
        current_intent = tracker.get_intent_of_latest_message()
        global task_selection_confirmation_flag, selected_task_status
        # selected_task_status = ""
        print('validate value of task_status', value)
        return {"task_status": value}

   
    def validate_start_time(self, value, dispatcher, tracker,domain):
        
        current_intent = tracker.get_intent_of_latest_message()
        global task_selection_confirmation_flag, selected_start_time
        
        # selected_start_time =''
        print('validate value of start_time', value)
        return {"start_time": value}

 
    def validate_end_time(self, value, dispatcher, tracker,domain):

        print('validate value of end_time', value)

        return {"end_time":value}
    
    def validate_comment(self, value, dispatcher, tracker,domain):
        global task_selection_confirmation_flag, selected_comment
        task_selection_confirmation_flag = ''
        selected_comment = ''
        print('validate value of comment', value)
        return {"comment": value}
   

    def validate_tte_data(self, value, dispatcher, tracker,domain):
        
        print('validate value of tte_data ', value)

        activity_name = tracker.get_slot("activity_name")
        status = tracker.get_slot("task_status")
        start_time = tracker.get_slot("start_time")
        end_time = tracker.get_slot("end_time")
        comment = tracker.get_slot("comment") if tracker.get_slot("comment") else 'NA'
        project = tracker.get_slot("project_id")
        maintask = tracker.get_slot("main_task_id")
        print("project,maintask",project,maintask)
        # print(f"Please confirm your activity for TTE,\n<b>Project: {project}</b><b>\nMain Task: {maintask}</b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at {start_time} and finished at {end_time}.\n")
        # dispatcher.utter_message(f"Please confirm your activity for TTE,\n<b>Project: {project}</b><b>\nMain Task: {maintask}</b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at {start_time} and finished at {end_time}.\n")
        
        # prediction = tracker.latest_message
        # entity_type = prediction['entities']
        # print('entity_type',entity_type)
        # print(tracker.get_slot('activity_name'))
        # # print(tracker.get_entity('time'))
        # print(tracker.get_slot('task_status'))
        current_intent = tracker.get_intent_of_latest_message()
        print("intent in TTE data validation loop", current_intent)
        global wrong_attempt, EMP_ID, add_TTE_form_slot,TTE_entry_to_Database_form_slot,tte_forms
        try:
            form_data = tracker.latest_message['text']
            print(form_data.split('|'))
            TTE_form_data = form_data.split('|')
            print("TTE form data  ::",TTE_form_data)
            activity_name =  TTE_form_data[0]  
            start_time = TTE_form_data[1]
            end_time= TTE_form_data[2]
            status = 'In progress' if 'in' in TTE_form_data[3].lower() else TTE_form_data[3]
            comment= TTE_form_data[4]
        except:
            if "|" not in form_data and current_intent == "Close_TTE_form": ## tring to close the form
                print("tring to close the TTE form")
                TTE_form_data = []
                TTE_entry_to_Database_form_slot=[]
                return [SlotSet("main_task_id",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None),SlotSet("main_task_name",None),SlotSet("task_description",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None),SlotSet("tte_data",None)]  

            if "|" not in form_data and current_intent == "request_for_task":
                print("Requesting new task")
                TTE_form_data = []
                TTE_entry_to_Database_form_slot=[]
                add_TTE_form_slot = add_TTE_form_slot.append("task_description")
                dispatcher.utter_template("utter_ask_task_description", tracker)
                return [SlotSet("project_id",None),SlotSet("task_description",None),SlotSet("project_name",None),SlotSet("main_task_id",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None),SlotSet("main_task_name",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None),SlotSet("tte_data",None),FollowupAction("action_getTTE_details")]
            else:
                TTE_form_data = []            
        try:
            if len(TTE_form_data) == 6:

                if activity_name == ""  or start_time == ""  or end_time == ""  or comment == "" and wrong_attempt < 3:
                
                    wrong_attempt = wrong_attempt + 1
                    dispatcher.utter_custom_json(tte_forms)
                    dispatcher.utter_message("Please provide me all correct value so that I can proceed.")
                
                    return {'tte_data': None}

                elif len(TTE_form_data) == 6:
                
                    print(add_TTE_form_slot,"add_TTE_form_slot")
                    wrong_attempt = 0
                
                    return {'tte_data': value}              
            
                elif wrong_attempt < 3:
                    
                    print("wrong_attempt", wrong_attempt)
                    wrong_attempt = wrong_attempt + 1
                    dispatcher.utter_custom_json(tte_forms)
                    dispatcher.utter_message("Please provide me all correct value so that I can proceed.")
                    return {'tte_data': None}
                else:
                   
                    add_TTE_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("You reached maximum limit.")
                    # self.deactivate()
                    return [AllSlotsReset()]

            elif wrong_attempt < 3:
                    print("wrong_attempt", wrong_attempt)
                    wrong_attempt = wrong_attempt + 1
                    dispatcher.utter_custom_json(tte_forms)
                    dispatcher.utter_message("Please provide me all correct value so that I can proceed.")
                    return {'tte_data': None} 
            else:
                    add_TTE_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("You reached maximum limit.")
                    # self.deactivate()
                    return [SlotSet("project_id",None),SlotSet("main_task_id",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None)]
        except:
            TTE_form_data = []

class ActionTTEentry(Action):
    
    def name(self):
        return "TTE_entry_to_Database_form_submit"

    def run(self, dispatcher, tracker, domain):
        
        global add_TTE_form_slot, selected_project_name,selected_main_task_name,selected_sub_task_name,selected_sub_sub_task_name,selected_project_id,selected_main_task_id,selected_sub_task_id,selected_sub_sub_task_id,selected_comment
        print("Inside try TTE_entry_to_Database_form_submit")
        current_intent = tracker.get_intent_of_latest_message()
        try:
            if not tracker.get_slot('tte_data') and not tracker.get_slot("task_description"):
                activity_name = tracker.get_slot("activity_name")
                status = tracker.get_slot("task_status")
                start_time = tracker.get_slot("start_time")
                end_time = tracker.get_slot("end_time")
                start_time = change_time_format(start_time)
                end_time = change_time_format(end_time)
                print('std_time_format:',start_time ,end_time)
                comment = tracker.get_slot("comment") if tracker.get_slot("comment") else "NA"
            else:
                form_data = tracker.get_slot("tte_data")
                print(form_data.split('|'))
                TTE_form_data = form_data.split('|')
                print(TTE_form_data)
                activity_name =  TTE_form_data[0]  
                start_time = TTE_form_data[1]
                end_time= TTE_form_data[2]
                status = 'In progress' if 'in' in TTE_form_data[3].lower() else TTE_form_data[3]
                comment= TTE_form_data[4]
        
                print('std_time_format:',start_time ,end_time)

            # activity_name =selected_activity_name if selected_activity_name else "NA"
            # status = selected_task_status if selected_task_status else "NA"
            # start_time = selected_start_time if selected_start_time else "NA"
            # end_time = selected_end_time if selected_end_time else "NA"
            

            print (f'activity name {activity_name},task status {status},start time {start_time},end time {end_time}')
            selected_project_id = tracker.get_slot("project_id") if tracker.get_slot("project_id") else "NA"
            selected_main_task_id = tracker.get_slot("main_task_id") if tracker.get_slot("main_task_id") else "NA"
            selected_sub_task_id = tracker.get_slot("sub_task_id") if tracker.get_slot("sub_task_id") else "NA"
            selected_sub_sub_task_id = tracker.get_slot("sub_sub_task_id") if tracker.get_slot("sub_sub_task_id") else "NA"
            project, maintask ,subtask, subsubtask= selected_project_id,selected_main_task_id,selected_sub_task_id,selected_sub_sub_task_id 
            print("Inside try TTE_entry_to_Database_form_submit", selected_project_id,selected_main_task_id,selected_sub_task_id,selected_sub_sub_task_id)
            project_name = selected_project_name if selected_project_name else "NA" 
            main_task_name = selected_main_task_name if selected_main_task_name else "NA"
            sub_task_name = selected_sub_task_name if selected_sub_task_name else "NA"
            sub_sub_task_name= selected_sub_sub_task_name if selected_sub_sub_task_name else "NA"
            print("sub_sub_task_name",sub_sub_task_name, selected_sub_sub_task_name)
            confirm_tte_details = confirm_tte_details_html_format(project_name,main_task_name,sub_task_name,sub_sub_task_name,activity_name,status,start_time,end_time) 
            # dispatcher.utter_message(f"You have submited below TTE details:{confirm_tte_details} ")
            # print("table data", confirm_tte_details)
            dispatcher.utter_custom_json(confirm_tte_details)
            # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Project: <b>{selected_project_name}</b><br>\nMain Task: <b>{selected_main_task_name}</b><br>\nSub Task: <b>{selected_sub_task_name}</b><br></b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            # return [SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None),SlotSet("project_name",None),SlotSet("project_id",None),SlotSet("main_task_name",None),SlotSet("main_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_name",None),SlotSet("sub_sub_task_id",None)]
            # return [AllSlotsReset()]
            selected_project_name,selected_main_task_name,selected_sub_task_name,selected_sub_sub_task_name = 'NA','NA','NA','NA'
            try:
                print("Inside action TTE_entry_to_Database_form_submit\n geting all tte_data from text and slot values html form skipped")

                # if any([tracker.get_slot("task_status"),tracker.get_slot("activity_name"),tracker.get_slot("start_time"),tracker.get_slot("end_time")]):
                if status and activity_name and start_time and end_time and comment:
                    taskstatus,activity,start_time,end_time,comment= status,activity_name,start_time,end_time,comment
                    print("Ids",selected_project_id,selected_main_task_id,selected_sub_task_id,selected_sub_sub_task_id)
                    # start_time = change_time_format(start_time)
                    # end_time = change_time_format(end_time)
                    print('std_time_format:',start_time , end_time)
                    if len(add_TTE_form_slot) == 2:
                        if tracker.get_slot('project_id') == 'miscellaneous task':
                            print("add miscellaneous task entry")
                            response_TTEentry = requests.get('{}/api/project/entermisctte?task_code={}&activity={}&start_time={}&end_time={}&comment={}&empid={}&taskStatus={}'.format(project_module_url,selected_main_task_id,activity,start_time,end_time,comment,EMP_ID,taskstatus))
                            print(response_TTEentry.status_code)
                        else:
                            print("add main task entry; {}/api/project/entertte?maintaskcode={}&activity={}&start_time={}&end_time={}&comment={}&emp_id={}&taskstatus={}".format(project_module_url,selected_main_task_id,activity,start_time,end_time,comment,EMP_ID,taskstatus))
                            response_TTEentry = requests.get('{}/api/project/entertte?maintaskcode={}&activity={}&start_time={}&end_time={}&comment={}&emp_id={}&taskstatus={}'.format(project_module_url,selected_main_task_id,activity,start_time,end_time,comment,EMP_ID,taskstatus))
                            print(response_TTEentry.status_code)
                    elif len(add_TTE_form_slot) == 3:
                        print("add sub task entry")
                        response_TTEentry = requests.get('{}/api/project/entertte?subtaskcode={}&activity={}&start_time={}&end_time={}&comment={}&emp_id={}&taskstatus={}'.format(project_module_url,selected_sub_task_id,activity,start_time,end_time,comment,EMP_ID,taskstatus))
                        print(response_TTEentry.status_code)
                    
                    elif len(add_TTE_form_slot) == 4:
                        print("add sub sub task entry")
                        response_TTEentry = requests.get('{}/api/project/entertte?subsubtaskcode={}&activity={}&start_time={}&end_time={}&comment={}&emp_id={}&taskstatus={}'.format(project_module_url,selected_sub_sub_task_id,activity,start_time,end_time,comment,EMP_ID,taskstatus))
                        print(response_TTEentry.status_code)
                    else:
                        print("Inside else databse entry")
            
                    print(response_TTEentry)
                    data_TTE = response_TTEentry.json()
                    print(data_TTE)
                    if data_TTE[ "errorCode"] == "200" and data_TTE["errorDescription"].lower() == "successfully time sheet added":
                        dispatcher.utter_message("The task and time entry done successfully.")
                        # return [AllSlotsReset()]  
                        return [SlotSet("project_name",None),SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None),SlotSet("main_task_name",None),SlotSet("main_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_name",None),SlotSet("sub_sub_task_id",None)]

                    else:
                        dispatcher.utter_message("Opps!!! Something went wrong with connection. Please try again.")
                        # return [AllSlotsReset()]
                        return [SlotSet("project_name",None),SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None),SlotSet("main_task_name",None),SlotSet("main_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_name",None),SlotSet("sub_sub_task_id",None)]
                else:
                    pass
                    return []
            except:
                pass
                return []
            
            # print(f"Please confirm your activity for TTE,\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at {start_time} and finished at {end_time}.\n")
            # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Activty to be added is <b>{activity_name}</b><br>Task Status is <b>{status}</b><br>You started working on the activity from {start_time} and finished at {end_time}.\n")     
            
            # try:
            #     project = tracker.get_slot("project_id") 
            #     maintask = tracker.get_slot("main_task_name")
            #     subtask = tracker.get_slot("sub_task_name")
            #     print("Inside try TTE_entry_to_Database_form_submit", project,maintask,subtask)
            #     # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Project: <b>{project}</b><br>\nMain Task: <b>{maintask}</b><br>\nSub Task: <b>{subtask}</b><br></b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            #     print(f"Please confirm your activity for TTE,\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at {start_time} and finished at {end_time}.\n")
            #     dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Activty to be added is <b>{activity_name}</b><br>Task Status is <b>{status}</b><br>You started working on the activity from {start_time} and finished at {end_time}.\n")     

            #     return [SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None)]  

            #     # subsubtask = tracker.get_slot("sub_task_name") 
            #     # project, maintask ,subtask, subsubtask= project , maintask ,subtask , subsubtask 
            #     # print(project, maintask,subtask,subsubtask)
            #     # print(f"Please confirm your activity for TTE,<br>Project: <b>{project}</b><br>\nMain Task: <b>{maintask}</b><br>\nSub Task: <b>{subtask}</b><br>\nSub Sub Task: <b>{subsubtask}</b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            #     # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Project: <b>{project}</b><br>\nMain Task: <b>{maintask}</b><br>\nSub Task: <b>{subtask}</b><br>\nSub Sub Task: <b>{subsubtask}</b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            #     # return [SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None)]  
            # except:
            #     print('string not contain project name')
            #     print(f"Please confirm your activity for TTE,\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            #     dispatcher.utter_message(f"Please confirm your activity for TTE,\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            #     add_TTE_form_slot.append('project_id')
            #     return add_TTE_form_slot
                # project, maintask ,subtask, subsubtask= 1,2,3,4
            # print("project,maintask,subtask,subsubtask",project, maintask, subtask, subsubtask)
            # print(f"Please confirm your activity for TTE,<br>Project: <b>{project}</b><br>\nMain Task: <b>{maintask}</b><br>\nSub Task: <b>{subtask}</b><br>\nSub Sub Task: <b>{subsubtask}</b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
            # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Project: <b>{project}</b><br>\nMain Task: <b>{maintask}</b><br>\nSub Task: <b>{subtask}</b><br>\nSub Sub Task: <b>{subsubtask}</b>\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at <b>{start_time}</b> and finished at <b>{end_time}</b>.\n")
    
            # print(f"Please confirm your activity for TTE,\nActivty to be added is <b>{activity_name}</b>\nTask is <b>{status}</b>\nYou started it at {start_time} and finished at {end_time}.\n")
            # dispatcher.utter_message(f"Please confirm your activity for TTE,<br>Activty to be added is <b>{activity_name}</b><br>Task Status is <b>{status}</b><br>You started working on the activity from {start_time} and finished at {end_time}.\n")     

            # return [SlotSet("activity_name",None),SlotSet("task_status",None),SlotSet("start_time",None),SlotSet("end_time",None),SlotSet("tte_data",None),add_TTE_form_slot]  
        except:
            if tracker.get_slot("task_description") and current_intent == "request_for_task":
                print("Request for task selected by user")
                TTE_form_data = []
                TTE_entry_to_Database_form_slot=[]
                add_TTE_form_slot = add_TTE_form_slot.append("task_description")
                dispatcher.utter_template("utter_ask_task_description", tracker)
                return [SlotSet("project_id",None),SlotSet("task_description",None),SlotSet("project_name",None),SlotSet("main_task_id",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None),SlotSet("main_task_name",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None),SlotSet("tte_data",None), FollowupAction("action_getTTE_details")]
            if current_intent == "Close_TTE_form":
                print("Close the form selected by user")
                TTE_form_data = []
                TTE_entry_to_Database_form_slot=[]
                return [SlotSet("main_task_id",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None),SlotSet("main_task_name",None),SlotSet("task_description",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None),SlotSet("tte_data",None)]  

class ActionTTEentry(Action):
    
    def name(self):
        return "action_reset"

    def run(self, dispatcher, tracker, domain):

        print("Inside action reset")
        global add_TTE_form_slot
        add_TTE_form_slot = []

        return [SlotSet("project_id",None),SlotSet("main_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None),SlotSet("tte_data",None)]  

class ActionCheckLoginStatus(Action):
    
    def name(self):
        return 'action_check_login_status'

    def run(self, dispatcher, tracker, domain):
        # emp_code = "OMI-1036"
        # password = "Omfys@123"
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

        global required_slots_list
        required_slots_list = ["start_date",
                               "end_date",
                               "leave_type",
                               "purpose",
                               "hand_over_Employee",
                               "knowledge_summary"]

        intent = tracker.latest_message['intent'].get('name')

        login_stauts = False

        if emp_code is None or password is None:
            print("returning false")
            return [SlotSet('login_status', False)]
        else:
            print("returning true")
            return [SlotSet('login_status', True)]

class ActionbackTo_lastproject(Action):
    def name(self):
        return "action_backTo_lastproject"

    def run(self, dispatcher, tracker, domain):
        global add_TTE_form_slot
        add_TTE_form_slot = ['project_id']
        print("Inside action reset")
        return [SlotSet("project_name"),SlotSet("main_task_id",None),SlotSet("main_task_name",None),SlotSet("sub_task_id",None),SlotSet("sub_sub_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None),SlotSet("tte_data",None)]


class ActionCheckLoggedForMainMenu(Action):
    def name(self):
        return 'action_check_logged_for_main_menu'

    def run(self, dispatcher, tracker, domain):
        # emp_code = 'OMI-1036'
        # password = 'Omfys@123'
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

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

class ActionLogout(Action):
    def name(self):
        return 'action_logout'

    def run(self, dispatcher, tracker, domain):
        # emp_code = 'OMI-1036'
        # password = 'Omfys@123'
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        print("password ", password)

        # emp_code = emp_code.upper()
        print("employee code inside logout", emp_code)

        if emp_code != None and password != None:
            print("Inside if ")
            return [SlotSet('logout_status', False), SlotSet('emp_code', None), SlotSet('password', None)]

        else:
            print("Inside else ")
            return [SlotSet('logout_status', True)]

        return []

class ActionRestart(Action):
    
    def name(self):
        return "action_restart"

    def run(self, dispatcher, tracker, domain):

        print("Inside action restart")
        
        dispatcher.utter_message("Successfully logged out!")
        return [AllSlotsReset()]  
    
class Actiontask_descriptionSlot(Action):
        
    def name(self):
        return "action_add_task_description_slot"

    def run(self, dispatcher, tracker, domain):
        global add_TTE_form_slot
        current_intent = tracker.get_intent_of_latest_message()
        print("Inside action task_description_slot intent", current_intent,"task description",tracker.get_slot("task_description"))
        if tracker.get_slot("task_description") != None:
            add_TTE_form_slot.append('task_description')
            print("Inside action add_task_description_slot user has requested for task")
        else:
            print("Inside action add_task_description_slot not requested for task")
            pass
        print("Inside action add_task_description_slot")
        return [] 


# class addTTEtodatabaseForm(FormValidationAction):
    
#     def name(self):
        
#         return "validate_request_for_task_form"
    
#     @staticmethod
#     async def required_slots(self,slots_mapped_in_domain, dispatcher , tracker):
#         print("Inside required slot")
#         global request_for_task_form_slot
#         request_for_task_form_slot = ['task_description']
#         return request_for_task_form_slot
        
    
#     def validate_task_description(self, value, dispatcher, tracker,domain):
        
#         print('validate value of task description ', value)
        
#         global wrong_attempt, EMP_ID, request_for_task_form_slot


#         if task_description != None:
        
#             wrong_attempt = 0
#             return {'task_description': value} 
        
#         elif wrong_attempt < 3:
        
#             print("wrong_attempt", wrong_attempt)
#             wrong_attempt = wrong_attempt + 1
#             dispatcher.utter_custom_json(tte_forms)
#             dispatcher.utter_message("Please provide me all correct value so that I can proceed.")
#             return {'task_description': None} 
            
#         else:
        
#             add_TTE_form_slot = []
#             wrong_attempt = 0
#             dispatcher.utter_message("You reached to maximum limit.")
#                     # self.deactivate()
#             return [SlotSet("project_id",None),SlotSet("main_task_id",None),SlotSet("sub_task_name",None),SlotSet("sub_sub_task_name",None)]
        

# class ActionRequestfortask(Action):
    
#     def name(self):
        
#         return "request_for_task_form_submit"

#     def run(self, dispatcher, tracker, domain):

#         print("Inside action submit")

#         global add_TTE_form_slot, employee_first_name_globally,employee_last_name_globally,email_id1

#         response = requests.get("{}/api/project?projectId={}&empId={}".format(project_module_url,tracker.get_slot('project_id'),EMP_ID))
#         data = response.json()
#         projectManager  = data[0]['projectManager']
#         projectCode  = data[0]['projectCode']
#         projectName  = data[0]['projectName']
#         task_description = tracker.get_slot('task_description')

#         if data['resources'][0]['role'] == "Project Manager":

#             projectManager_emp_code = data['resources'][0]['resourceEmpCode']
#             response = requests.get(
#             '{}/empCodeCheck?emp_code={}'.format(mindsconnect_url,projectManager_emp_code))

#             data =  response.json()
#             project_manager_email_id = str(data['emp_id']['email'])

#         print(employee_first_name_globally,employee_last_name_globally)

#         # response = requests.get(
#         #     '{}/empCodeCheck?emp_code={}'.format(mindsconnect_url,tracker.get_slot('emp_code')))

#         # data = response.json()
#         # EMP_ID = str(data['emp_id']['emp_id'])
#         # print('EMP_ID from validate ', EMP_ID)

#         # global employee_first_name_globally
#         # employee_first_name_globally = str(data['emp_id']['emp_first_name'])
#         # print('Employee first name ', str(data['emp_id']['emp_first_name']))

#         # global employee_last_name_globally
#         # employee_last_name_globally = str(data['emp_id']['emp_last_name'])
#         # print('Employee last name ', str(data['emp_id']['emp_last_name']))
#         # email_id1 = str(data['emp_id']['email'])

#         email_input = {}
#         if len(add_TTE_form_slot) == 2:

#             task_type = "Main Task"
                        
#         elif len(add_TTE_form_slot) == 3:

#             print("request main task")
#             main_response = requests.get("{}/api/project/mtasks?projectId={}&empId={}".format(project_module_url,tracker.get_slot('project_id'),EMP_ID))
#             main_data = main_response.json()
#             main_task_code  = main_data[0]['taskcode']
#             main_task_name = main_data[0]['task_name']

#             print("main task_code",main_task_code)
#             print("request sub task")
#             task_type = "Subtask"

#             email_input + {
#             "main_task_name":f"{main_task_name}",
#             "main_task_code": f"{main_task_code}"
#             }
            
#         elif len(add_TTE_form_slot) == 4:

#             main_response = requests.get("{}/api/project/mtasks?projectId={}&empId={}".format(project_module_url,tracker.get_slot('project_id'),EMP_ID))
#             main_data = main_response.json()
#             main_task_code  = main_data[0]['taskcode']
#             main_task_name = main_data[0]['task_name']
            
#             sub_response = requests.get("{}/api/project/mtask/stasks?projectId={}&empId={}&mainTaskId={}".format(project_module_url,tracker.get_slot('project_id'),EMP_ID,tracker.get_slot('main_task_id')))
#             sub_data = sub_response.json()
#             sub_task_code  = sub_data[0]['taskcode']
#             sub_task_name  = sub_data[0]['task']
#             print("task_code",sub_task_code)

#             task_type = "Sub-subtask"

#             email_input + {
#             "main_task_name":f"{main_task_name}",
#             "main_task_code": f"{main_task_code}",
#             "sub_task_name":f"{sub_task_name}",
#             "sub_task_code":f"{sub_task_code}"
#             }
#         project_manager_email_id = "sharada.pawar@omfysgroup.com"
#         email_input + {
#             "PM_name": f"{projectManager}",
#             "PM_email": f"{project_manager_email_id}",
#             "resource_name": f"{employee_first_name_globally} {employee_last_name_globally}",
#             "resource_email": f"{email_id1}",
#             "resource_empcode": f"{tracker.get_slot('emp_code')}",
#             "project_code": f"{projectCode}",
#             "project_name": f"{projectName}",
#             "task_description": f"{task_description}",
#             "task_type": f"{task_type}"
#             }

#         email_input_data = json.dumps(email_input)

#         url = f"{API_URL_Django}/emailsendtopm/"

#         print(email_input_data)
        
#         email_response = requests.post(url=url,data = email_input_data)

#         print("post api response",response.status_code)
        
#         if email_response.text == "Email sent":
        
#             dispatcher.utter_message("Your task request sent successfully. Your project manager will get back to you soon")
        
#         return [AllSlotsReset()]  