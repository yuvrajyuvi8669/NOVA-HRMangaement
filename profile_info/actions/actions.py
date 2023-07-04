from gevent.subprocess import value
from pyrsistent import optional
from rasa_sdk.forms import REQUESTED_SLOT, FormAction
from rasa_sdk import Tracker, Action, FormValidationAction
from typing import Dict, Text, Any, List, Union, Optional
from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime, date, timedelta
from rasa_sdk.events import SlotSet, EventType
from rasa_sdk.events import ActionExecuted
from spacy.vocab import Vocab
from rasa_sdk.types import DomainDict
from spacy.language import Language
from rasa_sdk.events import FollowupAction, AllSlotsReset  
# from rasa.core.trackers import DialogueStateTracker
import datetime as dt
import parsedatetime as pdt
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
import logging
# from cdifflib import CSequenceMatcher

global EMP_ID
cal = pdt.Calendar()
EMP_ID = 0
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
project_module_url = "http://uat.omfysgroup.com/project_mngt"
# mindsconnect_url ="http://uat.omfysgroup.com/MINDSCONNECT" #"http://103.109.13.198/MINDSCONNECT" # https://uat-java.omfysgroup.com/MINDSCONNECT/
# #production URl
mindsconnect_url ="https://demo.omfysgroup.com/mindsconnectleapi"
# UAT URL
#mindsconnect_url ="https://uat.omfysgroup.com/mindsconnect_objective/" #"http://103.109.13.198/MINDSCONNECT" # https://uat-java.omfysgroup.com/MINDSCONNECT/
 
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
        # EMP_name = str(data['emp_id']['emp_first_name'])
        # EMP_last_name = str(data['emp_id']['emp_last_name'])
        EMP_ID = (data["jd"]['emp_id']['emp_id'])
        print("emp_id",EMP_ID)
        # print(EMP_name)
        print("EMP Id Show",EMP_ID)
        #print("setting employee code is", emp_code)
        # print("password is", password)
        dispatcher.utter_message(text="Login successfully")
        return [SlotSet('emp_code',emp_code),SlotSet('password',password)]



    
class ActionProfileInfo(Action):
    def name(self):
        return 'action_get_profile_info'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        emp_code = emp_code.upper()
        print("employee code ", emp_code)

        # Calling API to get profile info

        # Working url in office

        response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

        # Working url at home

        # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

        # Getting Json response

        data = response.json()

        # Storing  values into variables
        # emp_id = int(data['emp_id'])
        # emp_code = str(data['emp_code'])
        # emp_first_name = str(data['emp_first_name'])
        # emp_last_name = str(data['emp_last_name'])
        # user_id = int(data['user_id'])
        # password = str(data['password'])
        # created_by = str(data['created_by'])
        # creation_date = str(data['creation_date'])
        # last_updated_by = str(data['last_updated_by'])
        # last_update_date = str(data['last_update_date'])
        # is_deleted = str(data['is_deleted'])
        # is_activated = str(data['is_activated'])
        # profile_id = int(data['profile_id'])
        # email = str(data['email'])

        gross_salary = str(data['gross_salary'])
        basic_salary = str(data['basic_salary'])
        pf_number = str(data['pf_number'])
        uan_number = str(data['uan_number'])
        esic_number = str(data['esic_number'])
        emp_code = str(emp_code)
        first_name = str(data['emp_id']['emp_first_name'])
        last_name = str(data['emp_id']['emp_last_name'])
        full_name = first_name + " " + last_name

        print('Gross Salary ', gross_salary)
        print('UAN Number ', uan_number)
        print('Employee id ', emp_code)
        print('Employee name ', first_name + " " + last_name)
        print(pf_number,"pf")

        response1 = """Your Gross Salary is {}.""".format(gross_salary)
        response2 = """Your Basic Salary is {}.""".format(basic_salary)
        response3 = """Your PF Number is {}.""".format(pf_number)
        response4 = """Your UAN Number is {}.""".format(uan_number)
        response5 = """Your ESIC Number is  {}.""".format(esic_number)
        response6 = """Your Employee ID is {}.""".format(emp_code)
        response7 = """Your Name {}.""".format(first_name + " " + last_name)

        # response = "Hi am message from action get profile info"

        dispatcher.utter_message(response1)
        dispatcher.utter_message(response2)
        dispatcher.utter_message(response3)
        dispatcher.utter_message(response4)
        dispatcher.utter_message(response5)
        dispatcher.utter_message(response6)
        dispatcher.utter_message(response7)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetEmpID(Action):
    def name(self):
        return 'action_get_empid'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            status_code = 0

            try:
                print("employee code above upper() method  ", emp_code)
                emp_code = emp_code.upper()
                print("employee code inside action_get_empid ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                # Working url at home

                # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

                # Getting Json response

                data = response.json()
                # emp_id

                try:

                    emp_id = str(data['emp_id']['emp_id'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Your Employee ID is  {}.""".format(emp_code)
                    print('Employee id ', emp_code)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except Exception as e:
                print("Exception has occured :: ", str(e))
                dispatcher.utter_template("utter_invalid_login", tracker)

            return [SlotSet('emp_code', emp_code), SlotSet('password', password)]

class ActionCheckLoginStatus(Action):
    def name(self):
        return 'action_check_login_status'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

        global required_slots_list
        required_slots_list = ["form_data"
        # ,"start_date",
        #                        "end_date",
        #                        "leave_type",
        #                        "purpose",
        #                        "hand_over_Employee",
        #                        "knowledge_summary"
        ]

        intent = tracker.latest_message['intent'].get('name')
        login_stauts = False

        if emp_code is None or password is None:
            print("returning false")
            return [SlotSet('login_status', False)]
        else:
            print("returning true")
            return [SlotSet('login_status', True)]

class ActionLeaveEligibility(Action):
    def name(self):
        return 'action_get_leave_eligibility'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # Working url at home

            # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

            # Getting Json response

            try:

                intent = tracker.latest_message['intent'].get('name')
                print("intent name is ::- ", intent)
                emp_code = emp_code.upper()
                print("Inside leave_eligiblity actions :: employee code ", emp_code)

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()

                print("Class:ActionLeaveEligibility data for loginCheck \n\n", data)

                if data is None:
                    raise Exception(
                        "I am sorry! I don't have this information with me. Could you please get it from HR Manager?")
                # emp_id
                emp_id = str(data['emp_id']['emp_id'])

                response = requests.get(
                    '{}/leaveEligibility?emp_id={}'.format(mindsconnect_url, emp_id))

                data = response.json()

                print("Class:ActionLeaveEligibility data for leave eligibility \n\n", data)

                errorCode = data['errorCode']

                print("errorCode ", errorCode)

                if errorCode == 105:
                    dispatcher.utter_message(
                        "I am sorry! Being a trainee, you are not eligible for any kind of leaves")
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
                elif errorCode == 106:
                    dispatcher.utter_message(
                        "Hey! You are still in probation period, you are eligible only for CL. You are not eligible to avail PL")
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
                elif errorCode == 0:
                    dispatcher.utter_message("Great! You are eligible to avail PL and CL.")
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)


            except Exception as e:
                intent = tracker.latest_message['intent'].get('name')
                print("intent name is ::- ", intent)
                print("Inside leave_eligibility action :: Exception has occured")
                if data is None:
                    dispatcher.utter_message(str(e))
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
                else:
                    dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]

class ActionCheckSalaryDetails(Action):
    def name(self):
        return 'action_check_login_for_salary_details'

    def run(self, dispatcher, tracker, domain):
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
                dispatcher.utter_template("utter_salary_detail", tracker)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

        return []

class ActionCheckPFDetails(Action):
    def name(self):
        return 'action_check_login_for_pf_details'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

        intent = tracker.latest_message['intent'].get('name')
        print(intent,"pf details")
        

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            try:

                if emp_code  == " " and password  == " ":
                    raise Exception('I know Python!')

                if emp_code is None and password is None:
                    raise Exception('I know Python!')

                print("below if statement")
                dispatcher.utter_template("utter_pf_detail", tracker)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

        return []



class ActionApplyLeaveAPI(Action):
    def name(self):
        return 'action_apply_leave_api'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code in action_apply_leave_api ", emp_code)
        # print("password ", password)

        emp_code = emp_code.upper()
        print("employee code action_apply_leave_api", emp_code)

        if len(required_slots_list) < 1:
            # dispatcher.utter_template("utter_continue_leaves_service",tracker)
            return [SlotSet("start_date", None), SlotSet("end_date", None),
                    SlotSet("hand_over_Employee", None), SlotSet("knowledge_summary", None),
                    SlotSet("leave_days", None), SlotSet(
                        "leave_type", None), SlotSet("one_day_leave", None),
                    SlotSet("purpose", None),SlotSet("form_data",None)]

        # global variable EMP_ID
        emp_id = EMP_ID
        print("Employee id ", emp_id)
        # leave_days = int(tracker.get_slot('leave_days'))
        # leave_days = tracker.get_slot('leave_days')
        # print('leave_days jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj : ', leave_days)
        try:
            leave_start_date1 = tracker.get_slot('start_date')
            leave_start_date = leave_start_date1.replace('/', '-')
            print('leave_start_date : ', leave_start_date)
            leave_end_date2 = tracker.get_slot('end_date')
            leave_end_date = leave_end_date2.replace('/', '-')
            print('leave_end_date : ', leave_end_date)
            leave_type = tracker.get_slot('leave_type')
            print('leave_type : ', leave_type)
            handover_employee = tracker.get_slot('hand_over_Employee')
            print('handover_employee : ', handover_employee)
            knowledge_summary = tracker.get_slot('knowledge_summary')
            print('knowledge_summary : ', knowledge_summary)
            purpose = tracker.get_slot('purpose')
            print('purpose : ', purpose)
        except:
            print("i am in except loop in action _apply_leave_api")
            leave_start_date = tracker.get_slot('start_date')
            print('leave_start_date : ', leave_start_date)
            leave_end_date = tracker.get_slot('end_date')
            print('leave_end_date : ', leave_end_date)
            leave_type = tracker.get_slot('leave_type')
            print('leave_type : ', leave_type)
            handover_employee = tracker.get_slot('hand_over_Employee')
            print('handover_employee : ', handover_employee)
            knowledge_summary = tracker.get_slot('knowledge_summary')
            print('knowledge_summary : ', knowledge_summary)
            purpose = tracker.get_slot('purpose')
            print("purpose",purpose)            

        if leave_days == 1:
            leave_start_date = leave_start_date
            leave_end_date = leave_start_date
            SlotSet('start_date', leave_start_date)
            SlotSet('end_date', leave_start_date)

        print('leave start date and end date is %s , %s ' %
              (leave_start_date, leave_end_date))

        # Working url in office to get emp_id
        print("""Parameters passing\n
            mindsconnect_url = {},\n
            emp_id = {},\n
            leave_days = {},\n
            leave_start_date = {},\n
            leave_end_date = {},\n
            leave_type = {},\n
            handover_employee = {},\n
            knowledge_summary = {},\n
            purpose = {}
         """.format(mindsconnect_url, emp_id, leave_days, leave_start_date, leave_end_date, leave_type,
                    handover_employee, knowledge_summary, purpose))
        response = requests.get('{}/applyLeaveAPI?emp_id={}&noOfDays={}&startDate={}&endDate={}&leaveType={}&handOverEmployee={}&knowledgeSummary={}&purpose={}'.format(mindsconnect_url, emp_id, leave_days, leave_start_date, leave_end_date, leave_type, handover_employee,knowledge_summary, purpose))
        # response = requests.get('http://10.0.0.25:8088/MINDS_CONNECT/applyLeaveAPI?emp_id=26&noOfDays=1&startDate=2019-05-29&endDate=2019-05-29&leaveType=PL&handOverEmployee=OMI-83&knowledgeSummary=doneedful&purpose=personal')
        print('{}/applyLeaveAPI?emp_id={}&noOfDays={}&startDate={}&endDate={}&leaveType={}&handOverEmployee={}&knowledgeSummary={}&purpose={}'.format(mindsconnect_url, emp_id, leave_days, leave_start_date, leave_end_date, leave_type, handover_employee,knowledge_summary, purpose))

        print(response.json())

        if response != None:
        
            try:
                print('Got data from apply leave')
                data = response.json()
                print("DATA  == ", data)
                errorCode = str(data['errorCode'])
                errorMsg = str(data['errorMsg'])
                errorDesc = str(data['errorDesc'])

                print('errorCode : ', errorCode)
                print('errorMsg : ', errorMsg)
                print('errorDesc : ', errorDesc)
                dispatcher.utter_message(errorDesc)
                dispatcher.utter_template("utter_continue_leaves_service",tracker)
          
            except Exception as e:
                print(str(e))

        else:
            
            # dispatcher.utter_message(
            #     "I am sorry! I don't have this information with me. Could you please get it from HR Manager?")
            # buttons = []
            # buttons.append({"title": "Yes",
            #                 "payload": "Yes"})
            # buttons.append({"title": "No",
            #                 "payload": "No"})
            # dispatcher.utter_button_message(
            #     "Do you want to apply one more leave?", buttons)
            
            dispatcher.utter_template("utter_continue_leaves_service",tracker)
        # Working url get leave balance

        return [SlotSet("start_date", None), SlotSet("end_date", None),
                SlotSet("hand_over_Employee", None), SlotSet("knowledge_summary", None),
                SlotSet("leave_days", None), SlotSet("leave_type", None), 
                SlotSet("one_day_leave", None),
                SlotSet("purpose", None),SlotSet("form_data",None)]

class ActionGetDOJ(Action):
    def name(self):
        return 'action_get_DOJ'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            status_code = 0

            try:

                emp_code = emp_code.upper()
                print("employee code ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                # Working url at home

                # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

                # Getting Json response

                try:

                    data = response.json()

                    # doj
                    doj = str(data['joining_date'])

                    # Removing time parameter from date of joining
                    date = doj
                    date = date.replace(',', ' ')
                    array = list(date.split(" "))

                    # New date of joining after formating
                    doj = array[1] + " " + array[0] + " " + array[3]

                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """You have joined us on  {}.""".format(doj)
                    print('Date of joining  ', doj)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetDesignation(Action):
    def name(self):
        return 'action_get_designation'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            status_code = 0

        # Calling API to get profile info

        # Working url at home

        # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

        # Getting Json response

        try:

            emp_code = emp_code.upper()
            print("employee code ", emp_code)

            # Working url in office

            response = requests.get(
                '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

            data = response.json()
            # designation

            try:
                designation = str(data['designation_id']['designation_name'])
                status_code = 0
            except:
                status_code = 1

            if status_code != 1:
                response3 = """You are working as a  {}.""".format(designation)
                print('Your designation is  ', designation)
            else:
                response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

            dispatcher.utter_message(response3)
            dispatcher.utter_template("utter_continue_profile_service", tracker)

        except:
            print("Exception has occured")
            dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetGrade(Action):
    def name(self):
        return 'action_get_grade'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # Working url at home

            # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

            # Getting Json response

            try:

                emp_code = emp_code.upper()
                print("employee code ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()
                # grade

                try:

                    # grade
                    grade = str(data['grade_id']['grade_name'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Currently you are with  {}.""".format(grade)
                    print('Your Grade is ', grade)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)
            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetAnnualCTC(Action):
    def name(self):
        return 'action_get_annual_ctc'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            # Working url at home

            # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

            # Getting Json response

            try:

                emp_code = emp_code.upper()
                print("employee code ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()

                try:

                    anual_ctc = str(data['ctc'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Your annual CTC is Rs. {}.""".format(anual_ctc)
                    print('Your annual CTC is Rs. ', anual_ctc)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetMonthlyGS(Action):
    def name(self):
        return 'action_get_mgs'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # Calling API to get profile info

            # Working url at home

            # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

            # Getting Json response

            try:

                
                print("employee code ", emp_code)

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()

                try:

                    # gross_salary
                    gross_salary = str(data['gross_salary'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Your monthly Basic Salary is  Rs.{}.""".format(gross_salary)
                    print('Your monthly gross salary is  Rs.', gross_salary)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)
            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionMonthlyBS(Action):
    def name(self):
        return 'action_get_mbs'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # Working url at home

            # Getting Json response

            try:

                emp_code = emp_code.upper()
                print("employee code ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()

                try:

                    # basic salary
                    basic_salary = str(data['basic_salary'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Your monthly Basic Salary is Rs.{}""".format(basic_salary)
                    print('Your monthly basic_salary is ', basic_salary)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetUan(Action):
    def name(self):
        return 'action_get_uan'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # Working url at home

            # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

            # Getting Json response

            try:

                emp_code = emp_code.upper()
                print("employee code ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()

                try:

                    # basic salar
                    uan_number = str(data['uan_number'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Your UAN number is {}.""".format(uan_number)
                    print('Your UAN number is ', uan_number)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetEsic(Action):
    def name(self):
        return 'action_get_esic'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # Working url at home

            # response = requests.get('http://mindsconnect.omfysgroup.com/MINDS_CONNECT/loginCheck?emp_code={}&password={}'.format("OMI-1023","Omfys@123"))

            # Getting Json response

            try:

                emp_code = emp_code.upper()
                print("employee code ", emp_code)

                # Calling API to get profile info

                # Working url in office

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()

                try:

                    # esic_number
                    esic_number = str(data['esic_number'])
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    response3 = """Your ESIC insurance number is  {}.""".format(esic_number)
                    print('Your ESIC number is ', esic_number)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionGetPf(Action):
    def name(self):
        return 'action_get_pf'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            try:

                emp_code = emp_code.upper()
                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))
                data = response.json()
                print("employee code inside pf ", emp_code)
                print("password inside pf ", password)
                try:
                    # pf_number
                    pf_number = str(data['pf_number'])
                    print(pf_number)
                    status_code = 0
                except:
                    status_code = 1

                if status_code != 1:
                    # response3 = """Your PF number is {}/{}/{}/{}/{}.""".format(pf_number.split(0,1),pf_number.split(2,4),pf_number.split(5,11),pf_number.split(12,14),pf_number.split(15,21),)
                    response3="""Your PF number is {}""".format(pf_number)
                    
                    print('Your PF number is ', pf_number)
                    print("response of PF number",response3)
                else:
                    response3 = "I am sorry! I don't have this information with me. Could you please get it from HR Manager?"

                dispatcher.utter_message(response3)
                dispatcher.utter_template("utter_continue_profile_service", tracker)

            except:
                print("Exception has occured")
                dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


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


class ActionLogout(Action):
    def name(self):
        return 'action_logout'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        # print("password ", password)

        # emp_code = emp_code.upper()
        print("employee code inside logout", emp_code)

        if emp_code != None and password != None:
            print("Inside if ")
            return [SlotSet('logout_status', False), SlotSet('emp_code', None), SlotSet('password', None)]

        else:
            print("Inside else ")
            return [SlotSet('logout_status', True)]

        return []


class ActionCheckLoggedForProfileService(Action):
    def name(self):
        return 'action_check_logged_for_profile_service'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is:action_check_logged_for_profile_service ", emp_code)
        print("password is:action_check_logged_for_profile_service ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            try:

                if emp_code  == " " and password  == " ":
                    raise Exception('I know Python!')

                if emp_code is None and password is None:
                    raise Exception('I know Python!')

                dispatcher.utter_template("utter_profile_information", tracker)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]

