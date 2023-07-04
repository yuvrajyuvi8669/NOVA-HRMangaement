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

global leaves_count
global EMP_ID
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

required_slots_list = ["form_data"
# ,"start_date",
#                        "end_date",
#                        "leave_type",
#                        "purpose",
#                        "hand_over_Employee",
#                        "knowledge_summary"
                       ]


# mindsconnect_url = "http://uat.omfysgroup.com/MINDSCONNECT"
#UAT URL
#mindsconnect_url = "https://uat.omfysgroup.com/mindsconnect_objective/"
#Production URL
mindsconnect_url = "https://demo.omfysgroup.com/mindsconnectleapi/"
# UAT Project Module
API_URL_Django = "http://13.127.186.145:8000"
API_URL_Flask = "http://43.231.254.81:5888"
employee_last_name_globally = "http://uat.omfysgroup.com/MINDSCONNECT"
# UAT Project Module
# project_module_url = "http://103.109.13.198/project-management"
# production url
project_module_url = "https://mindsconnect.omfysgroup.com/project_mngt/"
cmc_url = "https://cmc.omfysgroup.com"

################### action to set emp code and password after hi intent  ########################

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
        
        
        response = requests.get('{}empCodeCheck?emp_code={}'.format(mindsconnect_url, emp_code))
        data = response.json()
        #EMP_name = (data["jd"]['emp_id']['emp_first_name'])
        #EMP_last_name = str(data['emp_id']['emp_last_name'])
        EMP_ID = (data["jd"]['emp_id']['emp_id'])
        #print("emp_id",EMP_ID)
        #print(EMP_name)
        print("EMP Id Show",EMP_ID)
        # print("setting employee code is", emp_code)
        #print("password is", password)
        dispatcher.utter_message(text="Login successfully")
        return [SlotSet('emp_code',emp_code),SlotSet('password',password)]



class ActionCheckLoggedForLeavesService(Action):
    def name(self):
        return 'action_check_logged_for_leaves_service'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)

        intent = tracker.latest_message['intent'].get('name')
        print(intent,"leave details")
        

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:

            try:

                if emp_code  == " " and password  == " ":
                    raise Exception('I know Python!')

                if emp_code is None and password is None:
                    raise Exception('I know Python!')

                print("below if statement")
                dispatcher.utter_template("utter_leave_information", tracker)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

        return []



class ActionLeaveBalance(Action):
    def name(self):
        return 'action_get_leave_balance'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ss ", emp_code)
        print("password ", password)

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            try:
                emp_code = emp_code.upper()
                print("employee code :action_get_leave_balance ", emp_code)

                response = requests.get(
                    '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code, password))

                data = response.json()
                print("Class:ActionLeaveBalance data for employee loginCheck \n\n", data)

                # if data is None:
                #     raise Exception(
                #         "I am sorry! I don't have this information with me. Could you please get it from HR Manager?")
                # emp_id
                emp_id = str(data['emp_id']['emp_id'])
                print(emp_id)
                # print("employee id is :action_get_leave_balance ", emp_id)

                response = requests.get(
                    '{}/leaveEligibility?emp_id={}'.format(mindsconnect_url, emp_id))

                data = response.json()

                print("Class:ActionLeaveBalance data for leave eligibility \n\n", data)

                errorCode = data['errorCode']

                print("errorCode is action_get_leave_balance ", errorCode)

                response = requests.get(
                    '{}/leaveBalance?emp_id={}'.format(mindsconnect_url, emp_id))

                data = response.json()
                print(data,"ssssss")
                print("Class:ActionLeaveBalance data for leave balance \n\n", data)
                pl = data['pl']
                cl = data['cl']

                print("Your leave balance is PL :%.1f and CL :%.1f " % (pl, cl))

                current_intent = tracker.latest_message['intent'].get('name')

                if current_intent == "apply_pl" or current_intent == "apply_cl" or current_intent == "apply_lwp" or current_intent == "leav_apply":

                    if errorCode == 105:
                        dispatcher.utter_message(
                            "You don't have any credited leaves as you are Trainee")
                    elif errorCode == 106:
                        dispatcher.utter_message("Your leave balance is PL:" + str(pl) + " CL:" + str(
                            cl) + " But you are not eligible to avail pl as you are on probation period")
                    elif errorCode == 0:
                        dispatcher.utter_message(
                            "Your leave balance is PL- %.1f CL- %.1f" % (pl, cl))

                else:

                    if errorCode == None:
                        dispatcher.utter_message(
                            "You don't have any credited leaves as you are Trainee")
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)
                    elif errorCode == 106:
                        dispatcher.utter_message("Your leave balance is PL:" + str(pl) + " CL:" + str(
                            cl) + " But you can not avail pl as you are on probation period")
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)
                    elif errorCode == 0:
                        dispatcher.utter_message(
                            "Your leave balance is PL %.1f and CL %.1f" % (pl, cl))
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)


            except Exception as e:
                print("Exception has occured ", str(e))
                if data is None:
                    dispatcher.utter_message(
                        "You don't have any credited leaves as you are Trainee")
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
                else:
                    dispatcher.utter_template("utter_invalid_login", tracker)

        return [SlotSet('emp_code', emp_code), SlotSet('password', password)]


class ActionLeaveEligibility(Action):
    def name(self):
        return 'action_get_leave_eligibility'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code ", emp_code)
        print("password ", password)

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
                        "I am sorry! I don't have this information with me. Could you please get it from HR Manager3?")
                # emp_id
                emp_id = str(data['emp_id']['emp_id'])
                print(emp_id)

                response = requests.get(
                    '{}/leaveEligibility?emp_id={}'.format(mindsconnect_url, emp_id))

                data = response.json()
                print(data)
                print("Class:ActionLeaveEligibility data for leave eligibility \n\n", data)

                errorCode = data['errorCode']
                

                print("errorCode ", errorCode)

                if errorCode == 105:
                    dispatcher.utter_message(
                        "I am sorry! Being a trainee, you are not eligible for any kind of leaves")
                    print("above one")
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
                    print("1 one")
                elif errorCode == 106:
                    dispatcher.utter_message(
                        "Hey! You are still in probation period, you are eligible only for CL. You are not eligible to avail PL")
                    print("1 two")
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
                    print("1 thiree exception")
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
                else:
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
        print(intent)

        if emp_code is None or password is None:
            print("returning false")
            return [SlotSet('login_status', False)]
        else:
            print("returning true")
            return [SlotSet('login_status', True)]






class ActionGetLeaveStatus(Action):
    def name(self):
        return 'action_get_leave_status'

    def run(self, dispatcher, tracker, domain):
        output_leave_status_message = """<b>Your leaves status is as below:  </b><br><br>"""
        append_msg = """"""
        emp_code = tracker.get_slot('emp_code')

        leave_types = ""
        password = tracker.get_slot('password')
        print("employee code is", emp_code)
        print("password is", password)
        intent = tracker.latest_message['intent'].get('name')
        print(intent,'leave status')

        print(intent)
        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        else:
            # emp_code = emp_code.upper()
            print("employee code ", emp_code)
            response1 = requests.get(
                '{}/leaveRequestStatus?emp_id={}'.format(mindsconnect_url, EMP_ID))
            print(response1)
            data1 = response1.json()

            print('len of data1  in action_get_leave_status : ', len(data1))

            LR_ID = {}
            emp_code_index = 0
            if len(data1) > 0:
                for x in data1:
                    print('value of x ', x)
                    LIST_LR_ID.insert(emp_code_index, x)
                    emp_code_index = emp_code_index + 1
                # LIST_LR_ID.append(x)
                # for x_data in x:
                # 	print('value of x_data %s'%(x[x_data]))
                # 	print('key : %s value : %s' % (x_data,x[x_data]))
                # 	LR_ID[x_data] = x[x_data]

                print('Contents of LR_ID below for loop ',LR_ID)
                print('Dictionary content of LR_ID ', LIST_LR_ID)
            print('LIST_LR_ID from leaveRequestDetails ', LIST_LR_ID)

            lrid_set = {}
            count = 0
            print('length of LIST_LR_ID ', len(LIST_LR_ID))
            id_lenth = len(LIST_LR_ID)
            
            if len(LIST_LR_ID) > 0:
                for lr in LIST_LR_ID:
                    # New leave request status API
                    print('AAAAAAAAAAAA lr id is ', lr['lr_id'],'{}/leaveRequestDetails?emp_id={}&lr_id={}'.format(mindsconnect_url, lr['emp_id'], lr['lr_id']))
                    print(lr['emp_id'])
                    response = requests.get(
                        '{}/leaveRequestDetails?emp_id={}&lr_id={}'.format(mindsconnect_url, lr['emp_id'], lr['lr_id']))
                    data1 = response.json()
                    print("typeWa:---",type(data1))
                    print("TheResponce:---",response)
                    print("lr['emp_id']:---",lr['emp_id'])
                    global statusLeave
                    # Working url get leave balance
                    if data1:
                        try:
                            print('Got data from leave status',)
                            data = response.json()
                            print("data:---",data)
                            print('all records length ', len(data))
                            startDate = data[0]['start_date']
                            print('startDate type', type(startDate))
                            date_time_Str = startDate
                            date_time_obj = dt.datetime.strptime(date_time_Str, '%b %d, %Y %H:%M:%S %p')
                            month = date_time_obj.strftime('%b')
                            print('month ', month)
                            day = date_time_obj.date().day
                            print('day ', day)
                            year = date_time_obj.date().year
                            print('year ', year)

                            x_startDate = '{}-{}-{}'.format(day, month, year)
                            print('x_startDate ', x_startDate)

                            endDate = data[0]['end_date']
                            print('endDate ', endDate)

                            date_time_Str_1 = endDate
                            date_time_obj_1 = dt.datetime.strptime(
                                date_time_Str_1, '%b %d, %Y %H:%M:%S %p')
                            month_1 = date_time_obj_1.strftime('%b')
                            print('month_1 ', month_1)
                            day_1 = date_time_obj_1.date().day
                            print('day_1 ', day_1)
                            year_1 = date_time_obj_1.date().year
                            print('year_1 ', year_1)

                            x_endDate = '{}-{}-{}'.format(day_1, month_1, year_1)
                            print('x_endDate ', x_endDate)

                            statusLeave = lr['status']
                            print('statusleave 1')

                            # lrid_set.add(lr['lr_id'])
                            count = count + 1

                            if int(data[0]['leave_type']) == 2:
                                print('if leave type is ', int(data[0]['leave_type']))
                                leave_types = "PL"
                                print('leave type ', leave_types)

                            elif int(data[0]['leave_type']) == 1:
                                print('if leave type is ', int(data[0]['leave_type']))
                                leave_types = "CL"
                                print('leave type ', leave_types)

                            elif int(data[0]['leave_type']) == 7:
                                print('if leave type is ', int(data[0]['leave_type']))
                                leave_types = "OD"
                                print('leave type ', leave_types)

                            elif int(data[0]['leave_type']) == 5:
                                print('if leave type is ', int(data[0]['leave_type']))
                                leave_types = "LWP"
                                print('leave type ', leave_types)

                            print('Leave type is ', leave_types)
                            print('lr from leaveRequestDetails ', lr)

                        except Exception as e:
                            print("exeption stringwa:----",str(e))
                        
                        if statusLeave.lower() == "approved":
                            append_msg = append_msg + "Your {} starts from {} and end with {} is {}.<br><br>".format(leave_types, x_startDate, x_endDate, statusLeave)
                        else:
                            append_msg = append_msg + "Your {} starts from {} and end with {} is still {}.<br><br>".format(leave_types, x_startDate, x_endDate, statusLeave)
                        dispatcher.utter_message(output_leave_status_message+" " + append_msg)
                    else:
                        dispatcher.utter_message(
                            "I am sorry! I don't have this information with me. Could you please get it from HR Manager?2")
                        print("1 four status")    
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)
                print('appended message is ', append_msg)
                print('count is ', count)   
                print("id length",id_lenth)    
                if count == id_lenth-1:
                    dispatcher.utter_message(output_leave_status_message+" "+ append_msg)
                else:
                    print("id_lenth is not matched with count")
                    
                # Working url get leave balance
                LIST_LR_ID.clear()
                print("1 two status")
                dispatcher.utter_template("utter_continue_leaves_service", tracker)
            else:

                dispatcher.utter_message("There are no Leaves")
                print("1 three status")
                dispatcher.utter_template("utter_continue_leaves_service", tracker)

        return []



class ActionCheckLeaveDays(Action):
    def name(self):
        return 'action_check_leave_days'

    def run(self, dispatcher, tracker, domain):
        total_days_of_leave = int(tracker.get_slot('leave_days'))

        print("Total days of leave", total_days_of_leave)

        intent = tracker.latest_message['intent'].get('name')

        one_day_leave = True

        if total_days_of_leave > 1:
            print("returning false")
            return [SlotSet('one_day_leave', False)]
        elif total_days_of_leave == 1:
            print("returning true")
            return [SlotSet('one_day_leave', True)]
        return []



class ActionCheckLoginStatusLeaveApply(Action):
    def name(self):
        return 'action_check_login_leave_apply'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("Inside action check login for leave apply")
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
        print(intent)

        if emp_code is None or password is None:
            print("returning false")
            return [SlotSet('login_status', False)]
        else:
            print("returning true")
            return [SlotSet('login_status', True),FollowupAction('action_apply_leave_fill_details')]

class ActionCheckLoginStatusLeaveStatus(Action):
    def name(self):
        return 'action_check_login_status_leave_status'

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
        print(intent)

        if emp_code is None or password is None:
            print("returning false")
            return [SlotSet('login_status', False)]
        else:
            print("returning true")
            return [SlotSet('login_status', True)]

class ActionCheckLoginStatusCancelLeave(Action):

    def name(self):
        return 'action_check_login_status_cancel_lr_id'

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
        print(intent)

        if emp_code is None or password is None:
            print("returning false")
            return [SlotSet('login_status', False)]
        else:
            print("returning true")
            return [SlotSet('login_status', True)]




class ActionApplyLeave(Action):
    def name(self):
        return 'action_apply_leave_fill_details'

    def run(self, dispatcher, tracker, domain):
        names_response = requests.get('{}/allemployeeApi'.format(mindsconnect_url))
        names_data = names_response.json()
        current_intent=tracker.latest_message['intent'].get('name')
        print(current_intent)
        forms = []
        names_display = []
        emp_code = []
        # names_display.append({"text": "All"})
        # names_display.append({"text": "Not Applicable"})
        for name_details in names_data:
            #print("names_details",name_details['emp_first_name'], name_details['emp_last_name'])
            names_display.append({"text":name_details['emp_first_name']+ ' ' + name_details['emp_last_name']})
        print("hvadhjadhgdashgasdhjasdhjsdhSHJ",names_display)
        for Emp_code in names_data:
            emp_code.append({"emp_code":Emp_code['emp_code']})
        print("yuvraj",emp_code)
        print("Asked for to fill details for leave form")
        # print(names_display,"names_display")

        forms.append({
                    "type":"Form",
                    "title":"Please fill following details to apply leave.",
                    "fields":
                        [
                                    {
                                        "field":"Start Date",
                                        "type":"date",
                                        "name":"startDate",
                                        "placeholder":"Start Date"
                                    },
                                    {
                                         "field":"End Date",
                                        "type":"date",
                                        "name":"endDate",
                                        "placeholder":"End Date"
                                    },
                                    {
                                        "field":"Leave Type",
                                        "type":"dropdown",
                                        "name":"leaveType",
                                        "placeholder":"PL/CL/LWP/SOD/PL(1st HD)/CL(1st HD)/LWP(1st HD)/SOD(1st HD)/PL(2nd HD)/CL(2nd HD)/LWP(2nd HD)/SOD(2nd HD)",
                                        "value_list":
                                        [
                                            {
                                                "option_value":"PL"
                                            
                                            },
                                            {
                                                "option_value":"CL"
                                            
                                            },
                                            {
                                                "option_value":"LWP"
                                            
                                            },
                                            {
                                                "option_value":"SOD"
                                            
                                            },
                                            {
                                                "option_value":"PL(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"CL(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"LWP(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"SOD(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"PL(2nd HD)"
                                            
                                            },
                                            {
                                                "option_value":"CL(2nd HD)"
                                            
                                            },
                                            {
                                                "option_value":"LWP(2nd HD)"
                                            
                                            },
                                            {
                                                "option_value":"SOD(2nd HD)"
                                            
                                            }
                                        ]
                                    },
                                    {
                                        "field":"Purpose",
                                        "type":"text",
                                        "name":"purpose",
                                        "placeholder":"Eg. Personal Work"
                                    },
                                    {
                                        "field":"Handover Employee",
                                        "type":"dropdown",
                                        "name":"handOverEmployee",
                                        "placeholder":"Select Names",
                                        "text" : names_display,
                                        "value_list" : emp_code
                                        },
                                    {
                                        "field":"Knowledge Summary",
                                        "type":"text",
                                        "name":"knowledgeSummary",
                                        "placeholder":"Eg.Task"
                                    }                                
                                ]   
                        })

        dispatcher.utter_custom_json(forms)
        print("form sent",forms)
            
        return [SlotSet('separate_detail', None),SlotSet('name2', None)]


class ActionApplyLeaveAPI(Action):
    def name(self):
        return 'action_apply_leave_api'

    def run(self, dispatcher, tracker, domain):
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code in action_apply_leave_api", emp_code)
        print("password ", password)
        global EMP_ID
        
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
        print("EMP ID Show",EMP_ID)
        emp_id = EMP_ID
        # emp_id = str(data['emp_id']['emp_id'])
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

        leave_count = " "
        if leave_type == "PL(1st HD)" or "CL(1st HD)" or "LWP(1st HD)" or "SOD(1st HD)" or "PL(2nd HD)" or "CL(2nd HD)" or "LWP(2nd HD)" or "SOD(2nd HD)":
            leave_count = 0.5
        elif leave_type == "PL" or "CL" or "LWP" or "SOD":
            leave_count = 1

        print(leave_count)

        daytype = " "
        if leave_type == "PL" or "CL" or "LWP" or "SOD":
            daytype = "1st Half"
        elif leave_type == "PL(1st HD)" or "CL(1st HD)" or "LWP(1st HD)" or "SOD(1st HD)":
            daytype = "2nd Half"
        elif leave_type == "PL(2nd HD)" or "CL(2nd HD)" or "LWP(2nd HD)" or "SOD(2nd HD)":
            daytype = "Full day"
            
        print(daytype)

        Leave_Type = " "
        if leave_type == "PL(1st HD)":
            Leave_Type = "HDPL"
        elif leave_type == "CL(1st HD)":
            Leave_Type = "HDCL"
        elif leave_type == "LWP(1st HD":
            Leave_Type = "HDLWP"
        elif leave_type == "SOD(1st HD)":
            Leave_Type = "HDSOD"
        elif leave_type == "PL(2nd HD)":
            Leave_Type = "HDPL"
        elif leave_type == "CL(2nd HD)":
            Leave_Type = "HDCL"
        elif leave_type == "LWP(2nd HD)":
            Leave_Type = "HDLWP"
        elif leave_type == "SOD(2nd HD)":
            Leave_Type = "HDSOD"
        elif leave_type == "PL":
            Leave_Type = "PL"
        elif leave_type == "CL":
            Leave_Type = "CL"
        elif leave_type == "LWP":
            Leave_Type = "LWP"
        elif leave_type == "SOD":
            Leave_Type = "SOD"

        print(Leave_Type)

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
            purpose = {},\n
            daytype = {}
         """.format(mindsconnect_url, emp_id, leave_count, leave_start_date, leave_end_date, Leave_Type,
                    handover_employee, knowledge_summary, purpose,daytype))
        response = requests.get('{}applyLeaveAPI?emp_id={}&noOfDays={}&startDate={}&endDate={}&leaveType={}&handOverEmployee={}&knowledgeSummary={}&purpose={}&daytype={}'.format(mindsconnect_url, emp_id, leave_count, leave_start_date, leave_end_date, Leave_Type, handover_employee,knowledge_summary, purpose,daytype))
        # response = requests.get('http://10.0.0.25:8088/MINDS_CONNECT/applyLeaveAPI?emp_id=26&noOfDays=1&startDate=2019-05-29&endDate=2019-05-29&leaveType=PL&handOverEmployee=OMI-83&knowledgeSummary=doneedful&purpose=personal')
        # response = requests.get('{}/applyLeaveAPI?emp_id={}&noOfDays=1&startDate={}&endDate={}&leaveType={}&handOverEmployee={}&knowledgeSummary={}&purpose={}'.format(mindsconnect_url, emp_id, leave_days, leave_start_date, leave_end_date, leave_type, handover_employee,knowledge_summary, purpose)))
        #print('{}/applyLeaveAPI?emp_id={}&noOfDays={}&startDate={}&endDate={}&leaveType={}&handOverEmployee={}&knowledgeSummary={}&purpose={}'.format(mindsconnect_url, emp_id, leave_days, leave_start_date, leave_end_date, leave_type, handover_employee,knowledge_summary, purpose))

        print("form_API_data==",response.json())

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
                print("1 one leave apply api")
                dispatcher.utter_template("utter_continue_leaves_service",tracker)
          
            except Exception as e:
                print(str(e))

        else:
            
            dispatcher.utter_message(
                "I am sorry! I don't have this information with me. Could you please get it from HR Manager?1")
            buttons = []
            buttons.append({"title": "Yes",
                            "payload": "Yes"})
            buttons.append({"title": "No",
                            "payload": "No"})
            dispatcher.utter_button_message(
                "Do you want to apply one more leave?", buttons)
            print("1 two one leave apply api")
            dispatcher.utter_template("utter_continue_leaves_service",tracker)
        # Working url get leave balance

        return [SlotSet("start_date", None), SlotSet("end_date", None),
                SlotSet("hand_over_Employee", None), SlotSet("knowledge_summary", None),
                SlotSet("leave_days", None), SlotSet("leave_type", None), 
                SlotSet("one_day_leave", None),
                SlotSet("purpose", None),SlotSet("form_data",None)]




class LeaveApplyForm(FormValidationAction):

    def name(self):
        return "validate_apply_leave_form"
        
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:

        print("Inside required slot of apply leave form")
        # try:
        #     global form_data
        #     form_data = tracker.latest_message['text'].split('|')
        #     print(form_data)
        #     return [SlotSet('start_date',form_data[0]),SlotSet('end_date',form_data[1]),SlotSet('leave_type', form_data[2]),SlotSet('purpose', form_data[3]),SlotSet('hand_over_Employee', form_data[4]),SlotSet('knowledge_summary',form_data[5])]
        # except:
        #     pass
        
        global required_slots_list
        return required_slots_list

    # def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
    #     print("slot mapping")

    #     return {
    #         "form_data": [self.from_text()],
    #         "start_date": [self.from_text()],
    #         "end_date": [self.from_text()],
    #         "leave_type": [self.from_text()],
    #         "purpose": [self.from_text()],
    #         "hand_over_Employee": [self.from_text()],
    #         "knowledge_summary": [self.from_text()]
    #     }
    # #
    # def validate_start_date(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
    #                         domain: Dict[Text, Any]) -> Optional[Text]:
    #     print('value of start date ', value)
    #     print('start date ', value)
    #
    #     current_intent = tracker.latest_message['intent'].get('name')
    #     print('current intent is ', tracker.latest_message['intent'].get('name'))
    #
    #     if current_intent == 'stop':
    #         global required_slots_list
    #         required_slots_list = []
    #         dispatcher.utter_template("utter_continue_leaves_service", tracker)
    #         return self.deactivate()
    #
    #     try:
    #         date_format = '%d-%m-%Y'
    #         s_date = datetime.strptime(value, date_format)
    #         print('Start date inside validate: ', s_date.strftime('%Y-%m-%d'))
    #
    #         return {"start_date": s_date.strftime('%Y-%m-%d')}
    #     except Exception as e:
    #         print('Exception from start date ', str(e))
    #         dispatcher.utter_template('utter_wrong_start_date', tracker)
    #         return {"start_date": None}
    #
    # def validate_end_date(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
    #                       domain: Dict[Text, Any]) -> Optional[Text]:
    #     print('value of end date ', value)
    #     print('end date ', value)
    #     current_intent = tracker.latest_message['intent'].get('name')
    #     if current_intent == 'stop':
    #         global required_slots_list
    #         required_slots_list = []
    #         dispatcher.utter_template("utter_continue_leaves_service", tracker)
    #         return self.deactivate()
    #
    #     try:
    #         date_format = '%d-%m-%Y'
    #         e_date = datetime.strptime(value, date_format)
    #         print('start date in end_date ', tracker.get_slot('start_date'))
    #         print('End date inside validate: ', e_date.strftime('%Y-%m-%d'))
    #
    #         if e_date.strftime('%Y-%m-%d') >= tracker.get_slot('start_date'):
    #             print('Inside if statement checking end date')
    #             return {"end_date": e_date.strftime('%Y-%m-%d')}
    #         else:
    #             print('Inside else statement checking end date')
    #             dispatcher.utter_template('utter_end_date_greater_than_start_date', tracker)
    #             return {"end_date": None}
    #     except:
    #         dispatcher.utter_template('utter_wrong_end_date', tracker)
    #         return {"end_date": None}

    def validate_form_data(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:

        
        print('value of form data ', value)
        names_response = requests.get('{}/allemployeeApi'.format(mindsconnect_url))
        names_data = names_response.json()
        names_display = []
        names_display.append({"option_value": "All"})
        names_display.append({"option_value": "Not Applicable"})

        


        current_intent = tracker.latest_message['intent'].get('name')
        print('current intent is ', tracker.latest_message['intent'].get('name'))

        global wrong_attempt

        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return []

        try:

            global form_data
            form_data = tracker.latest_message['text'].split('|')
            print(form_data)

            if len(form_data) == 7:

                wrong_attempt = 0

                SlotSet('start_date',form_data[0])
                SlotSet('end_date',form_data[1])
                SlotSet('leave_type', form_data[2])
                SlotSet('purpose', form_data[3])
                SlotSet('hand_over_Employee', form_data[4])
                SlotSet('knowledge_summary',form_data[5])
                print("Inside form data",tracker.get_slot('start_date'), tracker.get_slot('end_date'))

                return {'form_data':value}
                # return [SlotSet('form_data',form_data),SlotSet('start_date',form_data[0]),SlotSet('end_date',form_data[1]),SlotSet('leave_type', form_data[2]),SlotSet('purpose', form_data[3]),SlotSet('hand_over_Employee', form_data[4]),SlotSet('knowledge_summary',form_data[5])]

            elif wrong_attempt < 3:
                wrong_attempt = wrong_attempt + 1
                for name_details in names_data:
                    # print("names_details",name_details['emp_first_name'])
                    names_display.append({"option_value":name_details['emp_first_name']+ ' ' + name_details['emp_last_name']})

                forms = []
                forms.append({
                    "type":"Form",
                    "title":"Please fill following details to apply leave.",
                    "fields":
                        [
                                    {
                                        "field":"Start Date",
                                        "type":"date",
                                        "name":"startDate",
                                        "placeholder":"Start Date"
                                    },
                                    {
                                        "field":"End Date",
                                        "type":"date",
                                        "name":"endDate",
                                        "placeholder":"End Date"
                                    },
                                    {
                                        "field":"Leave Type",
                                        "type":"dropdown",
                                        "name":"leaveType",
                                        "placeholder":"PL/CL/LWP/SOD/PL(1st HD)/CL(1st HD)/LWP(1st HD)/SOD(1st HD)/PL(2nd HD)/CL(2nd HD)/LWP(2nd HD)/SOD(2nd HD)",
                                        "value_list":
                                        [
                                            {
                                                "option_value":"PL"
                                            
                                            },
                                            {
                                                "option_value":"CL"
                                            
                                            },
                                            {
                                                "option_value":"LWP"
                                            
                                            },
                                            {
                                                "option_value":"SOD"
                                            
                                            },
                                            {
                                                "option_value":"PL(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"CL(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"LWP(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"SOD(1st HD)"
                                            
                                            },
                                            {
                                                "option_value":"PL(2nd HD)"
                                            
                                            },
                                            {
                                                "option_value":"CL(2nd HD)"
                                            
                                            },
                                            {
                                                "option_value":"LWP(2nd HD)"
                                            
                                            },
                                            {
                                                "option_value":"SOD(2nd HD)"
                                            
                                            }
                                        ]
                                    },
                                    {
                                        "field":"Purpose",
                                        "type":"text",
                                        "name":"purpose",
                                        "placeholder":"Eg. Personal Work"
                                    },
                                    {
                                        "field":"Handover Employee",
                                        "type":"dropdown",
                                        "name":"handOverEmployee",
                                        "placeholder":"Eg.OMI-0075",
                                        "value_list": names_display
                                        },
                                    {
                                        "field":"Knowledge Summary",
                                        "type":"text",
                                        "name":"knowledgeSummary",
                                        "placeholder":"Eg.Task"
                                    }                                
                                ]   
                        })

                dispatcher.utter_custom_json(forms)
                print("form sent in else if",forms)
                return {"form_data": None}
        
            else:
                required_slots_list = []
                wrong_start_date_attempt = 0
                dispatcher.utter_message("You have reached to maximum limit of attempts of start date. You should give the date in valid format[e.g YYYY-MM-DD,23rd May]")
                return []
        except:
                required_slots_list = []
                wrong_start_date_attempt = 0
                dispatcher.utter_message("Something Went wrong")
                return []

    def validate_start_date(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:

        print('value of start date ', value)
        print('start date ', value)

        current_intent = tracker.latest_message['intent'].get('name')
        print('current intent is ', tracker.latest_message['intent'].get('name'))
        global wrong_start_date_attempt

        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return []

        try:
            date_format = '%d-%m-%Y'
            # s_date = datetime.strptime(value, date_format)
            s_date = ((cal.nlp(value))[0][0]).strftime("%Y-%m-%d")
            print('Start date inside validate: ', s_date.strftime('%Y-%m-%d'))
            print('Start date inside validate: ', s_date)
            wrong_start_date_attempt = 0

            return {"start_date": s_date}
        except Exception as e:
            if wrong_start_date_attempt <  3:
                print("wrong_start_date_attempt",wrong_start_date_attempt)
                wrong_start_date_attempt = wrong_start_date_attempt + 1
                print('Exception from start date ', str(e))
                dispatcher.utter_template('utter_wrong_start_date', tracker)
                return {"start_date": None}
            else:
                required_slots_list = []
                wrong_start_date_attempt = 0
                dispatcher.utter_message("You have reached to maximum limit of attempts of start date. You should give the date in valid format[e.g YYYY-MM-DD,23rd May]")
                return self.deactivate()


    def validate_end_date(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print('value of end date ', value)
        print('end date ', value)
        current_intent = tracker.latest_message['intent'].get('name')
        global wrong_end_date_attempt
        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return self.deactivate()

        try:
            date_format = '%d-%m-%Y'
            # e_date = datetime.strptime(value, date_format)
            e_date = ((cal.nlp(value))[0][0]).strftime("%Y-%m-%d")

            print('start date in end_date ', tracker.get_slot('start_date'))
            print('End date inside validate: ', e_date.strftime('%Y-%m-%d'))
            print('End date inside validate: ', e_date)

            # if e_date.strftime('%Y-%m-%d') >= tracker.get_slot('start_date'):
            #     print('Inside if statement checking end date')
            #     return {"end_date": e_date.strftime('%Y-%m-%d')}
            if e_date >= tracker.get_slot('start_date'):
                print('Inside if statement checking end date')
                wrong_end_date_attempt = 0
                return {"end_date": e_date}
            elif wrong_end_date_attempt < 3:
                print("wrong_end_date_attempt",wrong_end_date_attempt)
                wrong_end_date_attempt = wrong_end_date_attempt + 1
                print('Inside else statement checking end date')
                dispatcher.utter_template('utter_end_date_greater_than_start_date', tracker)
                return {"end_date": None}
            else:
                required_slots_list = []
                wrong_end_date_attempt = 0
                dispatcher.utter_message("You have reached to maximum limit of attempts of end date. You should give the date in valid format[e.g YYYY-MM-DD,23rd May] ")
                return self.deactivate()
        except:
            if wrong_end_date_attempt < 3:
                print("wrong_end_date_attempt", wrong_end_date_attempt)
                wrong_end_date_attempt = wrong_end_date_attempt + 1
                print('Inside else statement checking end date')
                dispatcher.utter_template('utter_wrong_end_date', tracker)
                return {"end_date": None}
            else:
                required_slots_list = []
                wrong_end_date_attempt = 0
                dispatcher.utter_message("You have reached to maximum limit of attempts of end date. You should give the date in valid format[e.g YYYY-MM-DD,23rd May] ")
                return self.deactivate()


    def validate_leave_type(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                            domain: Dict[Text, Any]) -> Optional[Text]:
        print('value of leave type ', str(value).upper())
        print('leave type ', str(value))
        global wrong_leave_type_attempt
        current_intent = tracker.latest_message['intent'].get('name')
        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return self.deactivate()

        try:
            leave_type = str(value).upper()
            list_leaves = ['CL', 'PL', 'LWP', 'OD']

            if leave_type in list_leaves:
                wrong_leave_type_attempt = 0
                return {"leave_type": leave_type}
            elif wrong_leave_type_attempt< 3:
                print("wrong_leave_type_attempt", wrong_leave_type_attempt)
                wrong_leave_type_attempt = wrong_leave_type_attempt + 1
                print('Inside else statement checking leave')
                dispatcher.utter_template('utter_wrong_leave_type', tracker)
                return {"leave_type": None}
            else:
                required_slots_list = []
                dispatcher.utter_message("You have reached to maximum limit of attempts of entering leave type ")
                wrong_leave_type_attempt = 0

                return self.deactivate()
        except Exception as e_leave_type:
            if wrong_leave_type_attempt < 3:
                print("wrong_leave_type_attempt", wrong_leave_type_attempt)
                wrong_leave_type_attempt = wrong_leave_type_attempt + 1
                print('Inside else statement checking leave')
                dispatcher.utter_template('utter_wrong_leave_type', tracker)

                return {"leave_type": None}
            else:
                required_slots_list = []
                dispatcher.utter_message("You have reached to maximum limit of attempts of entering leave type ")
                wrong_leave_type_attempt = 0
                return self.deactivate()

    def validate_purpose(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                         domain: Dict[Text, Any]) -> Optional[Text]:
        current_intent = tracker.latest_message['intent'].get('name')
        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return self.deactivate()

        return {'purpose': value}

    def validate_knowledge_summary(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                                   domain: Dict[Text, Any]) -> Optional[Text]:
        current_intent = tracker.latest_message['intent'].get('name')
        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return self.deactivate()

        return {"knowledge_summary": value}

    def validate_hand_over_Employee(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                                    domain: Dict[Text, Any]) -> Optional[Text]:
        print("Inside validate hand over Employee")

        current_intent = tracker.latest_message['intent'].get('name')
        if current_intent == 'stop':
            global required_slots_list
            required_slots_list = []
            return self.deactivate()

        print('validate value of handover Employee id ', value)
        print('Employee id from tracker ', tracker.get_slot('emp_code'))
        print('mindsconnect_url ', mindsconnect_url)
        print('value ', value)
        print('password ', tracker.get_slot('password'))
        return {"hand_over_Employee": value}
        # response = requests.get('{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url,value,tracker.get_slot('password')))
        # print('handover employee id check reponse ',response.json())
        # if response.json() != None:
        #
        # 	return {"hand_over_Employee" : value}
        # else:
        # 	dispatcher.utter_template('utter_wrong_hand_over_Employee',tracker)
        # 	return {"hand_over_Employee" : None}

        # try:
        #     leave_type = str(value).upper()
        #     list_leaves = ['CL','PL','LWP']

        #     if leave_type in list_leaves:
        #         return {"leave_type":leave_type}
        #     else:
        #         dispatcher.utter_template('utter_wrong_leave_type',tracker)
        #         return {"leave_type":None}
        # except Exception as e_leave_type:
        #     dispatcher.utter_template('utter_wrong_leave_type',tracker)
        
        

class ActionLeaveFormSubmit(Action):
    
    def name(self):
        return "action_apply_leave_form_submit"

    def run(self, dispatcher, tracker, domain):
        print("Inside submit")

        if len(required_slots_list) < 1:
            buttons = []
            buttons.append({"title": "Yes",
                            "payload": "Yes"})
            buttons.append({"title": "No",
                            "payload": "No"})
            dispatcher.utter_button_message("Do you want to continue leave apply process?", buttons)
            return [SlotSet("start_date", None), SlotSet("end_date", None),
                SlotSet("hand_over_Employee", None), SlotSet("knowledge_summary", None),
                SlotSet("leave_days", None), SlotSet("leave_type", None), SlotSet("one_day_leave", None),
                SlotSet("purpose", None)]

        form_data_for_leave =  tracker.get_slot('form_data')
        leave_data = form_data_for_leave.split('|')
        print(leave_data)
        s_date = ((cal.nlp(leave_data[0]))[0][0]).strftime("%Y-%m-%d")
        e_date = ((cal.nlp(leave_data[1]))[0][0]).strftime("%Y-%m-%d")
        print("start date in submit",s_date)
        print("end date in submit",e_date)

        date_format = '%Y-%m-%d'
        s1_date = datetime.strptime(leave_data[0], date_format)
        e1_date = datetime.strptime(leave_data[1], date_format)
        delta = e1_date - s1_date
        print('Year is ', s1_date.year)

        print('Total days of leave ', int(delta.days) + 1)
        global leave_days
        leave_days = int(delta.days) + 1
        print('leave days from submit method ', leave_days)

        return [SlotSet('start_date',s_date),SlotSet('end_date',e_date),
                SlotSet('leave_type', leave_data[2]),
                SlotSet('purpose', leave_data[3]),
                SlotSet('hand_over_Employee', leave_data[4]),
                SlotSet('knowledge_summary',leave_data[5]), 
                FollowupAction("action_apply_leave_api")]
        
        # start_date = tracker.get_slot('start_date')
        # print('Leave start date:submit ', start_date)

        # end_date = tracker.get_slot('end_date')
        # print('Leave end date:submit ', end_date)

        # date_format = '%Y-%m-%d'

        # s_date = datetime.strptime(start_date, date_format)
        # e_date = datetime.strptime(end_date, date_format)

        # first_date = date(s_date.year,s_date.month, s_date.day)
        # last_date = date(e_date.year,e_date.month,e_date.day)

        # delta = e_date - s_date

        # print('Year is ', s_date.year)

        # print('Total days of leave ', int(delta.days) + 1)
        # global leave_days
        # leave_days = int(delta.days) + 1
        # print('leave days from submit method ', leave_days)

        # return []
#----------------------------------------------------------------------------------------myleavedetails and cancel leave----------------------------------------------------------------------------------------------------

class ActionMyLeaveDetail(Action):

    def name(self):
        return 'action_myleavesdetails'
    
    def run(self, dispatcher, tracker, domain):
        response1 = requests.get('{}/leaveRequestStatus?emp_id={}'.format(mindsconnect_url, EMP_ID))
        print(response1)
        data1 = response1.json()
        if response1 != None:
            try:
                print('Got data from leave status')
                data = response1.json()
                print('length of data array is ', len(data))
                global my_unapproved_leaves
                global display_unapproved
                my_unapproved_leaves = {}
                cancel_leave_list = []
                
                if len(data) > 0:
                    array_count = 0
                    for leave_requests in data:
                        print('leave requests ', leave_requests['lr_id'])
                        print('employee id ', leave_requests['emp_id'])
                        global LR_ID
                        LR_ID = str(leave_requests['lr_id'])
                        global EMP_ID1
                        EMP_ID1 = str(leave_requests['emp_id'])
                        global status
                        status = str(leave_requests['status'])

                        print('status is  : ', status)
                        print('LR_ID is : ', LR_ID)
                        response = requests.get(
                                '{}/leaveRequestDetails?lr_id={}&emp_id={}'.format(mindsconnect_url, LR_ID, EMP_ID1))

                        if response != None and status == "Pending for AR Approval" or status== "Pending for FR Approval":
                            data = response.json()
                            if len(data) > 0:
                                print("display data to cancel leave", data)

                                if int(data[0]['leave_type']) == 2:
                                    print('if leave type is ', int(data[0]['leave_type']))
                                    leave_types = "PL"
                                    print('leave type ', leave_types)
                                elif int(data[0]['leave_type']) == 1:
                                    print('if leave type is ', int(data[0]['leave_type']))
                                    leave_types = "CL"
                                    print('leave type ', leave_types)
                                elif int(data[0]['leave_type']) == 7:
                                    print('if leave type is ', int(data[0]['leave_type']))
                                    leave_types = "OD"
                                    print('leave type ', leave_types)
                                elif int(data[0]['leave_type']) == 5:
                                    print('if leave type is ', int(data[0]['leave_type']))
                                    leave_types = "LWP"
                                    print('leave type ', leave_types)

                                print('Leave type is ', leave_types)
                                data = response.json()
                                print('Got data from leaveRequestDetails', data, len(data))
                                global display_unapproved
                                display_unapproved = []
                                display_unapproved.append(("{} {} {} {}").format(dt.datetime.strptime(data[0]['start_date'],"%b %d, %Y %H:%M:%S %p").strftime("%Y-%m-%d"),dt.datetime.strptime(data[0]['end_date'],"%b %d, %Y %H:%M:%S %p").strftime("%Y-%m-%d"),leave_types,data[0]['lr_id']))
                                my_unapproved_leaves.update({data[0]['lr_id']:[data[0]['emp_id'],dt.datetime.strptime(data[0]['start_date'],"%b %d, %Y %H:%M:%S %p").strftime("%Y-%m-%d"),dt.datetime.strptime(data[0]['end_date'],"%b %d, %Y %H:%M:%S %p").strftime("%Y-%m-%d"),leave_types]})

                                array_count = array_count + 1
                                
                                cancel_leave_list.append({
                                    "type": "List",
                                    "title": "Following are your applied leaves which are not approved yet. So, You can cancel leave by providing Serial Number/Leave Request Id. Only one leave can be cancelled at a time.",
                                    "links": [
                                        {
                                            "more_link": "{}. {} {} {} {}".format(array_count,leave_types,"From",dt.datetime.strptime(data[0]['start_date'],"%b %d, %Y %H:%M:%S %p").strftime("%d-%m-%Y"),dt.datetime.strptime(data[0]['end_date'],"%b %d, %Y %H:%M:%S %p").strftime("%d-%m-%Y")),
                                            "link_href": data[0]['lr_id']
                                        }
                                    ]
                                })
                                print(cancel_leave_list, "------------s")
                        else:
                            print("In else of cancel no leaves")
                    
                    if display_unapproved:
                        # for i in display_unapproved:
                            # dispatcher.utter_message("Following are your applied leaves which are not approved yet. So, you can enter leave request id of leave to cancel your leave <br>{}<br>".format(i))
                        dispatcher.utter_custom_json(cancel_leave_list)
                    else:
                        dispatcher.utter_message('There are no leaves applied')
                        print("1 one myleavedetails") 
                        dispatcher.utter_template("utter_continue_leaves_service", tracker)
                else:
                    dispatcher.utter_message('There are no leaves applied')
                    print("1 one myleavedetails") 
                    dispatcher.utter_template("utter_continue_leaves_service", tracker)
            except Exception as e:
                print(str(e))
        else:
            dispatcher.utter_message("I am sorry! I don't have this information with me.<br> Could you please get it from HR Manager?4")
            print("1 one myleavedetails") 
            dispatcher.utter_template("utter_continue_leaves_service", tracker)
        
        return []

class CancelLeaveLrIdForm(FormValidationAction):

    def name(self):
        return "validate_cancel_lr_idform"

    async def required_slots( self, 
    slots_mapped_in_domain: List[Text], 
    dispatcher: "CollectingDispatcher",         
    tracker: "Tracker",
    domain: "DomainDict",) -> Optional[List[Text]]:
        print("Inside required slot of cancel leave with lr id")
        global required_leave_slot 
        required_leave_slot = ["cancel_lr_id"]    
        return required_leave_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("Inside slot mapping")
        return {
            
            "cancel_lr_id":
            [
                self.from_entity(entity="cancel_lr_id", intent=["cancel_with_lr_id"]),
                self.from_entity(entity="number"),
                self.from_text(intent="cancel_with_lr_id"),
                self.from_text()
            ]
        }
 
    def validate_cancel_lr_id(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of cancel_lr_id in my unaaproved leaves ', value[0], "my_unapproved_leaves.keys():", my_unapproved_leaves.keys())
        leave_id = int(value[0])
        unapproved_leaves_lr_ids = list(my_unapproved_leaves.keys())
        print("unapproved_leaves_lr_ids", unapproved_leaves_lr_ids, type(leave_id),type(unapproved_leaves_lr_ids[0]))
        # return {"cancel_lr_id": leave_id}
        if leave_id in unapproved_leaves_lr_ids:
            print("inside if validate cancel_lr_id" , leave_id)
            return {"cancel_lr_id": leave_id}
        else:
            dispatcher.utter_template('utter_wrong_cancel_lr_id',tracker)
            return {"cancel_lr_id": None}
   
    # def submit(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
    #     print("Inside submit of cancel leave using lr id")
    #     cancel_lr_id=tracker.get_slot('cancel_lr_id')
    #     response1 = requests.get('{}/cancelLeave?lr_id={}&emp_id={}'.format(mindsconnect_url,cancel_lr_id,EMP_ID1))
    #     print(response1)
    #     data1 = response1.json()
    #     print(data)
    #     dispatcher.utter_message(data['errorDesc'])
    #     print("submit detail")
    #     return []

class Actioncancel_lr_id_leave(Action):
    def name(self):
        return "action_cancel_lr_id_form_submit"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
        print("Inside submit of cancel leave using lr id")
        cancel_lr_id = int(tracker.get_slot('cancel_lr_id')[0])
        print(cancel_lr_id,type(cancel_lr_id))
        print('{}/cancelLeave?lr_id={}&emp_id={}'.format(mindsconnect_url,cancel_lr_id,EMP_ID1))
        response1 = requests.get('{}/cancelLeave?lr_id={}&emp_id={}'.format(mindsconnect_url,cancel_lr_id,EMP_ID1))
        print(response1)
        data1 = response1.json()
        print(data1)
        dispatcher.utter_message(data1['errorDesc'])
        print("1 one cancel leave") 
        dispatcher.utter_template("utter_continue_leaves_service", tracker)
        print("submit detail")
        return [SlotSet("cancel_lr_id",None)]   

class ActionCancelLeaveDate(Action):

    def name(self):
        return "action_cancel_Leave_by_Date"

    def run(self, dispatcher, tracker, domain):

        date1 = tracker.get_slot('daterange')
        print(date1)
        start_date = date1['start_date']
        end_date = date1['end_date']
        global my_unapproved_leaves
        array_count_month = 0
        for key in my_unapproved_leaves.keys():
            if start_date < my_unapproved_leaves[key][1] or end_date > my_unapproved_leaves[key][2]:
                global display_unapproved_month
                display_unapproved_month = []
                display_unapproved_month[array_count_month] = ("{} {} {} {}".format(
                    my_unapproved_leaves[key][1],
                    my_unapproved_leaves[key][2], my_unapproved_leaves[key][3],
                    my_unapproved_leaves[key]))
                array_count_month = array_count_month+1

            elif start_date is my_unapproved_leaves[key][1] and end_date is my_unapproved_leaves[key][2]:

                display_unapproved_month = []
                display_unapproved_month[array_count_month] = ("{} {} {} {}".format(
                    my_unapproved_leaves[key][1],
                    my_unapproved_leaves[key][2], my_unapproved_leaves[key][3],
                    my_unapproved_leaves[key]))
                array_count_month = array_count_month + 1
        if len(display_unapproved_month) !=0:
            for i  in len(display_unapproved_month):
                dispatcher.utter_message(
                    "Following are your applied leaves which are not approved yet. So, you can enter leave request id of leave to cancel your leave <br>{}<br>".format(
                        display_unapproved_month[i]))
                print("1 one cancel leave") 
                dispatcher.utter_template("utter_continue_leaves_service", tracker)
        else:
            dispatcher.utter_message("Oops !! Here no leaves of given information")

################################ end of Leave management start ########################################################