# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
from distutils.cmd import Command
from pickle import NONE
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import datetime as dt
import requests
from typing import Dict, Text, Any, List, Union, Optional
# from urlvalidator import URLValidator, ValidationError
from pyrsistent import optional
from rasa_sdk import FormValidationAction
from rasa_sdk.types import DomainDict
import re
from datetime import datetime, date, timedelta
from rasa_sdk.forms import REQUESTED_SLOT, FormAction
import dateparser
import parsedatetime as pdt
from dateutil.relativedelta import relativedelta
import calendar
import time
from spacy.language import Language
from spacy.vocab import Vocab
from spacy.language import Language




global emp_code_collect_form_slots
emp_code_collect_form_slots = []
global wrong_emp_code1_attempt
wrong_emp_code1_attempt = 0
global confirmation_box

EMP_ID = 0

leave_days = 0

other_emp_code = []

LIST_LR_ID = []



count = 0
wrong_ordinal_attempt = 0
wrong_command_attempt = 0

required_slots_list = ["form_data"
# ,"start_date",
#                        "end_date",
#                        "leave_type",
#                        "purpose",
#                        "hand_over_Employee",
#                        "knowledge_summary"
                       ]

# list of required slots  ### changes found recheck 
# required_slots_list = ["start_date",   
#                        "end_date",
#                        "leave_type",
#                        "purpose",
#                        "hand_over_Employee",
#                        "knowledge_summary"
#                        ]
# mindsconnect_url = "https://mindsconnect.omfysgroup.com" #Production
# mindsconnect_url = "http://10.0.0.25:8088/MINDS_CONNECT"
# mindsconnect_url = "http://43.231.254.81/MINDS_CONNECT"
# mindsconnect_url = "http://43.231.254.81/MINDSCONNECT"
# mindsconnect_url = "http://106.201.234.246/MINDSCONNECT"
# mindsconnect_url = "http://103.109.13.198/MINDSCONNECT"
#mindsconnect_url = "http://103.109.13.198/OLD_MINDSCONNECT" #UAT
# mindsconnect_url = "https://mindsconnect.omfysgroup.com"
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
# project_module_url = "http://103.109.13.198/project-management"
# production url
# project_module_url = "https://mindsconnect.omfysgroup.com/project_mngt/"
cmc_url = "https://cmc.omfysgroup.com"
project_module_url = "http://103.119.160.114/project_mngt"
#mindsconnect_url ="http://103.119.160.114/MINDSCONNECT" #"http://103.109.13.198/MINDSCONNECT" # https://uat-java.omfysgroup.com/MINDSCONNECT/
#mindsconnect_url ='https://uat.omfysgroup.com/mindsconnect_objective/'
#PRODUCTION URL
mindsconnect_url ="https://mindsconnect.omfysgroup.com/"





#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

# class ActionUserLogin(Action):
    
#     def name(self):
#         return "action_get_login_details"

#     def run(self, dispatcher, tracker, domain):
        
#         global login_slot
#         global EMP_ID,EMP_name,EMP_last_name,emp_code,password
#         # emp_code = 'OMI-1036'
#         # password = 'Omfys@123'
#         # EMP_ID = 3 #0 for FR and AR id
#         login_slot = ['emp_code','password']
#         print("inside action_get_login_details")
#         try:
#             print("Inside action_get_login_details user login submit")

#             response = requests.get(
#             '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code,password))
#             if len(login_slot)> 0 and response.json() != None:
#                 response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, emp_code))
#                 data = response.json()
#                 EMP_name = str(data['emp_id']['emp_first_name'])
#                 EMP_last_name = str(data['emp_id']['emp_last_name'])
#                 print(EMP_name)
#                 # global email_id1
#                 # email_id1 = str(data['emp_id']['email'])
#                 dispatcher.utter_message("Hi {} ".format(EMP_name))
#                 buttons = {"title":"Leave Mgmt.","payload":"leaves"},{"title":"Exit","payload":"logout"}
#                 dispatcher.utter_message(buttons=buttons,text="Congratulations! You are to avail my assistance. You can choose features to get started or type in a direct message.")
#                 dispatcher.utter_message(buttons=buttons,text="Congratulations! You are to avail my assistance. You can choose features to get started or type in a direct message.")
#                 return [SlotSet('emp_code', emp_code), SlotSet('password', password)]
#             else:
#                 dispatcher.utter_template("utter_greet",tracker)
#                 return [SlotSet('emp_code', None), SlotSet('password', None)]
#         except:
#             dispatcher.utter_template("utter_greet",tracker)
#             return [SlotSet('emp_code',None),SlotSet('password',None)]





class ActionGetListOfPendingApproval(Action):
    def name(self):
        return 'action_get_list_of_pending_approval'

    def run(self, dispatcher, tracker, domain):
        global emp_code_collect_form_slots
        try:
            #here emp code is the employee code of loggedIn user that user should be AR/FR
            response = requests.get(
                "{}/PendingLeaveApprovals?emp_code={}".format(mindsconnect_url, tracker.get_slot('emp_code')))
            print("Leave pending",response)
            data = response.json()
            print("data",data)
            print("len",len(data))
            leaves_count = len(data)
            gt = []
            global confirmation_box
            global confirmation_box_emp_code
            confirmation_box = {}
            confirmation_box_emp_code = {}
            global other_emp_code_dict
            other_emp_code_dict = {}
            global confirmation_box_slot
            try:
                print("leavecount",leaves_count)
                print("data",data)
                for particular_leave in range(0, leaves_count):
                    print("particular_leave",particular_leave)
                    confirmation_box.update({"{}".format(particular_leave + 1): [data[particular_leave]['emp_name'],
                                                                                 data[particular_leave]['leave_type'],
                                                                                 dt.datetime.strptime(
                                                                                     data[particular_leave][
                                                                                         'start_date'],
                                                                                     "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                                                     "%d/%m/%Y"), dt.datetime.strptime(
                            data[particular_leave]['end_date'],
                            "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"), data[particular_leave]['reason_for_leave'],
                                                                                 data[particular_leave]['Emp_code'],
                                                                                 data[particular_leave]['leave_count'],
                                                                                 data[particular_leave]['lr_id']]})
                    other_emp_code_dict.update({data[particular_leave]['Emp_code']: data[particular_leave]['lr_id']})
                    confirmation_box_emp_code.update(
                        {data[particular_leave]['Emp_code']: [data[particular_leave]['emp_name'],
                                                              data[particular_leave]['leave_type'],
                                                              dt.datetime.strptime(
                                                                  data[particular_leave]['start_date'],
                                                                  "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                                              dt.datetime.strptime(
                                                                  data[particular_leave]['end_date'],
                                                                  "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                                              data[particular_leave]['reason_for_leave'],

                                                              data[particular_leave]['Emp_code'],
                                                              data[particular_leave]['leave_count'],
                                                              data[particular_leave]['lr_id']]})
                    gt.append({
                        "type": "List",
                        "level": "third level",
                        "lr_id": data[particular_leave]['lr_id'],
                        "emp1_code": data[particular_leave]['Emp_code'],
                        "title": "Following are the leave requests pending for approval. You can approve/reject leave by providing employee code or serial number. Only one leave can approved/rejected at a time.",
                        "number": particular_leave,
                        "links":
                            [
                                {
                                    "display_text": "more",
                                    "more_link":
                                        " {} {} {} {} {} {}".format(
                                            (particular_leave + 1),
                                            data[particular_leave]['Emp_code'],
                                            data[particular_leave]['emp_name'],
                                            data[particular_leave]['leave_type'],
                                            dt.datetime.strptime(data[particular_leave]['start_date'],
                                                                 "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                            dt.datetime.strptime(data[particular_leave]['end_date'],
                                                                 "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                            data[particular_leave]['reason_for_leave']),
                                    "link_href":
                                        (data[particular_leave]['Emp_code']),

                                    "button":
                                        [
                                            {
                                                "title": "Approve",
                                                "payload": "approve"

                                            },
                                            {
                                                "title": "Reject",
                                                "payload": "reject"

                                            }
                                        ]

                                }
                            ]
                    }
                    )
                print("gt",gt)
                dispatcher.utter_custom_json(gt)
                global User_asked_before_intent
                User_asked_before_intent = tracker.latest_message['intent'].get('name')
                print("User_asked_before_intent",User_asked_before_intent)
                confirmation_box_slot = ['ordinal', 'command']
            except:
                if data['errorDesc'] == "No applications exists!":
                    dispatcher.utter_message("There is no leave requests are pending with me for approval.")
                    confirmation_box_slot = []
                    emp_code_collect_form_slots = []
                else:
                    dispatcher.utter_message(data['errorDesc'])
                confirmation_box_slot = []
                emp_code_collect_form_slots = []
                print(confirmation_box)
                print("456")
                print(confirmation_box_emp_code)
        except:
            confirmation_box_slot = []

            emp_code_collect_form_slots = []
        print(confirmation_box)
        print("245")
        print(confirmation_box_emp_code)
        return [SlotSet('command',None),SlotSet('empCodeForleaveRequest',None),SlotSet('reason',None),SlotSet('ordinal',None),SlotSet('name2',None),SlotSet('emp_code1',None)]


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
        
        
        #response = requests.get('{}empCodeCheck?emp_code={}'.format(mindsconnect_url, emp_code))
        #data = response.json()
        #EMP_name = (data["jd"]['emp_id']['emp_first_name'])
        #EMP_last_name = str(data['emp_id']['emp_last_name'])
        #EMP_ID = (data["jd"]['emp_id']['emp_id'])
        #print("emp_id",EMP_ID)
        #print(EMP_name)
        #print("EMP Id Show",EMP_ID)
        # print("setting employee code is", emp_code)
        #print("password is", password)
        dispatcher.utter_message(text="Login successfully")
        return [SlotSet('emp_code',emp_code),SlotSet('password',password)]

                                  # user login form
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
        print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        response = requests.get(
            '{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, value))

        # print('emp code response is ', response.json())
        global wrong_emp_code_count

        if response.json() != None:
            data = response.json()
            global EMP_ID
            EMP_ID = str(data['emp_id']['emp_id'])
            print('EMP_ID from validate ', EMP_ID)

            global employee_first_name_globally
            employee_first_name_globally = str(data['emp_id']['emp_first_name'])
            print('Employee first name ', str(data['emp_id']['emp_first_name']))

            global employee_last_name_globally
            employee_last_name_globally = str(data['emp_id']['emp_last_name'])
            print('Employee last name ', str(data['emp_id']['emp_last_name']))
            return {'emp_code': value}

        else:
            dispatcher.utter_template('utter_wrong_emp_code', tracker)
            return {"emp_code": None}

    def validate_password(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of password  ', value)
        print("Inside validate emp id; emp code :", tracker.get_slot("emp_code"),"password:", tracker.get_slot("password"))
        global wrong_password_attempt, login_slot

        response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, tracker.get_slot('emp_code'), value))
        data = response.json()
        # print("login data;",data)
        if data != None :
            try:
                if data["errorCode"]==208 and data['errorMsg'] == "Failed." :
                    print("password not matched")
                    wrong_password_attempt = wrong_password_attempt + 1
                    dispatcher.utter_template('utter_wrong_password', tracker)
                    return {"password": None}
            except:
                print("I am in except loop password matched")
                wrong_password_attempt = 0
                return {"password": value}
                
        elif wrong_password_attempt < 3:
            print("wrong_password_attempt", wrong_password_attempt)
            wrong_password_attempt = wrong_password_attempt + 1
            dispatcher.utter_template('utter_wrong_password', tracker)
            return {"password": None}
        else:
            login_slot = []
            wrong_password_attempt = 0
            dispatcher.utter_message("Login failed. You reached to maximum login limit.")
            return self.deactivate()


                                             # user login action
class ActionUserLogin(Action):
    
    def name(self):
        return "action_user_login_form_submit"

    def run(self, dispatcher, tracker, domain):
        global login_slot
        global EMP_ID,EMP_name,EMP_last_name
        try:
            response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format( mindsconnect_url, tracker.get_slot('emp_code'),tracker.get_slot('password')))
            if len(login_slot)> 0 and response.json() != None:

                response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, tracker.get_slot('emp_code')))
                data = response.json()
                EMP_name = str(data['emp_id']['emp_first_name'])
                EMP_last_name = str(data['emp_id']['emp_last_name'])
                print(EMP_name)
                global email_id1
                email_id1 = str(data['emp_id']['email'])

                print("Inside submit")
                global count
                if count == 1:
                    print("inside if login")
                    print("Employee name {}".format(EMP_name))
                    response = requests.get(
                        "{}/PendingLeaveApprovals?emp_code={}".format(mindsconnect_url, tracker.get_slot('emp_code')))
                    print(response)
                    data = response.json()
                    print(data)
                    print(len(data))
                    leaves_count = len(data)
                    dispatcher.utter_template('utter_help_user_after_loggedin', tracker)
                    return [SlotSet('pending_leaves',leaves_count)]
                else:
                    count = 1
                    print("Inside else login")
                    emp_code = tracker.get_slot('emp_code')
                    print('Employee code:submit ', emp_code)
                    password = tracker.get_slot('password')
                    print('Employee password:submit ', password)
                    print("Employee name {}".format(EMP_name))
                    response = requests.get(
                    "{}/PendingLeaveApprovals?emp_code={}".format(mindsconnect_url, tracker.get_slot('emp_code')))
                    print(response)
                    data = response.json()
                    print(data)
                    print(len(data))
                    leaves_count = len(data)
                    dispatcher.utter_message("Hi {} ".format(EMP_name))
                    # dispatcher.utter_template('utter_help_sub_menu', tracker)
                    return []
            else:
                dispatcher.utter_template("utter_greet",tracker)
                return [SlotSet('emp_code', None), SlotSet('password', None)]
        except:
            dispatcher.utter_template("utter_greet",tracker)
            return [SlotSet('emp_code',None),SlotSet('password',None)]

class ActionCheckLogin(Action):
    def name(self):
        return 'action_check_login'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            # emp_code = emp_code.upper()
            print("employee code ", emp_code)

            # Calling API to get profile info

            # Working url in office to get emp_id

            response = requests.get(
                '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

            # Working url get leave balance

            try:

                data = response.json()

                global EMP_ID,EMP_name,EMP_last_name

                # global LR_ID
                EMP_ID = str(data['emp_id']['emp_id'])
                EMP_name = str(data['emp_id']['emp_first_name'])
                EMP_last_name = str(data['emp_id']['emp_last_name'])
                email_id = str(data['emp_id']['email'])
                print("email id", email_id)
                print('EMP_ID ', EMP_ID)

                print("Class:ActionCheckLogin data for login check \n\n", data)

                if emp_code is None or password is None:
                    raise Exception('I know Python!')
                elif emp_code  == " " or password  == " ":
                    raise Exception('I know Python!')
                elif data is None:
                    raise Exception('I know Python!')
                else:
                    response = requests.get(
                        "{}/PendingLeaveApprovals?emp_code={}".format(mindsconnect_url, tracker.get_slot('emp_code')))
                    print(response)
                    data = response.json()
                    print(data)
                    print(len(data))
                    leaves_count = len(data)
                    dispatcher.utter_message("Hi {} ".format(EMP_name))
                    dispatcher.utter_template("utter_help_user", tracker)

            except Exception:
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password), SlotSet('pending_leaves', leaves_count)]




class ActionCheckLoginStatus(Action):
    
    def name(self):
        return 'action_check_login_status'

    def run(self, dispatcher, tracker, domain):
        
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
            print("returning false 123")
            return [SlotSet('login_status', False)]
        else:
            print("returning true 123")
            # dispatcher.utter_message("utter_help_sub_menu")
            return [SlotSet('login_status', True)]

                                # ShowAprrovedLeaves

class ActionShowAprrovedLeaves(Action):

    def name(self):
        return "action_show_approved_leaves"

    def run(self, dispatcher, tracker, domain):
        end_date,start_date = None,None
        try:
            tracker.get_slot('daterange')
            date1 = tracker.get_slot('daterange')
            print("111")
            print(date1)
            print("333")
            start_date = date1['start_date']
            print('start_date',date1['start_date'])
            end_date = date1['end_date']
            print('end_date', date1['end_date'])
            print('end_date', date1['end_date'])
        except:
            # pass
            start_date = (dt.datetime.now()).strftime("%d/%m/%Y")
            print('start_date', start_date)
            print("sss")
            end_date = (dt.datetime.now()).strftime("%d/%m/%Y")
            print('end_date', end_date)
            print("www")


        response1 = requests.get(
            '{}/getAllApprovedLeaveList?emp_code={}'.format(mindsconnect_url,tracker.get_slot('emp_code')))
        print(response1)
        data1 = response1.json()
        print(data1)
        print(len(data1))
        global approved_leaves
        approved_leaves = {}
        global display_approved_month
        display_approved_month = []
        try:
            for approved_leave in data1:
                approved_leaves.update({approved_leave['LR_Id']:[approved_leave['applicant_Name'],dt.datetime.strptime(approved_leave['start_date'],"%b %d, %Y").strftime("%d/%m/%Y"),dt.datetime.strptime(approved_leave['end_date'],"%b %d, %Y").strftime("%d/%m/%Y"),approved_leave['leave_type'],approved_leave['reason_for_leave']]})
        except:
            dispatcher.utter_message(data1['errorDesc'])
        try:
            array_count_month = 1
            for key in approved_leaves.keys():
                print("approved_leaves[key][1]",approved_leaves[key][1])
                print("approved_leaves[key][2]",approved_leaves[key][2])
                if start_date <= approved_leaves[key][1] and end_date >= approved_leaves[key][2] or start_date <= approved_leaves[key][2]  and end_date != None:

                    print("start_date <= approved_leaves[key][1]",start_date <= approved_leaves[key][1])
                    print("end_date >= approved_leaves[key][2]", end_date >= approved_leaves[key][2])
                    display_approved_month.append("{}. {} From {} to {} ".format(array_count_month,
                        approved_leaves[key][0],
                        dt.datetime.strptime(approved_leaves[key][1],
                                                                                     "%Y-%m-%d").strftime(
                                                                                     "%d/%m/%Y"),
                        dt.datetime.strptime(
                                                                                     approved_leaves[key][2],
                                                                                     "%Y-%m-%d").strftime(
                                                                                     "%d/%m/%Y")))
                    array_count_month = array_count_month + 1

                elif start_date <= approved_leaves[key][1] or end_date <= approved_leaves[key][2] or start_date <= approved_leaves[key][2]  and end_date != None:
                    print("start_date == approved_leaves[key][1]", start_date == approved_leaves[key][1])
                    print("end_date == approved_leaves[key][2]", end_date == approved_leaves[key][2])
                    display_approved_month.append("{}. {} From {} to {} ".format(array_count_month,
                        approved_leaves[key][0],
                         dt.datetime.strptime(approved_leaves[key][1],
                                                                                     "%Y-%m-%d").strftime(
                                                                                     "%d/%m/%Y"),
                        dt.datetime.strptime(
                                                                                     approved_leaves[key][2],
                                                                                     "%Y-%m-%d").strftime(
                                                                                     "%d/%m/%Y")))
                    array_count_month = array_count_month + 1


        except:
            if start_date == None and end_date == None:
                print("end_date == None", end_date == None)
                for key in approved_leaves.keys():

                    display_approved_month.append(("{}. {} From:{} To:{} ".format(array_count_month,
                        approved_leaves[key][0],
                         dt.datetime.strptime(approved_leaves[key][1],"%Y-%m-%d").strftime("%d/%m/%Y"),
                        dt.datetime.strptime( approved_leaves[key][2],"%Y-%m-%d").strftime("%d/%m/%Y"))))
                    array_count_month = array_count_month + 1

        if len(display_approved_month) != 0:
            approved_leaves = "<b>Employee/s on leave:</b>"
            for i in range(0,len(display_approved_month)):
                approved_leaves = approved_leaves + '<br><br>'+display_approved_month[i]
            dispatcher.utter_message(approved_leaves)

        else:
            pass
        dispatcher.utter_template("utter_continue_leaves_service", tracker)
        return [SlotSet("daterange",None)]

class ConfirmationBoxForm(FormValidationAction):

    def name(self):
        return "validate_confirmationBoxform"

    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        # print("hh")
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot confirmation box")
        print("ok")
        global confirmation_box_slot
        return confirmation_box_slot
        print("yes")

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping")
        return {

            "ordinal":
                [
                    self.from_entity(entity="ordinal"),
                    self.from_text(intent="approve_reject_one_leave"),
                    self.from_text()
                ],
            "command":
                [
                    self.from_entity(entity="command"),
                    self.from_text(intent="emp_code_i"),
                    self.from_text()
                ]
        }

    def validate_ordinal(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:
        global wrong_ordinal_attempt
        global confirmation_box_slot
        try:
            print("validate ordinal inside if value", value)
            sr_no = value

        except:
            print("validate ordinal inside except value", value[1])
            sr_no = value[1]
        try:
            if sr_no in confirmation_box.keys() or sr_no in other_emp_code_dict.keys():
                print("inside if validate")
                try:
                    buttons = []
                    num = sr_no
                    buttons.append({"title": "Approve",
                                    "payload": "approve"})
                    buttons.append({"title": "Reject",
                                    "payload": "rejected"})
                    print(confirmation_box[num])
                    dispatcher.utter_button_message(
                        "<b>Employee code:</b> {}<br><b>Name:</b> {}<br><b>Type of leave:</b> {}<br><b>From: </b> {}<br><b>To:</b> {}<br><b>Number of days:</b> {}<br><b>Reason of leave:</b> {}".format(
                            confirmation_box[num][5], confirmation_box[num][0], confirmation_box[num][1],
                            confirmation_box[num][2], confirmation_box[num][3], confirmation_box[num][6],
                            confirmation_box[num][4]), buttons)
                    message = tracker.latest_message
                    print(message)

                except:
                    buttons = []
                    num = sr_no
                    buttons.append({"title": "Approve",
                                    "payload": "approve"})
                    buttons.append({"title": "Reject",
                                    "payload": "rejected"})
                    print(confirmation_box_emp_code[num])
                    dispatcher.utter_button_message(
                        "<b>Employee code: </b>{}<br><b>Name:</b> {}<br><b>Type of leave:</b> {}<br><b>From:</b> {}<br><b>To:</b> {}<br><b>Number of days:</b> {}<br><b>Reason of leave:</b> {}".format(
                            confirmation_box_emp_code[num][5], confirmation_box_emp_code[num][0],
                            confirmation_box_emp_code[num][1],
                            confirmation_box_emp_code[num][2], confirmation_box_emp_code[num][3],
                            confirmation_box_emp_code[num][6],
                            confirmation_box_emp_code[num][4]), buttons)
                    message = tracker.latest_message
                    print(message)
                wrong_ordinal_attempt = 0
                return {"ordinal": sr_no}
            elif wrong_ordinal_attempt < 3:
                print("wrong_ordinal_attempt", wrong_ordinal_attempt)
                wrong_ordinal_attempt = wrong_ordinal_attempt + 1
                dispatcher.utter_message("You have asked for the leave which is not available")
                return {"ordinal": None}
            else:

                confirmation_box_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt")
                wrong_ordinal_attempt = 0
                return self.deactivate()
        except:
            if wrong_ordinal_attempt < 3:
                print("wrong_ordinal_attempt", wrong_ordinal_attempt)
                wrong_ordinal_attempt = wrong_ordinal_attempt + 1
                dispatcher.utter_message("You have asked for the leave which is not available")
                return {"ordinal": None}
            else:


                confirmation_box_slot = []
                wrong_ordinal_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt")
                return self.deactivate()

    def validate_command(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of command ', value)
        global confirmation_box_slot
        global wrong_command_attempt
        if value.lower() in ["approve","rejected"]:
            print("inside if validate commmand confirm")
            wrong_command_attempt = 0
            return {"command": value}

        elif value in ["No","nope","no"] and wrong_command_attempt < 3:
            buttons = []
            buttons.append({"title": "Approve",
                            "payload": "approve"})
            buttons.append({"title": "Reject",
                            "payload": "rejected"})
            dispatcher.utter_button_message(
                "Good. I am waiting for your decision for above leave", buttons)
            print("wrong_emp_code1_attempt", wrong_command_attempt)
            wrong_command_attempt = wrong_command_attempt + 1
            return {"command": None}

        elif value in ["Yes","yes","yup"]:
            dispatcher.utter_message("Could you provide me your expectation from me?")
            confirmation_box_slot = []
            wrong_command_attempt = 0
            return self.deactivate()

        elif tracker.latest_message['intent'].get('name') is not "approve_reject_one_leave" or tracker.latest_message['intent'].get('name') is not "emp_code_i":
            buttons = []
            buttons.append({"title": "Yes",
                            "payload": "Yes"})
            buttons.append({"title": "No",
                            "payload": "No"})
            dispatcher.utter_button_message("Do you want me to get out of leave approval process switch to your other expectation?", buttons)


        else:
            confirmation_box_slot = []
            wrong_command_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()

class ActionConfirmationBox_Submit(Action):
    
    def name(self):
        return "action_confirmationBoxform_submit"

    def run(self, dispatcher, tracker, domain):
        print("Inside submit of confirmation")
        global confirmation_box_slot,confirmation_box
        if len(confirmation_box_slot) > 0:
            num = tracker.get_slot('ordinal')
            print(num)
            empCodeForleaveRequest = tracker.get_slot('empCodeForleaveRequest')
            print(empCodeForleaveRequest)
            global emp_code_collect_form_slots
            emp_code_collect_form_slots = ['command', 'empCodeForleaveRequest', 'reason']
            print("submit detail")
            try:
                print(confirmation_box[num][5],'confirmation_box[num][5]')
                return [SlotSet('empCodeForleaveRequest', confirmation_box[num][5])]
            except:
                return [SlotSet('empCodeForleaveRequest', num)]

        else:
            emp_code_collect_form_slots = []

            return []

class ActionConfirmationBox(Action):
    def name(self):
        return 'action_show_confirmation_box'

    def run(self, dispatcher, tracker, domain):
        print("action_show_confirmation_box")

        return []

  #                                            # list slot-

class EmpCodeCollectionForm(FormValidationAction):

    def name(self):
        return "validate_emp_code_collect_form"

    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot emp code emp")
        Command = tracker.get_slot('command')
        print(tracker.get_slot('command'))
        global emp_code_collect_form_slots
        try:
            if (Command.lower() == 'approve') or (Command.lower() == 'rejected'):
                print("Inside IF OF required slot")
                return ['command', 'empCodeForleaveRequest']
            else:
                print("inside else required slots 1")
                return emp_code_collect_form_slots
        except:
            print("inside else required slots 2")
            return emp_code_collect_form_slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping")
        return {

            "command":
            [
                self.from_entity(entity="command"),
                self.from_text(intent="emp_code_i"),
                self.from_text()
            ],
            "empCodeForleaveRequest":
                [
                    self.from_text(intent="emp_code_i"),
                    self.from_text()
                ],
            "reason":
                [
                    self.from_text()
                ]
        }

    def validate_command(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of command ', value)
        if value  == "approve" or "rejected":
            print("inside if validate commmand coderequest")

            return {"command": value}

        else:
            dispatcher.utter_template('utter_wrong_command',tracker)
            return {"command": None}


    def validate_empCodeForleaveRequest(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print("validate empCodeForleaveRequest value", value)
        value.upper()
        global other_emp_code_dict
        try:
            if value in other_emp_code_dict.keys():
                print("inside if validate validate empCodeForleaveRequest ",value)
                return {"empCodeForleaveRequest": value}
            else:
                dispatcher.utter_template('utter_wrong_empCodeForleaveRequest',tracker)
                return {"empCodeForleaveRequest": None}
        except:
            dispatcher.utter_template('utter_wrong_empCodeForleaveRequest',tracker)
            return {"empCodeForleaveRequest": None}

    def validate_reason(
                self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                domain: Dict[Text, Any]) -> Optional[Text]:

        print("validate reason value", value)
        value.upper()
        global other_emp_code_dict
        try:
            if value is not None:
                print("inside if validate")
                return {"reason": value}
        except:
            dispatcher.utter_message('Please enter reason of rejection', tracker)
            return {"reason": None}
                



class ActionEmpCodeCollection(Action):
    
    def name(self):
        return "action_emp_code_collect_form_submit"

    def run(self, dispatcher, tracker, domain):
        global emp_code_collect_form_slots
        if len(emp_code_collect_form_slots) < 1:
            dispatcher.utter_template("utter_profile_information",Tracker)
            
        else:
            lr_id = (tracker.get_slot('empCodeForleaveRequest'))
            command = tracker.get_slot('command')
            reason = tracker.get_slot('reason')
            print("Inside submit of lr id")
            print(lr_id)
            print(command)
            print(reason)


        print("submit detail")

        return []

                                        # value get checked


class ActionGetCheckedValue(Action):
    def name(self):
        return 'action_get_checked_values'

    def run(self, dispatcher, tracker, domain):

        if len(emp_code_collect_form_slots) > 0:
            empCodeForleaveRequest = tracker.get_slot('empCodeForleaveRequest')
            print(tracker.get_slot('empCodeForleaveRequest'))
            global User_asked_before_intent
            print(User_asked_before_intent)
            try:
                global other_emp_code_dict
                print(other_emp_code_dict)
                if empCodeForleaveRequest in other_emp_code_dict.keys():
                    lr_id = other_emp_code_dict[empCodeForleaveRequest]
                    print("lr_id", lr_id)
                    print("emp_code", empCodeForleaveRequest)
                    print(tracker.get_slot('emp_code'))
                    if tracker.get_slot('command') == "rejected":
                        parameters_to_approve_api = f"""
                                                                           mindsconnect url  = {mindsconnect_url} \n
                                                                           emp_code = {tracker.get_slot('emp_code')} \n
                                                                           emp_code1 = {empCodeForleaveRequest} \n
                                                                           lr_id = {lr_id} \n
                                                                           # action = {tracker.get_slot('command')} \n
                                                                           reason = {tracker.get_slot('reason')} \n
                                                                           """
                        print(f"Parameters of reject API \n : {parameters_to_approve_api}")
                        response = requests.get(
                            "{}/approveRejectLeaveAPI?emp_code={}&emp1_code={}&lr_id={}&action=reject&comment={}".format(
                                mindsconnect_url, tracker.get_slot('emp_code'), empCodeForleaveRequest, lr_id,
                                tracker.get_slot('command'), tracker.get_slot('reason')))
                        print("second hit 1", response)
                        data1 = response.json()
                        print(data1)
                        print(User_asked_before_intent)
                        if data1['errorCode'] is 0:
                            dispatcher.utter_message("I have rejected this leave successfully!!")
                            buttons.append({"title": "Yes",
                                    "payload": "leave requests"})
                            buttons.append({"title": "No",
                                    "payload": "home"})
                            dispatcher.utter_button_message("Do you want to continue with leave approve process?", buttons)
                            return []
                            # return [FollowupAction('action_get_list_of_pending_approval')]
                        elif data1['errorCode'] is 1:
                            response2 = requests.get(
                            "{}/approveRejectLeaveAPI?emp_code={}&emp1_code={}&lr_id={}&action=reject&comment={}".format(
                                mindsconnect_url, tracker.get_slot('emp_code'), empCodeForleaveRequest, lr_id,
                                tracker.get_slot('command'), tracker.get_slot('reason')))
                            print("second hit 2", response2)
                            data2 = response2.json()
                            print(data2)
                            if data2['errorCode'] is 0:
                                dispatcher.utter_message("I have rejected this leave successfully!!")
                                buttons.append({"title": "Yes",
                                    "payload": "leave requests"})
                                buttons.append({"title": "No",
                                    "payload": "home"})
                                dispatcher.utter_button_message("Do you want to continue with leave approve process?", buttons)
                                return []
                                # return [FollowupAction('action_get_list_of_pending_approval')]
                            else:
                                print(1015)
                                dispatcher.utter_message(data1['errorDesc'])
                                dispatcher.utter_template("utter_continue_leaves_service",tracker)



                        else:
                            print(1022)
                            dispatcher.utter_message(data1['errorDesc'])
                            dispatcher.utter_template("utter_continue_leaves_service",tracker)


                    elif tracker.get_slot('command') == "approve":
                        parameters_to_approve_api = f"""
                                mindsconnect url  = {mindsconnect_url} \n
                                emp_code = {tracker.get_slot('emp_code')} \n
                                emp_code1 = {empCodeForleaveRequest} \n
                                lr_id = {lr_id} \n
                                action = {tracker.get_slot('command')} \n
                                reason = {tracker.get_slot('reason')} \n
                                    """
                        print(f"Parameters of approve API \n : {parameters_to_approve_api}")
                        response = requests.get(
                            "{}/approveRejectLeaveAPI?emp_code={}&emp1_code={}&lr_id={}&action={}&comment={}".format(
                                mindsconnect_url, tracker.get_slot('emp_code'), empCodeForleaveRequest, lr_id,
                                tracker.get_slot('command'), tracker.get_slot('reason')))
                        print(response)
                        data1 = response.json()
                        print(data1)
                        if data1['errorCode'] is 0:
                            response2 = requests.get(
                            "{}/approveRejectLeaveAPI?emp_code={}&emp1_code={}&lr_id={}&action={}&comment={}".format(
                                mindsconnect_url, tracker.get_slot('emp_code'), empCodeForleaveRequest, lr_id,
                                tracker.get_slot('command'), tracker.get_slot('reason')))
                            print("second hit 3", response2)
                            dispatcher.utter_message("I have approved this leave successfully!!")
                            buttons = []
                            buttons.append({"title": "Yes",
                                    "payload": "leave requests"})
                            buttons.append({"title": "No",
                                    "payload": "home"})
                            dispatcher.utter_button_message("Do you want to continue with leave approve process?", buttons)
                            return []
                            # return [FollowupAction('action_get_list_of_pending_approval')]
                        elif data1['errorCode'] is 1:
                            response2 = requests.get(
                            "{}/approveRejectLeaveAPI?emp_code={}&emp1_code={}&lr_id={}&action={}&comment={}".format(
                                mindsconnect_url, tracker.get_slot('emp_code'), empCodeForleaveRequest, lr_id,
                                tracker.get_slot('command'), tracker.get_slot('reason')))
                            print("second hit 4", response2)
                            data2 = response2.json()
                            print(data2)
                            if data2['errorCode'] is 0:
                                dispatcher.utter_message("I have approved this leave successfully!!")
                                #dispatcher.utter_message("I have approved this leave successfully!!")
                                buttons = []
                                buttons.append({"title": "Yes",
                                    "payload": "leave requests"})
                                buttons.append({"title": "No",
                                    "payload": "home"})
                                dispatcher.utter_button_message("Do you want to continue with leave approve process?", buttons)
                                return []
                                # return [FollowupAction('action_get_list_of_pending_approval')]
                            else:
                                print(1080)
                                dispatcher.utter_message(data1['errorDesc'])
                                dispatcher.utter_template("utter_continue_leaves_service",tracker)



                        else:
                            print(1086)
                            dispatcher.utter_message(data1['errorDesc'])
                            dispatcher.utter_template("utter_continue_leaves_service",tracker)
                    else:
                        print(1090)
                        dispatcher.utter_message("Your have given serial number ")
                        dispatcher.utter_template("utter_continue_leaves_service",tracker)
            except:
                print(1094)
                # dispatcher.utter_message("Your have given serial number")
                dispatcher.utter_template("utter_continue_leaves_service",tracker)

        else:
            buttons = []
            buttons.append({"title": "Yes",
                            "payload": "leave requests"})
            buttons.append({"title": "No",
                            "payload": "home"})
            dispatcher.utter_button_message("Do you want to continue with leave approve process?", buttons)

            return [SlotSet('command',None),SlotSet('empCodeForleaveRequest',None),SlotSet('reason',None),SlotSet('ordinal',None),SlotSet('name2',None),SlotSet('emp_code1',None)]
                   
                   # single validate form

class SingleApprovalForm(FormValidationAction):

    def name(self):
        return "validate_single_approval_form"

    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot of employee detail")
        global single_approval_form_slot
        single_approval_form_slot = ["emp_code1"]
        return single_approval_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("slot mapping")

        return {
            "emp_code1": [
                self.from_entity(entity="emp_code1",intent=["asking_for_one_leave"]),
                self.from_text(intent="data"),
                self.from_text()
            ]

        }

    def validate_emp_code1(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                           domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of emp_code1', value)
        global wrong_emp_code1_attempt

        response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, value))
        data = response.json()
       

        print('other emp code response is ', response.json())
        if response.json() != None:
            wrong_emp_code1_attempt = 0
            return {'emp_code1': value}
        elif wrong_emp_code1_attempt < 3:
            dispatcher.utter_template('utter_wrong_other_emp_code', tracker)
            print("wrong_emp_code1_attempt",wrong_emp_code1_attempt)
            wrong_emp_code1_attempt = wrong_emp_code1_attempt + 1
            return {"emp_code1": None}
        else:

            global single_approval_form_slot
            single_approval_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_emp_code1_attempt = 0
            return self.deactivate()


class ActionSingleApprovalForm(Action):
    
    def name(self):
        return "action_single_approval_form_submit"

    def run(self, dispatcher, tracker, domain):

        global single_approval_form_slot
        if len(single_approval_form_slot)<1:
            dispatcher.utter_template("utter_profile_information",Tracker)
            return [SlotSet("emp_code1", None)]
        else:
            
            print("Inside submit of pending leave form")

            print("submit detail")

            return []

class ActionOnePendingApproval(Action):
    def name(self):
        return 'action_get_one_pending_approval'

    def run(self, dispatcher, tracker, domain):
        global emp_code_collect_form_slots
        try:

            global confirmation_box_slot
            response = requests.get("{}/PendingLeaveApproval?emp_code={}&emp1_code={}".format(mindsconnect_url,
                                                                                              tracker.get_slot(
                                                                                                  'emp_code'),
                                                                                              tracker.get_slot(
                                                                                                  'emp_code1')))
            print(response)
            data = response.json()
            print(data)
            print(len(data))
            leaves_count = len(data)
            gt = []
            global confirmation_box
            confirmation_box = {}
            global confirmation_box_emp_code
            confirmation_box_emp_code = {}
            global other_emp_code_dict
            other_emp_code_dict = {}
            try:

                for particular_leave in range(0, leaves_count):
                    confirmation_box.update({"{}".format(particular_leave + 1): [data[particular_leave]['emp_name'],
                                                                                 data[particular_leave]['leave_type'],
                                                                                 dt.datetime.strptime(
                                                                                     data[particular_leave][
                                                                                         'start_date'],
                                                                                     "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                                                     "%d/%m/%Y"), dt.datetime.strptime(
                            data[particular_leave]['end_date'],
                            "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"), data[particular_leave]['reason_for_leave'],
                                                                                 tracker.get_slot(
                                                                                     'emp_code1'),
                                                                                 data[particular_leave]['leave_count'],
                                                                                 data[particular_leave]['lr_id']]})
                    other_emp_code_dict.update({tracker.get_slot(
                        'emp_code1'): data[particular_leave]['lr_id']})
                    confirmation_box_emp_code.update(
                        {tracker.get_slot('emp_code1'): [data[particular_leave]['emp_name'],
                                                         data[particular_leave]['leave_type'],
                                                         dt.datetime.strptime(
                                                             data[particular_leave][
                                                                 'start_date'],
                                                             "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                             "%d/%m/%Y"), dt.datetime.strptime(
                                data[particular_leave]['end_date'],
                                "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                                         data[particular_leave]['reason_for_leave'], tracker.get_slot(
                                'emp_code1'), data[particular_leave]['leave_count'], data[particular_leave]['lr_id']]})
                    gt.append({
                        "type": "List",
                        "level": "third level",
                        "lr_id": data[particular_leave]['lr_id'],
                        "emp1_code": tracker.get_slot('emp_code1'),
                        "title": "Following are the leave requests pending for approval. You can approve/reject leave by providing serial number. Only one leave can approved/rejected at a time.",
                        "number": particular_leave,
                        "links":
                            [
                                {
                                    "display_text": "more",
                                    "more_link":
                                        " {} {} {} {} {} {}".format(
                                            particular_leave + 1,
                                            tracker.get_slot('emp_code1'),
                                            data[particular_leave]['emp_name'],
                                            data[particular_leave]['leave_type'],
                                            dt.datetime.strptime(data[particular_leave]['start_date'],
                                                                 "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                            dt.datetime.strptime(data[particular_leave]['end_date'],
                                                                 "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                            data[particular_leave]['reason_for_leave']),

                                    "link_href":
                                        (tracker.get_slot('emp_code1')),

                                    "button":
                                        [
                                            {
                                                "title": "Approve",
                                                "payload": "approve"

                                            },
                                            {
                                                "title": "Reject",
                                                "payload": "reject"

                                            }
                                        ]

                                }
                            ]
                    }
                    )
                print(gt)
                dispatcher.utter_custom_json(gt)
                global User_asked_before_intent
                User_asked_before_intent = tracker.latest_message['intent'].get('name')
                print(User_asked_before_intent)
                confirmation_box_slot = ['ordinal', 'command']
            except:
                if data['errorDesc'] == "No applications exists!":
                    dispatcher.utter_message("There is no leave requests are pending with me for approval 1.")
                else:
                    dispatcher.utter_message(data['errorDesc'])

                confirmation_box_slot = []
                emp_code_collect_form_slots = []
            print(confirmation_box_emp_code)
            print(confirmation_box)
            print("000")
        except:

            confirmation_box_slot = []
            emp_code_collect_form_slots = []
        print(confirmation_box_emp_code)
        print(confirmation_box)
        print("666")
        return [SlotSet('command',None),SlotSet('empCodeForleaveRequest',None),SlotSet('reason',None),SlotSet('ordinal',None),SlotSet('name2',None),SlotSet('emp_code1',None)]

        

class SingleApprovalNameForm(FormValidationAction):

    def name(self):
        return "validate_single_approval_name_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot of single approval")
        global single_approval_name_form_slot
        single_approval_name_form_slot = ["name2"]
        return single_approval_name_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("slot mapping")

        return {
            "name2": [

                self.from_entity(entity="PERSON"),
                self.from_entity(entity="ORG"),
                self.from_entity(entity="name2"),
                self.from_text(intent="login_data"),
                self.from_text(intent="asking_for_one_leave_by_name"),
                self.from_text()
            ]

        }

    def validate_name2(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                           domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of name2', value)
        global wrong_name2_attempt
        global name_of_employee
        global valid
        
        u = value.upper()
        print("name value",value)
        print(u.rfind('OMI-'))
        
        try:
        
            print(name_of_employee.values(),"name_of_employee")
            if u.title() in list(name_of_employee.values()) or u.title() in list(name_of_employee.keys()):
                print(u.title()," u.title()")
                print("name_of_employee[u.title()]",name_of_employee[u.title()])
                valid = "true"
            else:
                print("Given name is not available in name of employee")
        
        except:
            valid = "false"
            print("No name")

        if valid == "true":
            wrong_name2_attempt = 0
            valid = ""
            return {"name2": name_of_employee[u.title()]}
    
        elif u.rfind('OMI-') == 0:
            print("inside if validate other employee code")
            wrong_name2_attempt = 0
            valid = ""
            return {"name2": u}
        
        else:
            response = requests.get("{}/empDetails?empdata={}".format(mindsconnect_url,value))
            data = response.json()
            print("employee count ",len(data))
            len1 = (len(data))
            
            try:
                if len(data) > 1:
                    if valid == "select employee":
                        pass
                    else:
                        name_of_employee = {}
                    
                        if len(data[0]) is 11:
                            valid = "select employee"
                            buttons = []
                            print(f"multiple employees are present of name {value}")
                            for number in range(len1):
                                name_of_employee.update({f"{data[number]['emp_first_name']} {data[number]['emp_last_name']}":f"{data[number]['emp_code']}"})
                                buttons.append({"title": f"{data[number]['emp_first_name']} {data[number]['emp_last_name']}","payload": f"{data[number]['emp_code']}"})

                            dispatcher.utter_button_message("Could you please select appropriate name of employee", buttons)
                                # dispatcher.utter_message("please enter employee code of colleague for whom you want to know about ")
                    return {"name2": None}
                elif len(data) == 1:
                    print("only one employee with name ",value)
                    wrong_name2_attempt = 0
                    valid = ""
                    return {"name2": data[0]['emp_code']}

                elif wrong_name2_attempt < 3:
                    dispatcher.utter_template('utter_wrong_name2', tracker)

                    print("wrong_name2_attempt", wrong_name2_attempt)
                    wrong_name2_attempt = wrong_name2_attempt + 1
                    return {"name2": None}
                else:
                    global single_approval_name_form_slot
                    single_approval_name_form_slot
                    wrong_name2_attempt = 0
                    dispatcher.utter_message("You have reached to maximum limit of attempt")
                    return self.deactivate()
            except:
                dispatcher.utter_message(data['errorDesc'])
                dispatcher.utter_template("utter_leave_information",Tracker)
                valid = ""
                return {"name2": value}
            

class ActionSingleApprovalNameForm(Action):
    
    def name(self):
        return "action_single_approval_name_form_submit"

    def run(self, dispatcher, tracker, domain):
        global single_approval_name_form_slot
        if len(single_approval_name_form_slot) < 1:
            dispatcher.utter_template("utter_profile_information",Tracker)
            return [SlotSet("name2",None)]
        else:
            
            global emp_code_collect_form_slots,confirmation_box_slot
            try:
                response = requests.get("{}/PendingLeaveApproval?emp_code={}&emp1_code={}".format(mindsconnect_url,
                                                                                                tracker.get_slot(
                                                                                                    'emp_code'),
                                                                                                tracker.get_slot(
                                                                                                    'name2')))
               
                print(response,"response of leave of particular employee")
                data = response.json()
                print(data,"data go from Api")
                print(len(data),"length of data")
                leaves_count = len(data)
                gt = []
                global confirmation_box
                confirmation_box = {}
                global confirmation_box_emp_code
                confirmation_box_emp_code = {}
                global other_emp_code_dict
                other_emp_code_dict = {}
                global confirmation_box_slot
                try:
                    for particular_leave in range(0, leaves_count):
                        print("particular_leave",particular_leave)
                        confirmation_box.update({"{}".format(particular_leave + 1): [data[particular_leave]['emp_name'],
                                                                                    data[particular_leave]['leave_type'],
                                                                                    dt.datetime.strptime(
                                                                                        data[particular_leave][
                                                                                            'start_date'],
                                                                                        "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                                                        "%d/%m/%Y"), dt.datetime.strptime(
                                data[particular_leave]['end_date'],
                                "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"), data[particular_leave]['reason_for_leave'],
                                                                                    tracker.get_slot(
                                                                                        'name2'),
                                                                                    data[particular_leave]['leave_count'],
                                                                                    data[particular_leave]['lr_id']]})
                        other_emp_code_dict.update({tracker.get_slot(
                            'name2'): data[particular_leave]['lr_id']})
                        confirmation_box_emp_code.update({tracker.get_slot('name2'): [data[particular_leave]['emp_name'],
                                                                                    data[particular_leave]['leave_type'],
                                                                                    dt.datetime.strptime(
                                                                                        data[particular_leave][
                                                                                            'start_date'],
                                                                                        "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                                                        "%d/%m/%Y"), dt.datetime.strptime(
                                data[particular_leave]['end_date'],
                                "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"), data[particular_leave]['reason_for_leave'],
                                                                                    tracker.get_slot(
                                                                                        'name2'),
                                                                                    data[particular_leave]['leave_count'],
                                                                                    data[particular_leave]['lr_id']]})
                        gt.append({
                            "type": "List",
                            "level": "third level",
                            "lr_id": data[particular_leave]['lr_id'],
                            "emp1_code": tracker.get_slot('name2'),
                            "title": "Following are the leave requests pending for approval. You can approve/reject leave by providing serial number. Only one leave can approved/rejected at a time.",
                            "number": particular_leave,
                            "links":
                                [
                                    {
                                        "display_text": "more",
                                        "more_link":
                                            " {} {} {} {} {} {}".format(
                                                particular_leave + 1,
                                                tracker.get_slot('name2'),
                                                data[particular_leave]['emp_name'],
                                                data[particular_leave]['leave_type'],
                                                dt.datetime.strptime(data[particular_leave]['start_date'],
                                                                    "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                                dt.datetime.strptime(data[particular_leave]['end_date'],
                                                                    "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                                data[particular_leave]['reason_for_leave']),

                                        "link_href":
                                            (tracker.get_slot('name2')),

                                        "button":
                                            [
                                                {
                                                    "title": "Approve",
                                                    "payload": "approve"

                                                },
                                                {
                                                    "title": "Reject",
                                                    "payload": "reject"

                                                }
                                            ]

                                    }
                                ]
                        }
                        )
                    print(gt)
                    particular_leave
                    dispatcher.utter_custom_json(gt)
                    global User_asked_before_intent
                    User_asked_before_intent = tracker.latest_message['intent'].get('name')
                    print("user asked before intent",User_asked_before_intent)
                    confirmation_box_slot = ['ordinal', 'command']
                except:
                    if data['errorDesc'] == "No applications exists for this Employee!":
                        dispatcher.utter_message("This employee has not yet applied for leave.")
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)
                    else:
                        dispatcher.utter_message(data['errorDesc'])
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)
                    confirmation_box_slot = []

                    emp_code_collect_form_slots = []
                

            except:
                print(1302)
                dispatcher.utter_template("utter_continue_leaves_service", tracker)
                confirmation_box_slot = []

                emp_code_collect_form_slots = []
            

            return [SlotSet('command',None),SlotSet('empCodeForleaveRequest',None),SlotSet('reason',None),SlotSet('ordinal',None),SlotSet('name2',None),SlotSet('emp_code1',None)]


            print("Inside submit of pending leave form")

            print("submit detail")

            return []   

# action get one pending approval by name

class ActionOnePendingNameApproval(Action):
    def name(self):
        return 'action_get_one_pending_approval_by_name'

    def run(self, dispatcher, tracker, domain):
        global emp_code_collect_form_slots
        try:
            response = requests.get("{}/PendingLeaveApproval?emp_code={}&emp1_code={}".format(mindsconnect_url,
                                                                                              tracker.get_slot(
                                                                                                  'emp_code'),
                                                                                              tracker.get_slot(
                                                                                                  'name2')))
            dispatcher.utter_custom_json(gt)
            print(response)
            data = response.json()
            print(data)
            print(len(data))
            leaves_count = len(data)
            gt = []
            global confirmation_box
            confirmation_box = {}
            global confirmation_box_emp_code
            confirmation_box_emp_code = {}
            global other_emp_code_dict
            other_emp_code_dict = {}
            global confirmation_box_slot
            try:
                for particular_leave in range(0, leaves_count):
                    print("particular_leave",particular_leave)
                    confirmation_box.update({"{}".format(particular_leave + 1): [data[particular_leave]['emp_name'],
                                                                                 data[particular_leave]['leave_type'],
                                                                                 dt.datetime.strptime(
                                                                                     data[particular_leave][
                                                                                         'start_date'],
                                                                                     "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                                                     "%d/%m/%Y"), dt.datetime.strptime(
                            data[particular_leave]['end_date'],
                            "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"), data[particular_leave]['reason_for_leave'],
                                                                                 tracker.get_slot(
                                                                                     'name2'),
                                                                                 data[particular_leave]['leave_count'],
                                                                                 data[particular_leave]['lr_id']]})
                    other_emp_code_dict.update({tracker.get_slot(
                        'name2'): data[particular_leave]['lr_id']})
                    confirmation_box_emp_code.update({tracker.get_slot('name2'): [data[particular_leave]['emp_name'],
                                                                                  data[particular_leave]['leave_type'],
                                                                                  dt.datetime.strptime(
                                                                                      data[particular_leave][
                                                                                          'start_date'],
                                                                                      "%Y-%m-%d %H:%M:%S.%f").strftime(
                                                                                      "%d/%m/%Y"), dt.datetime.strptime(
                            data[particular_leave]['end_date'],
                            "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"), data[particular_leave]['reason_for_leave'],
                                                                                  tracker.get_slot(
                                                                                      'name2'),
                                                                                  data[particular_leave]['leave_count'],
                                                                                  data[particular_leave]['lr_id']]})
                    gt.append({
                        "type": "List",
                        "level": "third level",
                        "lr_id": data[particular_leave]['lr_id'],
                        "emp1_code": tracker.get_slot('name2'),
                        "title": "Following are the leave requests pending for approval. You can approve/reject leave by providing serial number. Only one leave can approved/rejected at a time.",
                        "number": particular_leave,
                        "links":
                            [
                                {
                                    "display_text": "more",
                                    "more_link":
                                        " {} {} {} {} {} {}".format(
                                            particular_leave + 1,
                                            tracker.get_slot('name2'),
                                            data[particular_leave]['emp_name'],
                                            data[particular_leave]['leave_type'],
                                            dt.datetime.strptime(data[particular_leave]['start_date'],
                                                                 "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                            dt.datetime.strptime(data[particular_leave]['end_date'],
                                                                 "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y"),
                                            data[particular_leave]['reason_for_leave']),

                                    "link_href":
                                        (tracker.get_slot('name2')),

                                    "button":
                                        [
                                            {
                                                "title": "Approve",
                                                "payload": "approve"

                                            },
                                            {
                                                "title": "Reject",
                                                "payload": "reject"

                                            }
                                        ]

                                }
                            ]
                    }
                    )
                print(gt)
                dispatcher.utter_custom_json(gt)
                global User_asked_before_intent
                User_asked_before_intent = tracker.latest_message['intent'].get('name')
                print(User_asked_before_intent)
                confirmation_box_slot = ['ordinal', 'command']
            except:
                if data['errorDesc'] == "No applications exists!":
                    dispatcher.utter_message("There is no leave requests are pending with me for approval 2.")
                else:
                    dispatcher.utter_message(data['errorDesc'])
                confirmation_box_slot = []

                emp_code_collect_form_slots = []
            print(confirmation_box_emp_code)
            print(confirmation_box)
            print("123")

        except:
            print(1302)
            # dispatcher.utter_template("utter_continue_leaves_service", tracker)
            confirmation_box_slot = []

            emp_code_collect_form_slots = []
        # print(confirmation_box_emp_code)
        # print(confirmation_box)
        print("432")

        return [SlotSet('command',None),SlotSet('empCodeForleaveRequest',None),SlotSet('reason',None),SlotSet('ordinal',None),SlotSet('name2',None),SlotSet('emp_code1',None)]

# class ActionGetEmpID(Action):
#     def name(self):
#         return 'action_get_empid'

#     def run(self, dispatcher, tracker, domain):
#         emp_code = tracker.get_slot('emp_code')
#         password = tracker.get_slot('password')
#         print("employee code ", emp_code)
#         # print("password ", password)

#         if emp_code is None or password is None:
#             dispatcher.utter_template("utter_service_failed_login_message", tracker)
#         else:

#             status_code = 0

#             try:
#                 print("employee code above upper() method  ", emp_code)
#                 emp_code = emp_code.upper()
#                 print("employee code inside action_get_empid ", emp_code)

#                 # Calling API to get profile info

#                 # Working url in office

#                 response = requests.get(
#                     '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

#                 # Working url at home

#                 # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

#                 # Getting Json response

#                 data = response.json()
#                 # emp_id

#                 try:

#                     emp_id = str(data['emp_id']['emp_id'])
#                     status_code = 0
#                 except:
#                     status_code = 1

#                 if status_code != 1:
#                     response3 = """Your Employee ID is  {}.""".format(emp_code)
#                     print('Employee id ', emp_code)
#                 else:
#                     response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

#                 dispatcher.utter_message(response3)
#                 dispatcher.utter_template("utter_continue_profile_service", tracker)

#             except Exception as e:
#                 print("Exception has occured :: ", str(e))
#                 dispatcher.utter_template("utter_invalid_login", tracker)

#             return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


