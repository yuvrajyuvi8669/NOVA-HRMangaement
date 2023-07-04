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

cal = pdt.Calendar()
global EMP_ID
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
,"start_date",
                       "end_date",
                       "leave_type",
                       "purpose",
                       "hand_over_Employee",
                       "knowledge_summary"
                       ]

# mindsconnect_url = "https://mindsconnect.omfysgroup.com" #Production
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
# mindsconnect_url = "http://uat.omfysgroup.com/MINDSCONNECT"
mindsconnect_url = "http://uat.omfysgroup.com/mindsconnect/"
project_module_url = "http://uat.omfysgroup.com/project_mngt"
cmc_url = "https://cmc.omfysgroup.com"

class ActionUserLogin(Action):
    
    def name(self):
        return "action_get_login_details"

    def run(self, dispatcher, tracker, domain):
        
        global login_slot
        global EMP_ID,EMP_name,EMP_last_name,emp_code,password
        login_slot = ['emp_code','password']
        print("inside action_get_login_details")
        try:
            print("Inside action_get_login_details user login submit")
            emp_code = tracker.get_slot("emp_code")
            password = tracker.get_slot("password")
            response = requests.get(
            '{}/loginCheck?emp_code={}&password={}'.format(mindsconnect_url, emp_code,password))
            if len(login_slot)> 0 and response.json() != None:
                response = requests.get('{}/empCodeCheck?emp_code={}'.format(mindsconnect_url, emp_code))
                data = response.json()
                EMP_name = str(data['emp_id']['emp_first_name'])
                EMP_last_name = str(data['emp_id']['emp_last_name'])
                print(EMP_name)
                # global email_id1
                # email_id1 = str(data['emp_id']['email'])
                dispatcher.utter_message("Hi {} ".format(EMP_name))
                buttons = {"title":"Trainings","payload":"Training Management"},{"title":"Exit","payload":"logout"}
                dispatcher.utter_message(buttons=buttons,text="Congratulations! You are to avail my assistance. You can choose features to get started or type in a direct message.")
                return [SlotSet('emp_code', emp_code), SlotSet('password', password)]
            else:
                dispatcher.utter_template("utter_greet",tracker)
                return [SlotSet('emp_code', None), SlotSet('password', None)]
        except:
            dispatcher.utter_template("utter_greet",tracker)
            return [SlotSet('emp_code',None),SlotSet('password',None)]

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
        ,"start_date",
                               "end_date",
                               "leave_type",
                               "purpose",
                               "hand_over_Employee",
                               "knowledge_summary"
        ]

        intent = tracker.latest_message['intent'].get('name')
        login_stauts = False

        if emp_code is None or password is None:
            
            print("returning false")
            return [SlotSet('login_status', False)]
        
        else:
            
            print("returning true")
            return [SlotSet('login_status', True)]

class ActionCheckLoggedForTrainingManagement(Action):
    
    def name(self):
        return 'action_check_logged_for_training_management'

    def run(self, dispatcher, tracker, domain):
        
        global emp_code, password
        emp_code = tracker.get_slot('emp_code')
        password = tracker.get_slot('password')
        print("employee code is inside action_check_logged_for_training_management", emp_code)
        print("password is action_check_logged_for_training_management", password)
        
        print("employee code is inside action_check_logged_for_training_management", emp_code)
        print("password is action_check_logged_for_training_management", password)

        intent = tracker.latest_message['intent'].get('name')

        if emp_code is None or password is None:
            dispatcher.utter_template("utter_service_failed_login_message", tracker)
        
        else:

            try:
                print("inside try")

                # if emp_code  == " " and password  == " ":
                #     raise Exception('I know Python!')

                # if emp_code is None and password is None:
                #     raise Exception('I know Python!')

                response = requests.get("{}/TrainingofAll?Training_status=Completed&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                data = response.json()
                print(data)
                print(len(data))
                training = len(data) 
                print(training)
                
                buttons = []

                try:
                    if data['errorCode'] == 105:
                        buttons.append({"title": "Training Requests",
                                        "payload": "Training Requests"
                                        })

                        buttons.append({"title": "Completed Training",
                                        "payload": "Completed Training",
                                        "badge": "{}".format(data['errorDesc'])
                                        })
                     
                except:
                    buttons.append({"title": "Training Requests",
                                        "payload": "Training Requests"
                                        })
                    buttons.append({"title": "Completed Training",
                                           "payload": "Completed Training",
                                           "notifications": "{}".format(training)})
                    

                response1 = requests.get(
                    "{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                
                print(response1)
                data1 = response1.json()
                print(data1)
                print(len(data1))
                training1 = len(data1)

                try:

                    if (data1['errorCode'] == 105):

                        buttons.append({"title": "Ongoing Training",
                                                                   "payload": "Ongoing Training",
                                                                   "badge": "{}".format(data1['errorDesc'])})

                        # buttons.append({"title": "Request for Training",
                        #                                            "payload": "Request for training",
                        #                                            })
                        # buttons.append({"title": "Home",
                        #                                            "payload": "Home",
                        #                                            })

                       
                    elif (data1['errorCode'] == 109):


                        buttons.append({"title": "Ongoing Training",
                                        "payload": "Ongoing Training",
                                        "badge": "{}".format(data1['errorDesc'])})
                        # buttons.append({"title": "Request for Training",
                        #                                            "payload": "Request for training",
                        #                                            })
                        # buttons.append({"title": "Home",
                        #                 "payload": "Home"})
                        
                except:

                    buttons.append({"title": "Ongoing Training",
                                    "payload": "Ongoing Training",
                                    "notifications": "{}".format(training1)})
                    # buttons.append({"title": "Request for Training",
                    #                                                "payload": "Request for training",
                    #                                                })
                    # buttons.append({"title": "Home",
                    #                 "payload": "Home"})
            
                response_requestes_training = requests.get("{}/ListofRequestedTraining?User_Emp_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                print(response_requestes_training)
                data_requestes_training = response_requestes_training.json()
                print(data_requestes_training)
                print(len(data_requestes_training))
                training_requestes_training = len(data_requestes_training)
                


                try:

                    if (data_requestes_training['errorCode'] == 400):


                        buttons.append({"title": "Requested Training",
                                                                   "payload": "list the employee requested for training",
                                                                   "badge": "{}".format(data_requestes_training['errorDesc'])})

                        # buttons.append({"title": "Request for Training",
                        #                                            "payload": "Request for training",
                        #                                            })
                        # buttons.append({"title": "Home",
                        #                                            "payload": "Home",
                        #                                            })

                       
                    elif (data_requestes_training['errorCode'] == 109):


                        buttons.append({"title": "Requested Training",
                                                                   "payload": "list the employee requested for training",
                                                                   "badge": "{}".format(data_requestes_training['errorDesc'])})
                        # buttons.append({"title": "Request for Training",
                        #                                            "payload": "Request for training",
                        #                                            })
                        # buttons.append({"title": "Home",
                        #                 "payload": "Home"})
                        
                except:

                    buttons.append({"title": "Requested Training",
                                                                   "payload": "list the employee requested for training",
                                    "notifications": "{}".format(training_requestes_training)})
                    # buttons.append({"title": "Request for Training",
                    #                                                "payload": "Request for training",
                    #                                                })
                    # buttons.append({"title": "Home",
                    #                 "payload": "Home"})

                if tracker.get_slot("emp_code") == "OMI-0076":

                    buttons.append({"title": "Home",
                                        "payload": "Home"})
                else:
                    buttons.append({"title": "Request for Training",
                                                                   "payload": "Request for training",
                                                                   })
                    buttons.append({"title": "Home",
                                        "payload": "Home"})

                
                     
                print("below if statement")
                dispatcher.utter_button_message("Could you please let me know that which trainings would you like to see?",buttons)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

            return [SlotSet('emp_code', emp_code), SlotSet('password', password)]

class ActionCheckLoggedForTrainingRequest(Action):

    def name(self):
        return 'action_check_logged_for_training_request'

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

                response = requests.get("{}/TrainingRequestofAll?Training_request_name=Approved&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                data = response.json()
                print(data)
                print(len(data))
                training = len(data)
                print(training)
                


                buttons = []

                try:
                    if data['errorCode'] == 404:

                        buttons.append({"title": "Approved List",
                                        "payload": "Approved List",
                                        "badge": "{}".format(data['errorDesc'])
                                        })
                     
                except:
                    buttons.append({"title": "Approved List",
                                           "payload": "Approved List",
                                           "notifications": "{}".format(training)})
                    

                response1 = requests.get(
                    "{}/TrainingRequestofAll?Training_request_name=Pending&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                print(response1)
                data1 = response1.json()
                print(data1)
                print(len(data1))
                training1 = len(data1)


                response_pending_for_approval = requests.get(
                    "{}/TrainingRequestofAll?Training_request_name=Pending for Approval&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                print(response_pending_for_approval)
                data_pending_for_approval = response_pending_for_approval.json()
                print(data_pending_for_approval,"data_pending_for_approval")
                print(len(data_pending_for_approval),"len data_pending_for_approval")
                training_pending_for_approval = len(data_pending_for_approval)
                


                try:

                    try: 
                        if (data1['errorCode'] == 404 and data_pending_for_approval['errorCode'] == 404):

                            buttons.append({"title": "Pending List",
                                                                   "payload": "Pending List",
                                                                   "badge": "{}".format(data1['errorDesc'])})
                        
                            buttons.append({"title": "Home",
                                                                   "payload": "Home",
                                                                   })

                       
                    except:

                        try:
                            if (data1['errorCode'] == 404):

                                buttons.append({"title": "Pending List",
                                        "payload": "Pending List",
                                        "notifications": "{}".format(training_pending_for_approval)})
                        
                                buttons.append({"title": "Home",
                                        "payload": "Home"})
                        except:
                            if (data_pending_for_approval['errorCode'] == 404):


                                buttons.append({"title": "Pending List",
                                        "payload": "Pending List",
                                        "notifications": "{}".format(training1)})
                        
                                buttons.append({"title": "Home",
                                        "payload": "Home"})

                        
                except:

                    buttons.append({"title": "Pending List",
                                    "payload": "Pending List",
                                    "notifications": "{}".format(training1+training_pending_for_approval)})
                    
                    buttons.append({"title": "Home",
                                    "payload": "Home"})
                     
                print("below if statement")
                dispatcher.utter_button_message("Could you please let me know that which trainings would you like to see?",buttons)

            except Exception:
                print("Inside except block : action_check_login")
                dispatcher.utter_template("utter_service_failed_login_message", tracker)

            return [SlotSet('emp_code', emp_code), SlotSet('password', password)]

class trainingListForm(FormValidationAction):

    def name(self):
        return "validate_Training_list_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:

        print("Inside required slot of trining list form")
        trainees_emp_code = []
        trainees_name = []
        global Training_list_form_slot
        global current_intent_of_training, user
        current_intent_of_training = "None"
        user = "None"
        global allowed,selection,visit
        visit = 0
		
		# checking trainees available for periodic and inhouse training
        try:
            print("Inside Try")
            response = requests.get("{}/ListofTrainees?Training_Type=Periodic".format(mindsconnect_url))
            data = response.json()
            # # print(data)
            print(data[0]['emp_code'])

            for i in range(0, len(data)):
                trainees_emp_code.append(data[i]['emp_code'])
                trainees_name.append(data[i]['emp_first_name'] + " " + data[i]['emp_last_name'])

            print(trainees_emp_code)
            print(trainees_name)

            try:
                response1 = requests.get("{}/ListofTrainees?Training_Type=Inhouse".format(mindsconnect_url))
                data1 = response1.json()
                for i in range(0, len(data1)):
                    trainees_emp_code.append(data1[i]['emp_code'])
                    trainees_name.append(data1[i]['emp_first_name'] + " " + data1[i]['emp_last_name'])
                print(trainees_emp_code)
                print(trainees_name)
            except:
                print("no inhouse training")

        except:
            Training_list_form_slot = []
            print("No one is trainee")
            
            # displaying list of ongoing training and completed training

        try:
           
            current_intent_of_training = tracker.latest_message['intent'].get('name')
            print(current_intent_of_training, "current_intent_of_training")
            if current_intent_of_training == "Completed_training":
                allowed = "Completed_training"

                response = requests.get(
                    "{}/TrainingofAll?Training_status=Completed&User_Employee_Code={}".format(mindsconnect_url,
                                                                                              tracker.get_slot(
                                                                                                  'emp_code')))
                data = response.json()
                # print(data)
                print(len(data))
                # print(data["errorCode"], "data['errorCode']")
                training = len(data)
                print(training)

            elif current_intent_of_training == "Ongoing_trainings":
                allowed = "Ongoing_trainings"
                response = requests.get(
                    "{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,
                                                                                            tracker.get_slot(
                                                                                                'emp_code')))
                data = response.json()
                print(data)
                print(len(data))
                # print(data["errorCode"], "data['errorCode']")
                training = len(data)
                print(training)
            
            elif current_intent_of_training == "update_status" and tracker.get_slot("emp_code") in trainees_emp_code:
                allowed = "Ongoing_trainings"
                response = requests.get(
                    "{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,
                                                                                            tracker.get_slot(
                                                                                                'emp_code')))
                data = response.json()
                print(data)
                print(len(data))
                # print(data["errorCode"], "data['errorCode']")
                training = len(data)
                print(training)
            
            elif current_intent_of_training == "update_status":
                allowed = "Trainer"
                response = requests.get("{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                data = response.json()
                print(data)
                print(len(data))
                # print(data["errorCode"], "data['errorCode']")
                training = len(data)
                print(training)

            else:

                print("other intent")
                data = "other intent"

            try:
                if data['errorCode']:
                    print("inside try if")
                    print(data["errorCode"], "data['errorCode']")
                    
                    allowed = "No"
                    # dispatcher.utter_message("Trainings not available!")
                    Training_list_form_slot = []
                    return Training_list_form_slot

            except:
                
                print(tracker.get_slot("number_of_trainee"),'tracker.get_slot("number_of_trainee")')
                print(tracker.get_slot("trainees"),'tracker.get_slot("trainees")')

                if tracker.get_slot("number_of_trainee") == "all":  # check all employee or particular employee
                    print("Inside tracker of number of trainee",tracker.get_slot("number_of_trainee"))
                    Training_list_form_slot = ["number_of_trainee","trainings_period"]
                    return Training_list_form_slot

                # elif tracker.get_slot("number_of_trainee") == "trainee":
                #     print("Inside tracker of number of trainee",tracker.get_slot("number_of_trainee"))
                #     Training_list_form_slot = ["number_of_trainee","trainees"]
                #     return Training_list_form_slot

                elif tracker.get_slot("emp_code") in trainees_emp_code:
                    print("User is trainee")
                    user = "trainee"
                    Training_list_form_slot = []
                    return Training_list_form_slot
                 
                # if trainer asking for training list and trainer is also acting as a trainee for another training.
                elif tracker.get_slot("emp_code") in trainees_emp_code and tracker.get_slot("trainees"): 
                    print("User is trainee asking for trainee")
                    Training_list_form_slot = ["trainees"]
                    SlotSet("trainees", tracker.get_slot("trainees"))
                    return Training_list_form_slot

                elif tracker.get_slot("emp_code") in trainees_emp_code and tracker.get_slot("number_of_trainee") == "all":
                    print("User is trainee asking for all training")
                    user = "trainee"
                    SlotSet("number_of_trainee","all")
                    Training_list_form_slot = ["number_of_trainee"]
                    return Training_list_form_slot
                
                elif tracker.get_slot("number_of_trainee") == "trainee" and tracker.get_slot("trainees") is None:
                    print("User is other asking ")
                    Training_list_form_slot = ["trainees"]
                    return Training_list_form_slot 


                elif tracker.get_slot("number_of_trainee") == "trainee" and tracker.get_slot("trainees") is not None:
                    
                    print("Inside tracker of trainees",tracker.get_slot("trainees"))
                    Training_list_form_slot = ["trainees","trainings_period"]
                    return Training_list_form_slot

                elif data == "other intent":
                    if tracker.latest_message['intent'].get('name') == "Training_specification":
                        if  tracker.get_slot("specific_training") == "Trainee Specific":
                            Training_list_form_slot = ["number_of_trainee"]
                        elif  tracker.get_slot("specific_training") == "Period Specific":
                            Training_list_form_slot = ["trainings_period"]
                        elif  tracker.get_slot("specific_training") == "Competency Specific":
                            Training_list_form_slot = ["specific_training","compentency_group","trainings_period"]
                        else:
                            pass
                    return Training_list_form_slot

                # elif allowed_request == "Approved_list":
                #     print("Inside else")
                #     Training_request_list_form_slot = ["specific_training"]
                #     return Training_request_list_form_slot
                          
                
                    


            # elif data["errorCode"] is 105:
            #     print(data["errorCode"], "data['errorCode']")
            #     print('Trainings are not available!')
            #     dispatcher.utter_message(data["errorDesc"])
            #     Training_list_form_slot = []
            #     return Training_list_form_slot

                # elif data  == "other intent":
                #     print("Inside other intent")
                #     if tracker.latest_message['intent'].get('name') == "Training_specification": 
                #         Training_request_list_form_slot = ["number_of_trainee"]
                #     return Training_request_list_form_slot

    
                else:
                    print("Inside else")
                    # Training_list_form_slot = ["number_of_trainee"]
                    Training_list_form_slot = ["specific_training"]
                    return Training_list_form_slot
                

        except:
            print("Inside except")
            Training_list_form_slot = ["specific_training"]
            return Training_list_form_slot
        # return  Training_list_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("slot mapping")

        return {
            "trainings_period":[
                
                self.from_entity(entity="daterange"),
                self.from_entity(entity="trainings_period"),
                self.from_text()

            ],

            "specific_training":[
                self.from_text(),
                self.from_text(intent="Training_specification"),
                self.from_text()
                
            ],

            "number_of_trainee": [
                self.from_entity(entity="number_of_trainee"),
                self.from_text(intent="number_of_trainee_details"),
                self.from_text()
            ],

            "trainees":[
                self.from_entity(entity="PERSON"),
                self.from_entity(entity="trainees"),
                self.from_entity(entity="ORG"),
                self.from_entity(entity="name2"),
                self.from_text(intent="data"),
                self.from_text(intent="number_of_trainee_details"),
                self.from_text(intent="trainee_details"),
                self.from_text(intent="Training_Management"),
                self.from_text(intent="Ongoing_trainings"),
                self.from_text(intent="Completed_training"),
                self.from_text()
            ],

            "compentency_group":
            [
                self.from_text()

            ]
        }


    def validate_specific_training(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:

        print("Value",value)
        global wrong_attempt
        global Training_list_form_slot

        if value.title() in ["Competency Specific","Competency","Technology","Languages","Skills","Competency Specific","Compentency Specific"]:
            print("Inside if")
            wrong_attempt = 0
            Training_list_form_slot.append("compentency_group")
            Training_list_form_slot.append("trainings_period")
            return{"specific_training":"Competency Specific"}

        elif value.title() in ["Period Specific","Period","Time","Month","Weekly"]:
            print("Inside elif")
            wrong_attempt = 0
            Training_list_form_slot.append("trainings_period")
            return{"specific_training":"Period Specific"}

        elif value.title() in ["Trainee Specific","Trainee","A Trainee","A Particular Trainee"]:
            print("Inside elifif")
            wrong_attempt = 0
            Training_list_form_slot.append("number_of_trainee")
            return{"specific_training":"Trainee Specific"}
        
        elif value.title() in ["All","All Trainings"]:
            print("Inside elifif")
            wrong_attempt = 0
            Training_list_form_slot.append("trainings_period")
            return{"specific_training":"All"}

        elif wrong_attempt < 3:
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_specific_training",tracker)
            return {"specific_training": None}

        else:
            Training_list_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()

    def validate_compentency_group(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        
        print("compentency group Value",value)
        global wrong_attempt
        global Training_list_form_slot
        global Compentency_group_dict
        Compentency_group_dict = {}
         # Compentency_group_dict = {'Dot Net':[1,'DNET'],'Python':[11,'PY'],'Javascript':[12,'JS'],'VBA':[21,'VBA'],'Automation Anywhere':[22,'AAP'],'RASA Chatbot Platform':[41,'RCP'],'Java':[61,'JAV'],'Database':[62,'DTB'],'UI':[63,'UIT'],'Server':[64,'SVR'],'ODA':[81,'ODA'],'OPA Training':[101,'OPA'],'Test Engineering':[102,'STE'],'R  Programming Language':[103,'RPL'],'RPA for Sales Professionals':121,'Oracle Digital Assistant Certification':141,'OPA Cloud Service 2017 Sales Specialist':165,'OPA Cloud Service 2019 Sales Specialist':166,'OPA Cloud Service 2019 Solution Engineer':167,'OPA 2019 Implementation Essentials Certification':183,'AA Partner Sales Professional Accreditation ':202,'AA Partner Sales Engineer Accreditation ':204,'Connector Development':[221,'OCD']}
        
        response = requests.get("{}/getCompetencyGroupInformation".format(mindsconnect_url))
        data = response.json()
        for i in range(0,len(data)):

            Compentency_group_dict.update({data[i]['comp_name']:[data[i]['comp_gr_id'],data[i]['abbreviation']]})
       
       
        if value.title() in Compentency_group_dict.keys():
            print("Inside if")
            wrong_attempt = 0
            Training_list_form_slot.append("trainings_period")
            return{"compentency_group":value.title()}
        
        elif value.upper() in Compentency_group_dict.keys():
            print("Inside elif")
            wrong_attempt = 0
            Training_list_form_slot.append("trainings_period")
            return{"compentency_group":value.upper()}
        
        elif wrong_attempt < 3:
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_compentency_group",tracker)
            return {"compentency_group": None}

        else:
            Training_list_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()


    def validate_trainings_period(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        
        print("Value",value)
        global wrong_attempt
        global Training_request_list_form_slot
        global s_date_training,e_date_training

        s_date_training = None
        e_date_training = None

        

        try:
            try:    
                try:

                    print("Inside first try")
                    print(dateparser.parse(value['start_date']))
                    print(dt.datetime.strptime(str(dateparser.parse(value['start_date'])), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
                    s_date_training = dt.datetime.strptime(str(dateparser.parse(value['start_date'])), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    # s_date_training = ((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                    e_date_training = dt.datetime.strptime(str(dateparser.parse(value['end_date'])), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    # e_date_training= 	((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                    print(s_date_training)
                    print(e_date_training)

                except:
                    try:

                        print("Inside first else")
                        print(dateparser.parse(value[1]['start_date']))
                        print(dateparser.parse(value[1]['end_date']))
                        print(dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                     "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
                        s_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # s_date_training = ((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        e_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['end_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # e_date_training= 	((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        s_date_training = ((cal.nlp(value[1]['start_date']))[0][0]).strftime("%d/%m/%Y")
                        e_date_training = ((cal.nlp(value[1]['end_date']))[0][0]).strftime("%d/%m/%Y")
                        print(s_date_training)
                        print(e_date_training)
                        
                    except:
                        
                        print("Inside 2nd else")
                        print(dateparser.parse(value[1]['start_date']))
                        print(dateparser.parse(value[1]['end_date']))
                        print(dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                     "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
                        s_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # s_date_training = ((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        e_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['end_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # e_date_training= 	((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        # s_date_training = ((cal.nlp(value[0]['start_date']))[0][0]).strftime("%d/%m/%Y")
                        # e_date_training = ((cal.nlp(value[1]['end_date']))[0][0]).strftime("%d/%m/%Y")
                        print(s_date_training)
                        print(e_date_training)


            except:

                try:
                    print("Inside 2nd try")
                    s_date_training = ((cal.nlp(value))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(today))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                except:

                    print("Inside 2nd except")
                    s_date_training = ((cal.nlp(value[0]))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(value[1]))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)
        except:
            print(value)
            if value.title() in ["All","All Trainings"]:
                value = "last month"
            else:
                pass
            print("Not matching")

        

        if s_date_training and e_date_training:
            if s_date_training == e_date_training:
                print("Inside if")
                wrong_attempt = 0
                return{"trainings_period":"single"}

            elif s_date_training < e_date_training:
                print("Inside elif")
                wrong_attempt = 0
                return{"trainings_period":"double"}
        
        elif wrong_attempt < 3:
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_trainings_period",tracker)
            return {"trainings_period": None}

        else:
            Training_list_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()

    def validate_number_of_trainee(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        print("Value",value)
        global wrong_number_of_trainee_attempt
        global Training_list_form_slot
        if value.lower() in ["all","all trainees","i want all trainees training detail"]:
            print("Inside if")
            Training_list_form_slot.append("trainings_period")
            return{"number_of_trainee": "all"}
        elif value == "trainee":
            print("inside else")
            Training_list_form_slot.append("trainees")
            Training_list_form_slot.append("trainings_period")
            return{"number_of_trainee": "trainee"}

        elif wrong_number_of_trainee_attempt < 3:
            wrong_number_of_trainee_attempt = wrong_number_of_trainee_attempt + 1
            dispatcher.utter_template("utter_wrong_number_of_trainee",tracker)
            return {"number_of_trainee": None}

        else:
            Training_list_form_slot = []
            wrong_number_of_trainee_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()


    def validate_trainees(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                       domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of trainee ', value)
        global wrong_trainees_attempt
        global name_of_employee
        global valid
        valid = "false"
        u = value.upper()
        print(u.rfind('OMI-'))
        try:
            if u.title() in name_of_employee:
                print(u.title()," u.title()")
                print("name_of_employee[u.title()]",name_of_employee[u.title()])
                valid = "true"
        except:
            valid = "flase"
            print("No name")
        if valid == "true":
            wrong_trainees_attempt = 0
            return {"trainees": name_of_employee[u.title()]}
        
        elif u.rfind('OMI-') == 0:
            print("inside if validate trainee employee code")
            wrong_trainees_attempt = 0
            return {"trainees": u}

        # elif u.title() in name_of_employee:
        #     print( u.title()," u.title()")
        #     return {"trainees": name_of_employee[u.title()]}

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

                        # dispatcher.utter_message("Are you looking for  ")
                        for number in range(len1):
                            name_of_employee.update({"{} {}".format(data[number]['emp_first_name'],data[number]['emp_last_name']):data[number]['emp_code']})
                            buttons.append({"title": data[number]['emp_first_name'] + " " +
                                                     data[number]['emp_last_name'],
                                            "payload": "" + data[number]['emp_code']})
                        if value is None:
                            dispatcher.utter_message(text = "Could you please select appropriate trainee", buttons = buttons)
                        return {"trainees": None}

                elif len(data) is 1:
                    wrong_trainees_attempt = 0
                    return {"trainees": data[0]['emp_code']}

                else:
                    dispatcher.utter_template('utter_wrong_trainees', tracker)
                    return {"trainees": None}
            

            except:

                if wrong_trainees_attempt < 3:

                    wrong_trainees_attempt = wrong_trainees_attempt + 1
                    dispatcher.utter_message(data['errorDesc'])
                    return {"trainees": None}

                else:

                    global Training_list_form_slot
                    Training_list_form_slot = []
                    wrong_trainees_attempt = 0
                    dispatcher.utter_message("You reached to maximum limit of attempt")
                    return self.deactivate()
                
class ActiontrainingList(Action):
    
    def name(self):
        return "action_Training_list_form_submit"
    
    def run(self, dispatcher, tracker, domain):

        global Training_list_form_slot,user
        if len(Training_list_form_slot) < 1:
            if user == "trainee":
                
                return [SlotSet("trainees", None),SlotSet("number_of_trainee","all"),SlotSet("specific_training","Trainee Specific"),SlotSet("trainings_period",None),SlotSet("compentency_group",None)]
            else:
                
                # buttons = []
                # buttons.append({"title": "Yes",
                #                 "payload": "Yes"})
                # buttons.append({"title": "No",
                #                 "payload": "No"})
                # dispatcher.utter_button_message("Do you want get another training details?", buttons)
                return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None)]

        print("Inside submit of training details")

        print("submit detail")

        return []


class ActionShowCompletedTrainings(Action):

    def name(self):
        return "action_show_completed_trainings"

    def run(self, dispatcher, tracker, domain):

        global Training_list_form_slot
        global training
        global user,EMP_name,EMP_last_name,s_date_training,e_date_training,training_type_of_training
        print("action_show_completed_trainings")
        print("tracker.get_slot('number_of_trainee')",tracker.get_slot('number_of_trainee'))
        training_type_of_training = None

        try:
            print("Inside try")

            if tracker.get_slot('specific_training') == "Trainee Specific":
            

                if tracker.get_slot('number_of_trainee') == "all":
                    print("all completed training Trainee Specific")
                    response = requests.get("{}/TrainingofAll?Training_status=Completed&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                                    # print(data)
                    print(len(data))
                    len1 = (len(data))
                    try:

                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))
                            training = {}
                            gt = []

                            for each_training in range(0, len(data)):

                                if user == "trainee":

                                    serial_num = len(training)
                                    print(serial_num,"serial_num")

                                    try:

                                        if data[each_training]["training_type"] == "Inhouse":
                                            training_type_of_training = "Inhouse"
                                        else:
                                            training_type_of_training = "Periodic"
                                    except:
                                        training_type_of_training = "Periodic"
                                    
                                        
                                    training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                            dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 
                                                                 data[each_training]["status"],
                                                                 data[each_training]["tr_code"]]})
                                    print("training updated successfully")
                                    print("Inside completed training user is trainee")
                                    
                                    gt.append({
                                            "type": "List",
                                            "level": "third level",
                                            "title": "Following are completed trainings. You may download it for better view by clicking on link. Please enter Serial number to get details",
                                            "number": each_training,
                                            "links":
                                            [
                                                {
                                                "display_text": "more",
                                                "more_link": "{} {} training".format(data[each_training]["tr_code"],
                                                                           data[each_training]["subject"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,data[each_training]["tr_id"]),
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
                                
                                else:
                                    print("Inside for loop")
                                    print(s_date_training,"s_date_training")
                                    tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                    tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                    print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                    print(e_date_training,'e_date_training')
                                    if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                        serial_num = len(training)
                                        print(serial_num,"serial_num")
                                        try:
                                            if data[each_training]["training_type"] == "Inhouse":
                                                training_type_of_training = "Inhouse"
                                            else:
                                                training_type_of_training = "Periodic"
                                        except:
                                            training_type_of_training = "Periodic"
                                        training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                            dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 
                                                                 data[each_training]["status"],
                                                                 data[each_training]["tr_code"]]})
                                        print("training updated successfully")
                                         
                                        print("User is other")
                                        gt.append({
                                        "type": "List",
                                        "level": "third level",
                                        "title": "Following are completed trainings. You may download it for better view by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                            [
                                                {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],
                                                                           data[each_training]["subject"],
                                                                           data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,data[each_training]["tr_id"]),
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
                            if gt:
                                print("gt",gt)
                                print("Training ",training)
                                dispatcher.utter_custom_json(gt)
                            else:
                                dispatcher.utter_message("I am sorry! There is no training available for given duration")
                                Training_list_form_slot = []
                            return []
                        elif data["errorDesc"]:
                            print("Inside elif of show completed training")
                            Training_list_form_slot = []
                            dispatcher.utter_message("There is no completed training available")
                            # dispatcher.utter_message(data["errorDesc"])
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)                            
                            # return [SlotSet("trainees", None), SlotSet("number_of_trainee", None),SlotSet("ordinal1", None),SlotSet("ordinal2", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

                        else:
                            print("Inside else of show completed training")
                            Training_list_form_slot = []
                            print("response for completed training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)                            
                            # return [SlotSet("trainees", None), SlotSet("number_of_trainee", None),SlotSet("ordinal1", None),SlotSet("ordinal2", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

                    except:
                        print("Inside except of show completed training")
                        Training_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("There is no completed training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                elif tracker.get_slot('trainees') is not None:
                    response = requests.get("{}/TrainingofParticularTrainee?Training_status=Completed&User_Employee_Code={}&Trainee_Employee_code={}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("trainees")))

                    # try:
                    #     print("EMP_name",EMP_name)
                    #     if EMP_name+" "+EMP_last_name  == "{} {}".format(data[each_training]["trainer_id"]["emp_first_name"], data[each_training]["trainer_id"]["emp_last_name"]):
                    #         print("user is trainer")
                    #         user = "trainer"
                    #     else:
                    #         pass
                    # except:
                    #         pass

                    data = response.json()
                    print(len(data))
                    len1 = (len(data))
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            training = {}
                            gt = []
                            for each_training in range(0, len(data)):
                                print("Inside for loop")
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                try:
                                    if data[each_training]["training_type"] == "Inhouse":
                                        training_type_of_training = "Inhouse"
                                    else:
                                        training_type_of_training = "Periodic"
                                except:
                                        training_type_of_training = "Periodic"

                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                
                                    serial_num = len(training)
                                    print(serial_num,"serial_num")
                                    try:
                                        if data[each_training]["training_type"] == "Inhouse":
                                            training_type_of_training = "Inhouse"
                                        else:
                                            training_type_of_training = "Periodic"
                                    except:
                                        training_type_of_training = "Periodic"
                                    training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                            dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 data[each_training]["status"],data[each_training]["tr_code"]]})

                                    print("training updated")
                                     
                                    gt.append({
                                        "type": "List",
                                        "level": "third level",
                                        "title": "Following are completed trainings. You may download it for better view by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                        [
                                            {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],
                                                                                  data[each_training]["subject"],
                                                                                  data[each_training]["trainee_id"][
                                                                                      "emp_first_name"],
                                                                                  data[each_training]["trainee_id"][
                                                                                      "emp_last_name"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url, data[each_training]["tr_id"]),
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

                            if gt:
                                print("gt",gt)
                                print("Training ",training)
                                dispatcher.utter_custom_json(gt)
                            else:
                                dispatcher.utter_message("There is no training available for this trainee given duration")
                                Training_list_form_slot = []
                            return []

                        elif data["errorDesc"]:
                            Training_list_form_slot = []
                            dispatcher.utter_message("There is no completed training available for this trainee")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                        else:
                            Training_list_form_slot = []
                            print("response for ongoing training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    except:
                        Training_list_form_slot = []
                        print("trainings are nor available")
                        print("response for ongoing training", response)
                        dispatcher.utter_message('There is no completed training available for this trainee')
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

            elif tracker.get_slot("specific_training") == "Competency Specific":
                if s_date_training and e_date_training:
                
                    print("all completed training Competency Specific")
                    response = requests.get("{}/TrainingofAll?Training_status=Completed&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                    # print(data)
                    print(len(data))
                    len1 = (len(data))
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))

                            training = {}
                            gt = []

                            for each_training in range(0, len(data)):
                                print("Inside for loop")
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                print("Competency group",tracker.get_slot("compentency_group"))
                                c_grp = tracker.get_slot("compentency_group")
                                global Compentency_group_dict
                                tr_code = Compentency_group_dict[c_grp][1]
                                print(tr_code,"tr_code")
                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                
                                    if (data[each_training]["tr_code"]).find(tr_code) != -1:
                                        serial_num = len(training)
                                        print("serial_num",serial_num)
                                        try:
                                            if data[each_training]["training_type"] == "Inhouse":
                                                training_type_of_training = "Inhouse"
                                            else:
                                                training_type_of_training = "Periodic"
                                        except:
                                            training_type_of_training = "Periodic"

                                        training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                            dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 
                                                                 data[each_training]["status"],
                                                                 data[each_training]["tr_code"]]})

                                        print("training updated successfully")

                            
                                        print("User is other")
                                        gt.append({
                                        "type": "List",
                                        "level": "third level",
                                        "title": "Following are completed trainings. You may download it for better view by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                            [
                                                {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],
                                                                           data[each_training]["subject"],
                                                                           data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,data[each_training]["tr_id"]),
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
                            if gt:
                                print("gt",gt)
                                dispatcher.utter_custom_json(gt)
                            else:
                                dispatcher.utter_message("There is no training available for given competency in given duration")
                                Training_list_form_slot = []
                            print("Training ",training)
                            
                            return []

                        elif data["errorDesc"]:
                            print("Inside elif of show completed training")
                            Training_list_form_slot = []
                            dispatcher.utter_message("There is no completed training available")
                            # dispatcher.utter_message(data["errorDesc"])
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)    
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                        else:
                            print("Inside else of show completed training")
                            Training_list_form_slot = []
                            print("response for completed training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    except:
                        print("Inside except of show completed training")
                        Training_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("There is no completed training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

            elif tracker.get_slot("specific_training") == "Period Specific":
                
                print("all completed training Period Specific")
                response = requests.get("{}/TrainingofAll?Training_status=Completed&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                data = response.json()
                # print(data)
                print(len(data))
                len1 = (len(data))
                try:
                    if response.status_code is 200:
                        data = response.json()
                        print(len(data))
                        len1 = (len(data))

                        training = {}
                        gt = []

                        for each_training in range(0, len(data)):
                            print(s_date_training,"s_date_training")
                            tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                            print(e_date_training,'e_date_training')
                            if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                serial_num = len(training)
                                print("serial_num",serial_num)
                                try:
                                    if data[each_training]["training_type"] == "Inhouse":
                                        training_type_of_training = "Inhouse"
                                    else:
                                        training_type_of_training = "Periodic"
                                except:
                                    training_type_of_training = "Periodic"
                           
                                training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                            dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 
                                                                 data[each_training]["status"],
                                                                 data[each_training]["tr_code"]]})
                                print("training updated successfully")               
                                print("User is other")
                                gt.append({
                                    "type": "List",
                                        "level": "third level",
                                        "title": "Following are completed trainings. You may download it for better view by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                            [
                                                {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],
                                                                           data[each_training]["subject"],
                                                                           data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,data[each_training]["tr_id"]),
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
                        if gt:
                            print("gt",gt)
                            dispatcher.utter_custom_json(gt)
                        else:
                            dispatcher.utter_message("There is no completed training available in given duration")
                            Training_list_form_slot = []
                            print("Training ",training)
                        return []
                    elif data["errorDesc"]:
                        print("Inside elif of show completed training")
                        Training_list_form_slot = []
                        dispatcher.utter_message("There is no completed training available")
                        # dispatcher.utter_message(data["errorDesc"])
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)                            
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    else:
                        print("Inside else of show completed training")
                        Training_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("Sorry! Something went wrong")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                except:
                        print("Inside except of show completed training")
                        Training_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("There is no completed training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

            elif tracker.get_slot("specific_training") == "All":

                try:
                    print("Inside 2nd try")
                    s_date_training = ((cal.nlp("last month"))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp("today"))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                except:

                    print("Inside 2nd except")
                    s_date_training = ((cal.nlp(value[0]))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(value[1]))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                
                print("all completed training all Specific")
                response = requests.get("{}/TrainingofAll?Training_status=Completed&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                data = response.json()
                # print(data)
                print(len(data))
                len1 = (len(data))
                try:
                    if response.status_code is 200:
                        data = response.json()
                        print(len(data))
                        len1 = (len(data))

                        training = {}
                        gt = []

                        for each_training in range(0, len(data)):
                            print(s_date_training,"s_date_training")
                            tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                            print(e_date_training,'e_date_training')
                            if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                serial_num = len(training)
                                print("serial_num",serial_num)
                                try:
                                    if data[each_training]["training_type"] == "Inhouse":
                                        training_type_of_training = "Inhouse"
                                    else:
                                        training_type_of_training = "Periodic"
                                except:
                                    training_type_of_training = "Periodic"
                                training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                            dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 
                                                                 data[each_training]["status"],
                                                                 data[each_training]["tr_code"]]})
                                print("training updated successfully")
                            
                                         
                                print("User is other")
                                gt.append({
                                    "type": "List",
                                        "level": "third level",
                                        "title": "Following are completed trainings. You may download it for better view by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                            [
                                                {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],
                                                                           data[each_training]["subject"],
                                                                           data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,data[each_training]["tr_id"]),
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
                        if gt:
                            print("gt",gt)
                            dispatcher.utter_custom_json(gt)
                        else:
                            dispatcher.utter_message("There is no completed training available in given duration")
                            Training_list_form_slot = []
                            print("Training ",training)
                        return []
                    elif data["errorDesc"]:
                        print("Inside elif of show completed training")
                        Training_list_form_slot = []
                        dispatcher.utter_message("There is no completed training available")
                        # dispatcher.utter_message(data["errorDesc"])
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)                            
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    else:
                        print("Inside else of show completed training")
                        Training_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("Sorry! Something went wrong")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                except:
                        print("Inside except of show completed training")
                        Training_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("There is no completed training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

        except:
            Training_list_form_slot = []
            return [SlotSet("trainees",None),SlotSet("number_of_trainee",None)]


class ActionShowOngoingTrainings(Action):

    def name(self):
        return "action_show_ongoing_trainings"

    def run(self, dispatcher, tracker, domain):

        global Training_list_form_slot,s_date_training,e_date_training
        global training,user,Emp_name,EMP_last_name
        print("all ongoing trainings")
        
        try:
            print("Inside try")

            if tracker.get_slot('specific_training') == "Trainee Specific":

            
                if tracker.get_slot('number_of_trainee') == "all":
                    print("all trainings")
                    response = requests.get("{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                    print(len(data))
                    len1 = (len(data))                
                
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))
                            training = {}
                            gt = []
                            for each_training in range(0,len(data)):  
                                print("Training update of ongoing trainings")
                                if user == "trainee":
                                    serial_num = len(training)
                                    print("serial_num",serial_num)
                                    try:
                                        if data[each_training]["training_type"] == "Inhouse":
                                            training_type_of_training = "Inhouse"
                                        else:
                                            training_type_of_training = "Periodic"
                                    except:
                                        training_type_of_training = "Periodic"

                                    training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                        data[each_training]["subject"],
                                        data[each_training]["comp_group"]["comp_gr_id"],
                                        data[each_training]["trainee_id"]["emp_code"],
                                        data[each_training]["trainer_id"]["emp_code"],
                                        "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                        #    dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        #     dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        #     # dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"), 
                                                                 
                                                                 
                                                                data[each_training]["status"],data[each_training]["tr_code"]]})
                                    print("Training updated successfully of ongoing trainings") 
                                                                  
                                    print("user is trainee")                                     
                                    gt.append({
                                        "type": "List",
                                        "level": "third level",
                                        "title": "Following are ongoing trainings. You may download it by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                            [
                                            {
                                                "display_text": "more",
                                                "more_link": "{} {} - {}".format(data[each_training]["tr_code"],data[each_training]["subject"],data[each_training]["status"]),
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,data[each_training]["tr_id"]),

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
                                else:
                                    serial_num = len(training)
                                    print("serial_num",serial_num)
                                    try:
                                        if data[each_training]["training_type"] == "Inhouse":
                                            training_type_of_training = "Inhouse"
                                        else:
                                            training_type_of_training = "Periodic"
                                    except:
                                        training_type_of_training = "Periodic"
                                    training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                        data[each_training]["subject"],
                                        data[each_training]["comp_group"]["comp_gr_id"],
                                        data[each_training]["trainee_id"]["emp_code"],
                                        data[each_training]["trainer_id"]["emp_code"],
                                        "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                        #    dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        #     dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        #     # dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"), 
                                                                 
                                                                 
                                                                 data[each_training]["status"],data[each_training]["tr_code"]]})
                                    print("Training updated successfully of ongoing trainings") 
                                    
                                    print("User is another user")
                                    gt.append({
                                        "type": "List",
                                            "level": "third level",
                                        "title": "Following are ongoing trainings. You may get details by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                        [
                                            {
                                                "display_text": "more",
                                                "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url, data[each_training]["tr_id"]),

                                                "more_link": "{} {} to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                "link_href": "{}".format(each_training+1),
                                                "button":
                                                    [
                                                        {
                                                            "title": "Approve",
                                                            "payload": "approve"

                                                        },
                                                        {

                                                        "title": "Reject",
                                                        "payload    ": "reject"

                                                        }
                                                    ]

                                            }
                                        ]
                                        }
                                        )
                            
                            print(gt)
                            dispatcher.utter_custom_json(gt)
                            
                            return []

                        elif data["errorDesc"]:

                            Training_list_form_slot = []
                            dispatcher.utter_message("There is no ongoing training available")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                        else:
                            Training_list_form_slot = []
                            print("response for ongoing training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    except:
                        Training_list_form_slot = []
                        print("ongoing Trainings are not avalilable")
                        print("response for ongoing training", response)
                        dispatcher.utter_message("There is no training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                elif tracker.get_slot('trainees') is not None:
                    print("tracker.get_slot('trainees') employee code", tracker.get_slot('trainees'))
                    response = requests.get(
                    "{}/TrainingofParticularTrainee?Training_status=Ongoing&User_Employee_Code={}&Trainee_Employee_code={}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("trainees")))
                    data = response.json()
                    print(len(data))
                    len1 = (len(data))
                
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))


                            training = {}
                            gt = []
                            for each_training in range(0, len(data)):
                                serial_num = len(training)
                                print("serial_num",serial_num)
                                try:
                                    if data[each_training]["training_type"] == "Inhouse":
                                        training_type_of_training = "Inhouse"
                                    else:
                                        training_type_of_training = "Periodic"
                                except:
                                    training_type_of_training = "Periodic"
                               
                                training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                                                 data[each_training]["subject"],
                                                                 data[each_training]["comp_group"]["comp_gr_id"],
                                                                 data[each_training]["trainee_id"]["emp_code"],
                                                                 data[each_training]["trainer_id"]["emp_code"],
                                                                 "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                                dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 
                                                                 data[each_training]["status"],data[each_training]["tr_code"]]})
                                print("Trainings are available")
                                     
                                gt.append({
                                        "type": "List",
                                    "level": "third level",
                                    "title": "Following are ongoing training list. You may get details view by clicking on link. Please enter Serial number to get details",
                                    "number": each_training,
                                    "links":
                                        [
                                            {
                                                "display_text": "more",
                                                "more_link": "{} {} to {} {}".format(data[each_training]["tr_code"],
                                                                                  data[each_training]["subject"],
                                                                                  data[each_training]["trainee_id"][
                                                                                      "emp_first_name"],
                                                                                  data[each_training]["trainee_id"][
                                                                                      "emp_last_name"]),
                                                "link_href": "{}".format(each_training+1),
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
                            print(training)
                            dispatcher.utter_custom_json(gt)
                                
                            return []

                        elif data["errorDesc"]:
                            Training_list_form_slot = []
                            dispatcher.utter_message("There is no ongoing training available for this trainee")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                        else:
                            Training_list_form_slot = []
                            print("response for ongoing training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    except:
                        Training_list_form_slot = []
                        print("Something went wrong")
                        print("response for ongoing training", response)
                        dispatcher.utter_message('There is no training available for this trainee')
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

            elif tracker.get_slot("specific_training") == "Competency Specific":
                
                if s_date_training and e_date_training:
                    print("all trainings")
                    response = requests.get("{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                    print(len(data))
                    len1 = (len(data))                
                
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))
                            training = {}
                            gt = []
                            for each_training in range(0,len(data)):  
                                print("Training update of ongoing trainings")
                                print("Inside for loop")
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                print("Competency group",tracker.get_slot("compentency_group"))
                                c_grp = tracker.get_slot("compentency_group")
                                global Compentency_group_dict
                                tr_code = Compentency_group_dict[c_grp][1]
                                print(tr_code,"tr_code")
                                
                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                
                                    if (data[each_training]["tr_code"]).find(tr_code) != -1:

                                        serial_num = len(training)
                                        print("serial_num",serial_num)
                                        try:
                                            if data[each_training]["training_type"] == "Inhouse":
                                                training_type_of_training = "Inhouse"
                                            else:
                                                training_type_of_training = "Periodic"
                                        except:
                                            training_type_of_training = "Periodic"

                                        training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                            data[each_training]["subject"],
                                            data[each_training]["comp_group"]["comp_gr_id"],
                                            data[each_training]["trainee_id"]["emp_code"],
                                            data[each_training]["trainer_id"]["emp_code"],
                                            "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                           dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"), 
                                                                 
                                                                 
                                                                 data[each_training]["status"],data[each_training]["tr_code"]]})
                                        print("Training updated successfully of ongoing trainings") 
                                                                  
                            
                                    
                                        print("User is another user")
                                        gt.append({
                                            "type": "List",
                                            "level": "third level",
                                            "title": "Following are ongoing trainings. You may get details by clicking on link. Please enter Serial number to get details",
                                            "number": each_training,
                                            "links":
                                            [
                                                {
                                                    "display_text": "more",
                                                    "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url, data[each_training]["tr_id"]),

                                                    "more_link": "{} {} to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                    "link_href": "{}".format(each_training+1),
                                                    "button":
                                                    [
                                                        {
                                                            "title": "Approve",
                                                            "payload": "approve"

                                                        },
                                                        {

                                                        "title": "Reject",
                                                        "payload    ": "reject"

                                                        }
                                                    ]

                                            }
                                        ]
                                        }
                                        )
                            
                            print(gt)
                            dispatcher.utter_custom_json(gt)
                            
                            return []

                        elif data["errorDesc"]:

                            Training_list_form_slot = []
                            dispatcher.utter_message("There is no ongoing training available")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                        else:
                            Training_list_form_slot = []
                            print("response for ongoing training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_management",tracker)
                            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    except:
                        Training_list_form_slot = []
                        print("ongoing Trainings are not avalilable")
                        print("response for ongoing training", response)
                        dispatcher.utter_message("There is no training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

            elif tracker.get_slot("specific_training") == "Period Specific":
                print("all trainings")
                response = requests.get("{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                data = response.json()
                print(len(data))
                len1 = (len(data))                
                
                try:
                    
                    if response.status_code is 200:
                        data = response.json()
                        print(len(data))
                        len1 = (len(data))
                        training = {}
                        gt = []
                        for each_training in range(0,len(data)):  
                            print("Training update of ongoing trainings")
                            print("Inside for loop")
                            print(s_date_training,"s_date_training")
                            tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                            print(e_date_training,'e_date_training')
                                
                
                            if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                serial_num = len(training)
                                print("serial_num",serial_num)
                                try:
                                    if data[each_training]["training_type"] == "Inhouse":
                                        training_type_of_training = "Inhouse"
                                    else:
                                        training_type_of_training = "Periodic"
                                except:
                                    training_type_of_training = "Periodic"
                                training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                            data[each_training]["subject"],
                                            data[each_training]["comp_group"]["comp_gr_id"],
                                            data[each_training]["trainee_id"]["emp_code"],
                                            data[each_training]["trainer_id"]["emp_code"],
                                            "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                           dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"), 
                                                                 
                                                                 
                                                                 data[each_training]["status"],data[each_training]["tr_code"]]})
                                print("Training updated successfully of ongoing trainings") 
                                                                  
                            
                                    
                                print("User is another user")
                                gt.append({
                                            "type": "List",
                                            "level": "third level",
                                            "title": "Following are ongoing trainings. You may get details by clicking on link. Please enter Serial number to get details",
                                            "number": each_training,
                                            "links":
                                            [
                                                {
                                                    "display_text": "more",
                                                    "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url, data[each_training]["tr_id"]),

                                                    "more_link": "{} {} to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                    "link_href": "{}".format(each_training+1),
                                                    "button":
                                                    [
                                                        {
                                                            "title": "Approve",
                                                            "payload": "approve"

                                                        },
                                                        {

                                                        "title": "Reject",
                                                        "payload    ": "reject"

                                                        }
                                                    ]

                                            }
                                        ]
                                        }
                                        )
                            
                        print(gt)
                        dispatcher.utter_custom_json(gt)
                            
                        return []

                    elif data["errorDesc"]:

                        Training_list_form_slot = []
                        dispatcher.utter_message("There is no ongoing training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                    else:
                        Training_list_form_slot = []
                        print("response for ongoing training", response)
                        dispatcher.utter_message("Sorry! Something went wrong")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                except:
                        Training_list_form_slot = []
                        print("ongoing Trainings are not avalilable")
                        print("response for ongoing training", response)
                        dispatcher.utter_message("There is no training available")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]


            elif tracker.get_slot("specific_training") == "All":

                try:
                    print("Inside 2nd try")
                    s_date_training = ((cal.nlp("last month"))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp("today"))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                except:

                    print("Inside 2nd except")
                    s_date_training = ((cal.nlp(value[0]))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(value[1]))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)


                print("all trainings")
                response = requests.get("{}/TrainingofAll?Training_status=Ongoing&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                data = response.json()
                print(len(data))
                len1 = (len(data))                
                
                try:
                    
                    if response.status_code is 200:
                        data = response.json()
                        print(len(data))
                        len1 = (len(data))
                        training = {}
                        gt = []
                        for each_training in range(0,len(data)):  
                            print("Training update of ongoing trainings")
                            print("Inside for loop")
                            print(s_date_training,"s_date_training")
                            tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                            print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                            print(e_date_training,'e_date_training')
                                
                
                            if s_date_training >=  tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                serial_num = len(training)
                                print("serial_num",serial_num)
                                try:
                                    if data[each_training]["training_type"] == "Inhouse":
                                        training_type_of_training = "Inhouse"
                                    else:
                                        training_type_of_training = "Periodic"
                                except:
                                    training_type_of_training = "Periodic"

                                training.update({"{}".format(serial_num + 1): [data[each_training]["tr_id"],
                                            data[each_training]["subject"],
                                            data[each_training]["comp_group"]["comp_gr_id"],
                                            data[each_training]["trainee_id"]["emp_code"],
                                            data[each_training]["trainer_id"]["emp_code"],
                                            "{} {}".format(data[each_training]["trainee_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainee_id"][
                                                                                    "emp_last_name"]),
                                                                 "{} {}".format(data[each_training]["trainer_id"][
                                                                                    "emp_first_name"],
                                                                                data[each_training]["trainer_id"][
                                                                                    "emp_last_name"]),
                                                           dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                            # dt.datetime.strptime(data[each_training]["acEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"), 
                                                                 
                                                                 
                                                                 data[each_training]["status"],data[each_training]["tr_code"]]})
                                print("Training updated successfully of ongoing trainings") 
                                                                  
                            
                                    
                                print("User is another user")
                                gt.append({
                                            "type": "List",
                                            "level": "third level",
                                            "title": "Following are ongoing trainings. You may get details by clicking on link. Please enter Serial number to get details",
                                            "number": each_training,
                                            "links":
                                            [
                                                {
                                                    "display_text": "more",
                                                    "download": "{}/DownloadTrainingSheet?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url, data[each_training]["tr_id"]),

                                                    "more_link": "{} {} to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],data[each_training]["trainee_id"]["emp_first_name"],data[each_training]["trainee_id"]["emp_last_name"]),
                                                    "link_href": "{}".format(each_training+1),
                                                    "button":
                                                    [
                                                        {
                                                            "title": "Approve",
                                                            "payload": "approve"

                                                        },
                                                        {

                                                        "title": "Reject",
                                                        "payload    ": "reject"

                                                        }
                                                    ]

                                            }
                                        ]
                                        }
                                        )
                            
                        print(gt)
                        dispatcher.utter_custom_json(gt)
                            
                            

                    elif data["errorDesc"]:

                        Training_list_form_slot = []
                        dispatcher.utter_message("There is no ongoing training available")
                                # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]


                    else:
                        Training_list_form_slot = []
                        print("response for ongoing training", response)
                        dispatcher.utter_message("Sorry! Something went wrong")
                                # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

                except:
                    Training_list_form_slot = []
                    print("ongoing Trainings are not avalilable")
                    print("response for ongoing training", response)
                    dispatcher.utter_message("There is no training available")
                    # dispatcher.utter_template("utter_continue_Training_management",tracker)
                    return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

        except:
            Training_list_form_slot = []
            return [SlotSet("trainees",None),SlotSet("number_of_trainee",None)]

class SubTrainingDetailForm(FormValidationAction):

    def name(self):
        return "validate_sub_training_detail_form"
    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot")
        global Training_list_form_slot
        global sub_training_detail_slot
        global user

        print("ordinal1",tracker.get_slot("ordinal1"))
        print("len(Training_list_form_slot)",len(Training_list_form_slot))
        if len(Training_list_form_slot) < 1:
            if user == "trainee":
                sub_training_detail_slot = ["ordinal1"]
                return sub_training_detail_slot
            elif user == "trainer":
                sub_training_detail_slot = ["ordinal1"]
                return sub_training_detail_slot
            else:
                sub_training_detail_slot = []
                return sub_training_detail_slot
        else:
            sub_training_detail_slot = ["ordinal1"]
            return sub_training_detail_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping")
        return {
            "ordinal1":
                [
                    self.from_entity(entity="ordinal"),
                    self.from_entity(entity="ordinal1"),
                    self.from_text()
                ]
            }
    
    def validate_ordinal1(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_ordinal1_attempt
        global sub_training_detail_slot
        global training
        global sub_trainings,allowed,user
        sub_trainings = {}
        global compentency_present
        compentency_present = []

        try:
            print("validate ordinal1 inside if value",value)
            sr_no = value
            print(sr_no,"sr_no")
        except:
            print("Validate ordinal1 inside except value",value[1])
            sr_no = value[1]

        try:
            print("inside try")
            print(training.keys(),"training.keys()")
            if sr_no in training.keys():

                print("inside if validate")
                training_id = training[sr_no][0]
                print(training_id)
                response = requests.get("{}/TrainingDetails?Training_Id={}&Training_Type=Periodic".format(mindsconnect_url,training_id))
                data = response.json()
                print(len(data))
                len1 = (len(data))
                global gt1
                gt1 = []
                print(data[1]["tr_lines_id"],"data[1]['tr_lines_id']")
                try:
                    print("EMP_name+''+EMP_last_name",EMP_name+' '+EMP_last_name)
                    if EMP_name+" "+EMP_last_name  == "{} {}".format(data[1]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[1]["tr_sh_id"]["trainer_id"]["emp_last_name"]):
                        print("user is trainer")
                        user = "trainer"
                        print("Allowed",allowed)
                        try:

                            if allowed == "Trainer":
                                print("user is trainer asking for my training")
                                allowed = "Ongoing_trainings"
                        except: 
                            pass

                    else:
                        
                        if allowed == "Trainer":
                            print("user is other asking for my training")
                            allowed = "Ongoing_trainings"
                               
                            dispatcher.utter_message("You are not able to update the status of this trainings because you are not trainer/trainee")
                       
                except:
                    pass

                for sub_training in range(1,len1):
                    
                    compentency_present.append(data[sub_training]["comp_m_id"]["comp_title"])
                    
                    print("for sub_training in range(1,len1):")
                    
                    if allowed == "Completed_training":
                        print('if allowed == "Completed_training":')
                        print('if allowed == "Completed_training":')
                        print('trainee_id {}'.format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"]))
                        print('trainer_id {}'.format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"]))
                        print('comp_group {}'.format(data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"]))
                        print('trainee_name {} {}'.format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]))
                        print('trainer_name: {} {}'.format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]))
                        print('Compentency {}'.format(data[sub_training]["comp_m_id"]["comp_title"]))
                        print('assigned_id {}'.format(data[sub_training]["assigned_to_emp"]["emp_code"]))
                        print('assigned_name {} {}'.format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]))
                        print('nameofTopics{}'.format(data[sub_training]["nameOfTopics"]))
                        print('sub_training_planned_start_date {}'.format(dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y")))
                        print('sub_training_planned_end_date {}'.format(dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y")))
                        print('sub_training_Actual_start_date {}'.format(dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y")))
                        print('sub_training_Actual_end_date {}'.format(dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y")))
                        print('sub_training_start_time {}'.format(data[sub_training]["start_time"]))
                        print('sub_training_end_time {}'.format(data[sub_training]["end_time"]))
                        print('sub_training_training_type {}'.format(data[sub_training]["training_type"]))
                        print('sub_training_trainer_status {}'.format(data[sub_training]["trainerStatus"]))
                        print('sub_training_trainee_status {}'.format(data[sub_training]["status"]))
                                            
                        serial_num = len(sub_trainings)
                        print("serial_num",serial_num)
                        
                        sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                            "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                            "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                            "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                            "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                            "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                            "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                            "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                            "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                            "nameofTopics":data[sub_training]["nameOfTopics"],
                            "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                            "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                            "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                            "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                            "sub_training_start_time":data[sub_training]["start_time"],
                            "sub_training_end_time":data[sub_training]["end_time"],
                            "sub_training_training_type":data[sub_training]["training_type"],
                            "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                            "sub_training_trainee_status":data[sub_training]["status"]}})
                                            
                        gt1.append({
                            "type": "List",
                            "level": "third level",
                            "title": "Following are competencies completed {} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                            "number": sub_training-1,
                            "links":
                                [
                                {
                                    "display_text": "more",
                                    "more_link":
                                    "{}".format(data[sub_training]["nameOfTopics"]),

                                    "link_href":sub_training,

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
                            })
                    elif allowed == "Ongoing_trainings":
                        print(data[sub_training]['status'],"data[sub_training]['status']")
                        try:
                            print("try")
                            if data[sub_training]["status"] == "Completed":
                                print("completed")
                                serial_num = len(sub_trainings)
                                print("serial_num",serial_num)
                                global compentency_list
                                competency_present = []
                                competency_present.append(data[sub_training]["comp_m_id"]["comp_title"])
                                sub_trainings.update({"{}".format(serial_num +1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                         "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                                         "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                                        "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                                         "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],
                                                         data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                                         "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],
                                                         data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                                        "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                                        "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                                        "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                                        "nameofTopics":data[sub_training]["nameOfTopics"],
                                                        "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_start_time":data[sub_training]["start_time"],
                                                                      "sub_training_end_time":data[sub_training]["end_time"],
                                                                      "sub_training_training_type":data[sub_training]["training_type"],
                                                                      "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                                      "sub_training_trainee_status":data[sub_training]["status"]}})
                                
                                gt1.append({
									"type": "List",
									"level": "third level",
									"title": "Following are competenciescompleted",
									"number": sub_training-1,
									"links":
									[
									{
                                    "display_text": "more",
                                    "more_link":
                                    "{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

                                    "link_href":sub_training,

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
									})
                            
                            elif data[sub_training]["status"] == "Pending":
                                try:
                                    print('data[sub_training]["status"] == "Pending":')
                                    serial_num = len(sub_trainings)
                                    print("serial_num",serial_num)
                                    sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                         "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                                         "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                                        "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                                         "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                                         "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                                        "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                                        "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                                        "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                                         "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                         "sub_training_start_time":data[sub_training]["start_time"],
                                                                    #   "sub_training_end_time":data[sub_training]["end_time"],
                                                                      "sub_training_training_type":data[sub_training]["training_type"],
                                                                    "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                                      "sub_training_trainee_status":data[sub_training]["status"]}})
                                    # gt1.append({
									# 	"type": "List",
									# 	"level": "third level",
									# 	"title": "Following are competencies planned by training co-ordinator {} {} ".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
									# 	"number": sub_training-1,
									# 	"links":
									# 	[
									# 	{
									# 	"display_text": "more",
									# 	"more_link":
									# 	"{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

									# 	"link_href":sub_training,

									# 	"button":
									# 		[
									# 			{
									# 				"title": "Approve",
									# 				"payload": "approve"

									# 			},
									# 			{
									# 				"title": "Reject",
									# 				"payload": "reject"

									# 			}
									# 		]

									# }
									# ]
									# })

                                except:
                                    print("pending except")
                                    serial_num = len(sub_trainings)
                                    print("serial_num",serial_num)
                                    sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                         "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                                          "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                                         "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                                          "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                                          "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                                            "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                                         "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                                         "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                                          "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                          #   "sub_training_start_time":data[sub_training]["start_time"],
                                                                     #   "sub_training_end_time":data[sub_training]["end_time"],
                                                        # "sub_training_training_type":data[sub_training]["training_type"],
                                                         "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                         "sub_training_trainee_status":data[sub_training]["status"]}})
                                    # gt1.append({
									# 	"type": "List",
									# 	"level": "third level",
									# 	"title": "Following are competencies planned by training co-ordinator {} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
									# 	"number": sub_training-1,
									# 	"links":
									# 	[
									# 	{
									# 	"display_text": "more",
									# 	 "more_link":
                                    #         "{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

									# 	"link_href":sub_training,

									# 	"button":
									# 		[
									# 			{
									# 				"title": "Approve",
									# 				"payload": "approve"

									# 			},
									# 			{
									# 				"title": "Reject",
									# 				"payload": "reject"

									# 			}
									# 		]

									# }
									# ]
									# })
                            elif data[sub_training]["status"] == "In Progress":
                                try:
                                    print('data[sub_training]["status"] == "In Progress":')
                                    serial_num = len(sub_trainings)
                                    print("serial_num",serial_num)
                                    sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                         "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                                         "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                                        "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                                         "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                                         "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                                            "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                                        "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                                        "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                                         "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                        "sub_training_start_time":data[sub_training]["start_time"],
                                                                    #   "sub_training_end_time":data[sub_training]["end_time"],
                                                                      "sub_training_training_type":data[sub_training]["training_type"],
                                                                    "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                                      "sub_training_trainee_status":data[sub_training]["status"]}})
                                    # gt1.append({
									# 	"type": "List",
									# 	"level": "third level",
									# 	"title": "Following are competencies planned by training co-ordinator {} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
									# 	"number": sub_training-1,
									# 	"links":
									# 	[
									# 	{
									# 	"display_text": "more",
									# 	"more_link":
									# 	"{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

									# 	"link_href":sub_training,

									# 	"button":
									# 		[
									# 			{
									# 				"title": "Approve",
									# 				"payload": "approve"

									# 			},
									# 			{
									# 				"title": "Reject",
									# 				"payload": "reject"

									# 			}
									# 		]

									# }
									# ]
									# })

                                except:
                                    print("In Progress except")
                                    serial_num = len(sub_trainings)
                                    print("serial_num",serial_num)
                                    sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                         "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                                          "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                                         "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                                          "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                                          "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                                            "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                                         "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                                         "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                                          "nameofTopics":data[sub_training]["nameOfTopics"],
                                                        "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                        #   "sub_training_start_time":data[sub_training]["start_time"],
                                                                     #   "sub_training_end_time":data[sub_training]["end_time"],
                                                            "sub_training_training_type":data[sub_training]["training_type"],
                                                         "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                         "sub_training_trainee_status":data[sub_training]["status"]}})
                                    # gt1.append({
									# 	"type": "List",
									# 	"level": "third level",
									# 	"title": "Following are competencies planned by training co-ordinator {} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
									# 	"number": sub_training-1,
									# 	"links":
									# 	[
									# 	{
									# 	"display_text": "more",
									# 	 "more_link":
                                    # "{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

									# 	"link_href":sub_training,

									# 	"button":
									# 		[
									# 			{
									# 				"title": "Approve",
									# 				"payload": "approve"

									# 			},
									# 			{
									# 				"title": "Reject",
									# 				"payload": "reject"

									# 			}
									# 		]

									# }
									# ]
									# })
                            
                            
                            elif data[sub_training]["status"] == "Approved":
                                print("Approved elif")
                                serial_num = len(sub_trainings)
                                print("serial_num",serial_num)
                                sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                    "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                    "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                    "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                    "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                    "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                    "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                    "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                    "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                    "nameofTopics":data[sub_training]["nameOfTopics"],
                                   "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                      "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                    #   "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                                                         #   "sub_training_start_time":data[sub_training]["start_time"],
                                                                    #   "sub_training_end_time":data[sub_training]["end_time"],
                                                                    "sub_training_training_type":data[sub_training]["training_type"],
                                                                    "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                                      "sub_training_trainee_status":data[sub_training]["status"]}})
                                # gt1.append({
								# "type": "List",
								# "level": "third level",
								# "title": "Following are competencies planned by training co-ordinator {} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
								# "number": sub_training-1,
								# "links":
                                # [
                                # {
                                #     "display_text": "more",
                                #      "more_link":
                                #     "{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

                                #     "link_href":sub_training,

                                #     "button":
                                #         [
                                #             {
                                #                 "title": "Approve",
                                #                 "payload": "approve"

                                #             },
                                #             {
                                #                 "title": "Reject",
                                #                 "payload": "reject"

                                #             }
                                #         ]

                                # }
                                # ]
								# })

                            else: 
                                print("inside else")
                                serial_num = len(sub_trainings)
                                print("serial_num",serial_num)
                                sub_trainings.update({"{}".format(serial_num+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                    "trainee_id":data[sub_training]["tr_sh_id"]["trainee_id"]["emp_code"],
                                    "trainer_id":data[sub_training]["tr_sh_id"]["trainer_id"]["emp_code"],
                                    "comp_group":data[sub_training]["tr_sh_id"]["comp_group"]["comp_name"],
                                    "trainee_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainee_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainee_id"]["emp_last_name"]),
                                    "trainer_name":"{} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
                                    "Compentency":data[sub_training]["comp_m_id"]["comp_title"],
                                    "assigned_id":data[sub_training]["assigned_to_emp"]["emp_code"],
                                    "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                    "nameofTopics":data[sub_training]["nameOfTopics"],
                                   "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                    "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                     "sub_training_Actual_start_date":dt.datetime.strptime(data[sub_training]["actualStDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                     #   "sub_training_Actual_end_date":dt.datetime.strptime(data[sub_training]["actualEndDate"],"%b %d, %Y %X %p").strftime("%d/%m/%Y"),
                                    "sub_training_start_time":data[sub_training]["start_time"],
                                    # "sub_training_end_time":data[sub_training]["end_time"],
                                    "sub_training_training_type":data[sub_training]["training_type"],
                                    "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                    "sub_training_trainee_status":data[sub_training]["status"]}})

                                # gt1.append({
								#     "type": "List",
								#     "level": "third level",
								#     "title": "Following are competencies planned by training co-ordinator {} {}".format(data[sub_training]["tr_sh_id"]["trainer_id"]["emp_first_name"],data[sub_training]["tr_sh_id"]["trainer_id"]["emp_last_name"]),
								#     "number": sub_training,
								#     "links":
                                #      [
                                #     {
                                #     "display_text": "more",
                                #      "more_link":
                                #     "{} {}".format(data[sub_training]["nameOfTopics"],data[sub_training]["status"]),

                                #     "link_href":sub_training,

                                #     "button":
                                #         [
                                #             {
                                #                 "title": "Approve",
                                #                 "payload": "approve"

                                #             },
                                #             {
                                #                 "title": "Reject",
                                #                 "payload": "reject"

                                #             }
                                #         ]

                                #     }
                                #     ]
                                #     })
                        except:
                            print("no training")
               
                wrong_ordinal1_attempt = 0
                return {"ordinal1": sr_no}

            elif wrong_ordinal1_attempt < 3:

                print("wrong_ordinal1_attempt", wrong_ordinal1_attempt)
                wrong_ordinal1_attempt = wrong_ordinal1_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"ordinal1": None}

            else:
                sub_training_detail_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt1")
                wrong_ordinal1_attempt = 0
                return self.deactivate()
        except:
            if wrong_ordinal1_attempt < 3:
                print("wrong_ordinal1_attempt", wrong_ordinal1_attempt)
                wrong_ordinal1_attempt = wrong_ordinal1_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"ordinal1": None}

            else:
                sub_training_detail_slot = []
                wrong_ordinal1_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt2")
                return self.deactivate()
            
class ActionSubTrainingDetail(Action):
    
    def name(self):
        return "action_sub_training_detail_form_submit"

    def run(self, dispatcher, tracker, domain):
        global sub_training_detail_slot,allowed,visit,user
        global allowed,gt1,sub_trainings,competency_available
        global sub_training_full_detail_slot,compentency_present
       
        
        if len(sub_training_detail_slot) < 1:
            if allowed == "No":
                # dispatcher.utter_message("There is no training available")
                print("Inside if of form sub_training_detail_slot) < 1:")
            # dispatcher.utter_template("utter_continue_Training_management",tracker)
        else:
            competency_available = []
            competency_available = list(set(compentency_present))
            print("user",user)
            print("allwed",allowed)
            print(len(competency_available),"length of competency available")
            append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
            for i , competency in enumerate(competency_available,1):
                append_msg = append_msg + "<br> {}. {}".format(i,competency)
            dispatcher.utter_message(append_msg)

        #     # buttons = []
        #     # buttons.append({"title": "Yes",
        #     #             "payload": "Yes"})
        #     # buttons.append({"title": "No",
        #     #             "payload": "No"})
        #     # dispatcher.utter_button_message("Do you want get another training details?", buttons)
        #     return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)]
        # elif user == "trainee" and allowed == "Ongoing_trainings":
        #     print("user",user)
        #     print("Inside first elif")
        #     try:
        #         print("Inside first elif try")
        #         if visit != 0:
        #             print("Inside first elif try if")
        #             visit = 0
        #             print(gt1)
        #             # dispatcher.utter_custom_json(gt1)
                    
        #             return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)]
        #         else:
        #             print("Inside first elif try if else")
        #             print(gt1)
        #             # dispatcher.utter_custom_json(gt1)
        #             append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #             for i , competency in enumerate(competency_available,1):
        #                 append_msg = append_msg + "<br> {} {}".format(i,competency)
        #             dispatcher.utter_message(append_msg)
        #             visit = 0   

        #             buttons = []
        #             buttons.append({"title": "Yes",
        #                     "payload": "Yes"})
        #             buttons.append({"title": "No",
        #                     "payload": "No"})
        #             dispatcher.utter_button_message("Do you want update training plan status of training?", buttons)
        #             return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal3", None)]
                
        #     except:
        #         print("Inside first elif except")
        #         visit = 0   
        #         print(gt1)
        #         # dispatcher.utter_custom_json(gt1)
        #         append_msg = "Following are competencies planned by training co-ordinator {}<br> ".format(sub_trainings['1']["trainer_name"])
        #         for i , competency in enumerate(competency_available,1):
        #             append_msg = append_msg + "<br> {} {}".format(i,competency)
        #         dispatcher.utter_message(append_msg)

        #         # buttons = []
        #         # buttons.append({"title": "Yes",
        #         #             "payload": "Yes"})
        #         # buttons.append({"title": "No",
        #         #             "payload": "No"})
        #         # dispatcher.utter_button_message("Do you want get details training plan of training?", buttons)
        #         return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)],SlotSet("ordinal2", None)
        
        # elif user == "trainer" and allowed == "Ongoing_trainings":
        #     print("Inside second eliff")
            
        #     try:
        #         print("Inside second elif try")
        #         if visit != 0:
        #             print("Inside second elif try if ")
        #             visit = 0
        #             print(gt1)
        #             # dispatcher.utter_custom_json(gt1)
        #             append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #             for i , competency in enumerate(competency_available,1):
        #                 append_msg = append_msg + "<br> {} {}".format(i,competency)
        #             dispatcher.utter_message(append_msg)
        #             return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)]
        #         else:
        #             print("Inside second elif try else ")
        #             print(gt1)
        #             # dispatcher.utter_custom_json(gt1)
        #             append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #             for i , competency in enumerate(competency_available,1):
        #                 append_msg = append_msg + "<br> {} {}".format(i,competency)
        #             dispatcher.utter_message(append_msg)
        #             visit = 0   

        #             # buttons = []
        #             # buttons.append({"title": "Yes",
        #             #         "payload": "Yes"})
        #             # buttons.append({"title": "No",
        #             #         "payload": "No"})
        #             dispatcher.utter_button_message("Do you want update training plan status of training?", buttons)
        #             return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal3", None)]
                
        #     except:   
        #         print(gt1)
        #         # dispatcher.utter_custom_json(gt1)
        #         append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #         for i , competency in enumerate(competency_available,1):
        #             append_msg = append_msg + "<br> {} {}".format(i,competency)
        #         dispatcher.utter_message(append_msg)

        #         # buttons = []
        #         # buttons.append({"title": "Yes",
        #         #             "payload": "Yes"})
        #         # buttons.append({"title": "No",
        #         #             "payload": "No"})
        #         # dispatcher.utter_button_message("Do you want get details training plan of training?", buttons)
        #         return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)],SlotSet("ordinal2", None)


        # else:
        #     try:
        #         if visit != 0:
        #             visit = 0
        #             print(gt1)
        #             # dispatcher.utter_custom_json(gt1)
        #             append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #             for i , competency in enumerate(competency_available,1):
        #                 append_msg = append_msg + "<br> {} {}".format(i,competency)
        #             dispatcher.utter_message(append_msg)
        #             return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]
        #         else:   
        #             print(gt1)
        #             # dispatcher.utter_custom_json(gt1)
        #             append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #             for i , competency in enumerate(competency_available,1):
        #                 append_msg = append_msg + "<br> {} {}".format(i,competency)
        #             dispatcher.utter_message(append_msg)

        #             # buttons = []
        #             # buttons.append({"title": "Yes",
        #             #         "payload": "Yes"})
        #             # buttons.append({"title": "No",
        #             #         "payload": "No"})
                            
        #             # dispatcher.utter_button_message("Do you want to get detail status of training plan?", buttons)
        #             return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]
                
        #     except:
        #         visit = 0   
        #         print(gt1)
        #         # dispatcher.utter_custom_json(gt1)
        #         append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
        #         for i , competency in enumerate(competency_available,1):
        #                 append_msg = append_msg + "<br> {} {}".format(i,competency)
        #         dispatcher.utter_message(append_msg)

        #         # buttons = []
        #         # buttons.append({"title": "Yes",
        #         #             "payload": "Yes"})
        #         # buttons.append({"title": "No",
        #         #             "payload": "No"})
        #         # dispatcher.utter_button_message("Do you want to get detail status of training plan?", buttons)
        #         return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]

        print("Inside submit of training details")
        

        print("submit detail")
        return []


class topicsInCompetencyForm(FormValidationAction):

    def name(self):
        return "validate_Topics_in_competency_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot")
        global Training_list_form_slot
        global sub_training_detail_slot
        global Topics_in_competency_form_slot,user,allowed
        if len(sub_training_detail_slot) < 1:
            Topics_in_competency_form_slot = []
        else:
            Topics_in_competency_form_slot = ["competency"]
        return Topics_in_competency_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping competency")
        return {
            "competency":
                [
                    self.from_entity(entity="ordinal"),
                    self.from_entity(entity="competency"),
                    self.from_text()
                ]            
            }
    
    def validate_competency(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt,competency_available
        global Topics_in_competency_form_slot
        global sub_trainings,nameoftopic
        global allowed,show_details,topics
        topics = []

        print("allowed",allowed)

        try:
            print("validate competency inside if value", value)
            sr_no = value
            
        except:
            print("validate competency inside except value", value[1])
            sr_no = value[1]
            print(type(sr_no))

        try:
            print(competency_available)

            try:
        
                user_input = [competency for i,competency in enumerate(competency_available,1) if int(sr_no) is i]
                print(user_input[0])

            except:

                user_input = [competency for i,competency in enumerate(competency_available,1) if sr_no.title() is competency]
                print(user_input[0])

            if user_input is not None:

                print("inside if validate")

                if allowed == "Completed_training":
                    print(len(sub_trainings),"Length of sub training")
                    topics = [sub_trainings[str(i+1)]["nameofTopics"] for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["Compentency"]]
                    print(topics)
                    nameoftopic = ["{} : Planned from {} to {} and status is {}".format(sub_trainings[str(i+1)]["nameofTopics"],sub_trainings[str(i+1)]["sub_training_planned_start_date"],sub_trainings[str(i+1)]["sub_training_planned_end_date"],sub_trainings[str(i+1)]["sub_training_trainee_status"]) for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["Compentency"]]
                    print(nameoftopic)
                    show_details = "Followings are name of topics in compentency {}<br>".format(user_input[0])

                    for i in range(0,len(nameoftopic)):
                        show_details = show_details + "<br>{}. {}".format(i+1,nameoftopic[i])
                    print(show_details)
                elif allowed == "Ongoing_trainings":
                    print(len(sub_trainings),"Length of sub training")
                    len1 = len(sub_trainings)
                    print("elif allowed =='Ongoing_trainings':")
                    print(sub_trainings)
                    ui = user_input[0]
					
					
                    for i in range(1,len1):
						
                        if sub_trainings[str(i)]["Compentency"] == ui:
                            print(sub_trainings[str(i)]["Compentency"],'Competency')
                            print(sub_trainings[str(i)]["nameofTopics"],'Name of topic')
                    
                    
                    topics = [sub_trainings[str(i+1)]["nameofTopics"] for i in range(0,len(sub_trainings)) if sub_trainings[str(i+1)]["Compentency"] == ui]
                    print(topics)

                    try:

                        nameoftopic = ["{} : Planned from {} to {} and status is {}".format(sub_trainings[str(i+1)]["nameofTopics"],sub_trainings[str(i+1)]["sub_training_planned_start_date"],sub_trainings[str(i+1)]["sub_training_planned_end_date"],sub_trainings[str(i+1)]["sub_training_trainee_status"]) for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["Compentency"]]
                        print(nameoftopic)
                        show_details = "Followings are name of topics in compentency {}<br>".format(user_input[0])

                        for i in range(0,len(nameoftopic)):
                            show_details = show_details + "<br>{}. {}".format(i+1,nameoftopic[i])
                        print(show_details)
                    except:
                        nameoftopic = ["{} : Planned from {} to {} and status is {}".format(sub_trainings[str(i+1)]["nameofTopics"],sub_trainings[str(i+1)]["sub_training_planned_start_date"],sub_trainings[str(i+1)]["sub_training_planned_end_date"],sub_trainings[str(i+1)]["sub_training_trainee_status"]) for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["Compentency"]]
                        print(nameoftopic)
                        show_details = "Followings are name of topics in compentency {}<br>".format(user_input[0])

                        for i in range(0,len(nameoftopic)):
                            show_details = show_details + "<br>{}. {}".format(i+1,nameoftopic[i])
                        print(show_details)
                        
                else:
                    # dispatcher.utter_message("I am not able to provide details of sub training")
                    show_details = "I am not able to provide name of topics in training plan of training"
                
                wrong_attempt = 0
                return {"competency": sr_no}

            elif wrong_attempt < 3:

                print("wrong_competency_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"competency": None}

            else:
                Topics_in_competency_form_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt")
                wrong_attempt = 0
                return self.deactivate()

        except:

            if wrong_attempt < 3:

                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"competency": None}

            else:

                Topics_in_competency_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt")
                
                return self.deactivate()

class ActiontopicsInCompetency(Action):
    
    def name(self):
        
        return "action_Topics_in_competency_form_submit"

    def run(self, dispatcher, tracker, domain):
        
        global sub_training_detail_slot,allowed,visit,user
        global allowed,sub_trainings,competency_available,show_details
        global Topics_in_competency_form_slot,compentency_present
       
        if len(Topics_in_competency_form_slot) < 1:
        
            if allowed == "No":
        
                dispatcher.utter_message("There is no training available")
        
            print("Inside if of form")
            dispatcher.utter_template("utter_continue_Training_management",tracker)

            # buttons = []
            # buttons.append({"title": "Yes",
            #             "payload": "Yes"})
            # buttons.append({"title": "No",
            #             "payload": "No"})
            # dispatcher.utter_button_message("Do you want get another training details?", buttons)
            
            return [SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]

        elif user == "trainee" and allowed == "Ongoing_trainings":
            print("user",user)
            print("Inside first elif")
            try:
                print("Inside first elif try")
                if visit != 0:
                    print("Inside first elif try if")
                    visit = 0
                    competency_available = []
                    competency_available = list(set(compentency_present))
                    print("user",user)
                    print("allwed",allowed)
                    dispatcher.utter_message(show_details)
                    return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)]

                else:
                    print("Inside first elif try if else")
                    print(gt1)
                    # dispatcher.utter_custom_json(gt1)
                    dispatcher.utter_message(show_details)
                    visit = 0   

                    buttons = []
                    buttons.append({"title": "Yes",
                            "payload": "Yes"})
                    buttons.append({"title": "No",
                            "payload": "No"})
                    dispatcher.utter_button_message("Do you want update any topic status of training plan?", buttons)
                    return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal3_training", None)]
                
            except:
                print("Inside first elif except")
                visit = 0   
                print(gt1)
                # dispatcher.utter_custom_json(gt1)
                dispatcher.utter_message(show_details)

                buttons = []
                buttons.append({"title": "Yes",
                            "payload": "Yes"})
                buttons.append({"title": "No",
                            "payload": "No"})
                dispatcher.utter_button_message("Do you want get details of topic of training plan?", buttons)
                return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)],SlotSet("ordinal2", None)
        
        elif user == "trainer" and allowed == "Ongoing_trainings":
            print("Inside second eliff")
            
            try:
                
                print("Inside second elif try")
                
                if visit != 0:
                
                    print("Inside second elif try if ")
                    visit = 0
                    print(gt1)
                    # dispatcher.utter_custom_json(gt1)
                    dispatcher.utter_message(show_details)
                    return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)]
                
                else:
                
                    print("Inside second elif try else ")
                    print(gt1)
                    # dispatcher.utter_custom_json(gt1)
                    dispatcher.utter_message(show_details)
                    visit = 0   

                    buttons = []
                    buttons.append({"title": "Yes",
                            "payload": "Yes"})
                    buttons.append({"title": "No",
                            "payload": "No"})
                    dispatcher.utter_button_message("Do you want update any topic status of training plan?", buttons)
                
                    return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal3_training", None)]
                
            except:   
                print(gt1)
                
                # dispatcher.utter_custom_json(gt1)
                dispatcher.utter_message(show_details)

                buttons = []
                buttons.append({"title": "Yes",
                            "payload": "Yes"})
                buttons.append({"title": "No",
                            "payload": "No"})
                dispatcher.utter_button_message("Do you want get details of topic of training plan?", buttons)
                
                return [SlotSet("trainees", None),SlotSet("number_of_trainee", None)],SlotSet("ordinal2", None)

        else:

            try:

                if visit != 0:
                    visit = 0
                    print(gt1)

                    # dispatcher.utter_custom_json(gt1)
                    append_msg = "Following are competencies planned by training co-ordinator {}<br>".format(sub_trainings['1']["trainer_name"])
                    dispatcher.utter_message(show_details)

                    return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]

                else:   

                    print(gt1)
                    # dispatcher.utter_custom_json(gt1)
                    dispatcher.utter_message(show_details)

                    buttons = []
                    buttons.append({"title": "Yes",
                            "payload": "Yes"})
                    buttons.append({"title": "No",
                            "payload": "No"})
                            
                    dispatcher.utter_button_message("Do you want get details of topic of training plan?", buttons)
                    return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]
                
            except:
                visit = 0   
                print(gt1)
                # dispatcher.utter_custom_json(gt1)
                dispatcher.utter_message(show_details)

                buttons = []
                buttons.append({"title": "Yes",
                            "payload": "Yes"})
                buttons.append({"title": "No",
                            "payload": "No"})
                dispatcher.utter_button_message("Do you want get details of topic of training plan?", buttons)
                return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]

        print("Inside submit of training details")
        print("submit detail")
        return []

class SubTrainingfullDetailForm(FormValidationAction):

    def name(self):
        return "validate_Sub_Training_full_Detail_form"

    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot")
        global Training_list_form_slot
        global sub_training_detail_slot
        global sub_training_full_detail_slot,user,allowed
        return sub_training_full_detail_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping ordinal2")
        return {
            "ordinal2":
                [
                    self.from_entity(entity="ordinal2"),
                    self.from_text()
                ],
            "ordinal3_training":
                [
                    self.from_entity(entity="ordinal3_training"),
                    self.from_text()
                ],
            "training_type_trainee": [
                self.from_entity(entity="training_type_trainee"),
                self.from_text(intent="training_type"),
                self.from_text(intent="update"),
                self.from_text()
            ],
            "status":[
                self.from_entity(entity="training_type_trainee"),
                self.from_text(intent="status"),
                self.from_text(intent="update"),
                self.from_text()
            ],
            "training_start_time": [
        
                self.from_text()
            ],
            "training_end_time": [
                
                self.from_text()
            ],
            "training_type_decision":
            [
                self.from_text()
            ]


            }
    
    def validate_training_start_time(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of training_start_time ', value)
        if value is not None:
    
            return {"training_start_time": value}

        else:
            dispatcher.utter_template('utter_wrong_training_start_time',tracker)
            return {"training_start_time": None}
    
    def validate_training_end_time(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:
        global topics

        print('validate value of training_end_time ', value)
        if value is not None:
            sr_no = tracker.get_slot("ordinal3_training")
            print(tracker.get_slot("ordinal3_training"))

            # try:
        
            #     user_input = [topics for i,topics in enumerate(topics,1) if int(ser_no) == i]
            #     print(user_input[0])

            # except:

            #     user_input = [topics for i,topics in enumerate(topics,1) if ser_no == topics]
            #     print(user_input[0])

        

            
            print(sub_trainings.keys())
            # detail = [i+1 for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["nameofTopics"]]
            print(str(detail[0]))

            # # if str(sr_no) in sub_trainings.keys():
            # if str(detail[0]):
            #     sr_no = str(detail[0])

        
            
            if user == "trainee" and allowed == "Ongoing_trainings":
                # if allowed != "Pending_list":
                if sub_trainings[sr_no]["sub_training_trainee_status"] == "Pending":
                    sub_training_full_detail_slot.append("status")
                    dispatcher.utter_message("I am updating training status to In Progress")
                        
                elif sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":
                    try:
                        if tracker.get_slot("training_type_decision") == "Yes":
                            sub_training_full_detail_slot.append("status")
                            dispatcher.utter_message("I am updating training type only")
                        elif tracker.get_slot("training_type_decision") == "No":
                            sub_training_full_detail_slot.append("status")
                            dispatcher.utter_message("I am updating training status to Completed")
                        else:
                            sub_training_full_detail_slot.append("status")
                            dispatcher.utter_message("I am updating training status to Completed") 
                    except:
                        sub_training_full_detail_slot.append("status")
                        dispatcher.utter_message("I am updating training status to Completed")
                elif sub_trainings[sr_no]["sub_training_trainee_status"] == "Completed":
                    dispatcher.utter_message("You have already completed this topic.")
            elif user == "trainer" and allowed == "Ongoing_trainings":
                if sub_trainings[sr_no]["sub_training_trainer_status"] == "Pending":
                    dispatcher.utter_message("I am updating training status to In Progress")
                    sub_training_full_detail_slot.append("status")
                elif sub_trainings[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings[sr_no]["sub_training_trainee_status"] == "Completed":
                    sub_training_full_detail_slot.append("status")
                    sub_training_full_detail_slot.append("training_end_time")
                    dispatcher.utter_message("I am updating training status to Completed")

                elif sub_trainings[sr_no]["sub_training_trainer_status"] == "Completed":
                    dispatcher.utter_message("Trainee have already completed this training.")
                elif sub_trainings[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings[sr_no]["sub_training_trainee_status"] == "Pending" :
                    dispatcher.utter_message("You can not update the status of this training to In progress because the trainee has not yet started training")
                elif sub_trainings[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":
                    dispatcher.utter_message("You can not update the status of this training to completed because the trainee has not yet completed training")

    
            return {"training_end_time": value}

        else:
            dispatcher.utter_template('training_end_time',tracker)
            return {"training_end_time": None}
    
    def validate_training_type_decision(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:
        global sub_training_full_detail_slot,wrong_attempt

        print('validate value of training_type_decision ', value)
        if tracker.latest_message["intent"].get("name") == "affirm":
            sub_training_full_detail_slot.append("training_type_trainee")
                       
            wrong_attempt = 0
            return {"training_type_decision":"Yes"}

        elif tracker.latest_message["intent"].get("name") == "deny":
            sub_training_full_detail_slot.append("training_end_time")
            wrong_attempt = 0
            return {"training_type_decision": "No"}
        
        elif wrong_attempt < 3:
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_template("utter_wrong_training_type_decision",tracker)
                return{"training_type_decision":None}
        else:
            sub_training_full_detail_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
    
    
    def validate_ordinal2(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_ordinal2_attempt

        global sub_training_full_detail_slot
        global sub_trainings,nameoftopic
        global allowed,show_details,topics

        print("allowed",allowed)

        try:
            print("validate ordinal2 inside if value", value)
            ser_no = value
        except:
            print("validate ordinal2 inside except value", value[1])
            ser_no = value[1]
            print(type(sr_no))

        try:
        
            user_input = [topics for i,topics in enumerate(topics,1) if int(ser_no) is i]
            print(user_input[0])

        except:

            user_input = [topics for i,topics in enumerate(topics,1) if ser_no is topics]
            print(user_input[0])

        

        try:
            print(sub_trainings.keys())
            detail = [i+1 for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["nameofTopics"]]
            print(detail[0])

            # if str(sr_no) in sub_trainings.keys():
            if detail[0]:
                sr_no = str(detail[0])

                print("inside if validate")
                if allowed == "Completed_training":
                    print("<b>Here is status of topic {} </b><br><b>Competency Group:</b> {}<br>Competency: {}\nAssigned to Trainer: {}\nPlanned Start Date: {}\nPlanned End Date: {}\nActual Start Date: {}\nActual Completion Date: {}\nTraining Type: {}\nTrainer Status: {}\nTrainee Status: {}".format(sub_trainings[sr_no]["nameofTopics"],
                    sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],
                       
                            sub_trainings[sr_no]["assigned_name"],
                            sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],
                            sub_trainings[sr_no]["sub_training_Actual_start_date"],
                            sub_trainings[sr_no]["sub_training_Actual_end_date"],
                            sub_trainings[sr_no]["sub_training_training_type"],
                            sub_trainings[sr_no]["sub_training_trainer_status"],
                            sub_trainings[sr_no]["sub_training_trainee_status"]))
                    # dispatcher.utter_message("<b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Actual Completion Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>".format(sub_trainings[sr_no]["nameofTopics"], sub_trainings[sr_no]["assigned_name"],
                    #        sub_trainings[sr_no]["sub_training_planned_start_date"],
                    #        sub_trainings[sr_no]["sub_training_planned_end_date"],
                    #        sub_trainings[sr_no]["sub_training_Actual_start_date"],
                    #        sub_trainings[sr_no]["sub_training_Actual_end_date"],
                    #        sub_trainings[sr_no]["sub_training_training_type"],
                    #        sub_trainings[sr_no]["sub_training_trainer_status"],
                    #        sub_trainings[sr_no]["sub_training_trainee_status"]))
                    show_details = "<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br><b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Actual Completion Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>".format(sub_trainings[sr_no]["nameofTopics"], 
                        sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],
                        sub_trainings[sr_no]["assigned_name"],
                           sub_trainings[sr_no]["sub_training_planned_start_date"],
                           sub_trainings[sr_no]["sub_training_planned_end_date"],
                           sub_trainings[sr_no]["sub_training_Actual_start_date"],
                           sub_trainings[sr_no]["sub_training_Actual_end_date"],
                           sub_trainings[sr_no]["sub_training_training_type"],
                           sub_trainings[sr_no]["sub_training_trainer_status"],
                           sub_trainings[sr_no]["sub_training_trainee_status"])
                elif allowed == "Ongoing_trainings":
                    print("elif allowed =='Ongoing_trainings':")
                    if sub_trainings[sr_no]["sub_training_trainee_status"] == "Pending":
                        print('sub_trainings[sr_no]["sub_training_trainee_status"] == "Pending":')
                        try:
                            print("<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br>Competency: {}\nAssigned to Trainer: {}\nPlanned Start Date: {}\nPlanned End Date: {}\nActual Start Date: {}\nTraining Type: {}\nTrainer Status: {}\nTrainee Status: {}".format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                                sub_trainings[sr_no]["sub_training_planned_end_date"],sub_trainings[sr_no]["sub_training_Actual_start_date"],
                                sub_trainings[sr_no]["sub_training_training_type"],sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"]))
                        # dispatcher.utter_message("<b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>"
                        #     .format(sub_trainings[sr_no]["nameofTopics"],
                        #     sub_trainings[sr_no]["assigned_name"],
                        #    sub_trainings[sr_no]["sub_training_planned_start_date"],
                        #    sub_trainings[sr_no]["sub_training_planned_end_date"],
                        #    sub_trainings[sr_no]["sub_training_Actual_start_date"],
                        #    sub_trainings[sr_no]["sub_training_training_type"],
                        #    sub_trainings[sr_no]["sub_training_trainer_status"],
                        #    sub_trainings[sr_no]["sub_training_trainee_status"]))
                            show_details = "<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br><b>Competency: </b> {}<br><b>Assigned to Trainer: </b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type:</b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>".format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                            sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                                sub_trainings[sr_no]["sub_training_planned_end_date"],sub_trainings[sr_no]["sub_training_Actual_start_date"],
                                sub_trainings[sr_no]["sub_training_training_type"],sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"])
                        except:
                            print("Competency: {}\nAssigned to Trainer: {}\nPlanned Start Date: {}\nPlanned End Date: {}\nTrainer Status: {}\nTrainee Status: {}"
                            .format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],
                            sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"]))
                        # dispatcher.utter_message("<b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>"
                        #     .format(sub_trainings[sr_no]["nameofTopics"],
                        #     sub_trainings[sr_no]["assigned_name"],
                        #    sub_trainings[sr_no]["sub_training_planned_start_date"],
                        #    sub_trainings[sr_no]["sub_training_planned_end_date"],
                        #    sub_trainings[sr_no]["sub_training_Actual_start_date"],
                        #    sub_trainings[sr_no]["sub_training_training_type"],
                        #    sub_trainings[sr_no]["sub_training_trainer_status"],
                        #    sub_trainings[sr_no]["sub_training_trainee_status"]))
                            show_details = "<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br><b>Competency: </b> {}<br><b>Assigned to Trainer: </b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>" .format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],
                            sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"])
                    elif sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":
                        print('sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":')
                        try:
                            print("<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br>Competency: {}\nAssigned to Trainer: {}\nPlanned Start Date: {}\nPlanned End Date: {}\nActual Start Date: {}\nTraining Type: {}\nTrainer Status: {}\nTrainee Status: {}".format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                                sub_trainings[sr_no]["sub_training_planned_end_date"],sub_trainings[sr_no]["sub_training_Actual_start_date"],
                                sub_trainings[sr_no]["sub_training_training_type"],sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"]))
                        # dispatcher.utter_message("<b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>"
                        #     .format(sub_trainings[sr_no]["nameofTopics"],
                        #     sub_trainings[sr_no]["assigned_name"],
                        #    sub_trainings[sr_no]["sub_training_planned_start_date"],
                        #    sub_trainings[sr_no]["sub_training_planned_end_date"],
                        #    sub_trainings[sr_no]["sub_training_Actual_start_date"],
                        #    sub_trainings[sr_no]["sub_training_training_type"],
                        #    sub_trainings[sr_no]["sub_training_trainer_status"],
                        #    sub_trainings[sr_no]["sub_training_trainee_status"]))
                            show_details = "<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br><b>Competency: </b> {}<br><b>Assigned to Trainer: </b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type:</b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>".format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                                sub_trainings[sr_no]["sub_training_planned_end_date"],sub_trainings[sr_no]["sub_training_Actual_start_date"],
                                sub_trainings[sr_no]["sub_training_training_type"],sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"])
                        except:
                            print("<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br>Competency: {}\nAssigned to Trainer: {}\nPlanned Start Date: {}\nPlanned End Date: {}\nTrainer Status: {}\nTrainee Status: {}"
                            .format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],
                            sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"]))
                        # dispatcher.utter_message("<b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>"
                        #     .format(sub_trainings[sr_no]["nameofTopics"],
                        #     sub_trainings[sr_no]["assigned_name"],
                        #    sub_trainings[sr_no]["sub_training_planned_start_date"],
                        #    sub_trainings[sr_no]["sub_training_planned_end_date"],
                        #    sub_trainings[sr_no]["sub_training_Actual_start_date"],
                        #    sub_trainings[sr_no]["sub_training_training_type"],
                        #    sub_trainings[sr_no]["sub_training_trainer_status"],
                        #    sub_trainings[sr_no]["sub_training_trainee_status"]))
                            show_details = "<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br><b>Competency: </b> {}<br><b>Assigned to Trainer: </b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>" .format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],
                            sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"])


                    elif sub_trainings[sr_no]["sub_training_trainee_status"] == "Completed":
                        print("<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br>Competency: {}\nAssigned to Trainer: {}\nPlanned Start Date: {}\nPlanned End Date: {}\nActual Start Date: {}\nActual End Date: {}\nTrainer Status: {}\nTrainee Status: {}".format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],sub_trainings[sr_no]["sub_training_Actual_start_date"],sub_trainings[sr_no]["sub_training_Actual_end_date"],
                            sub_trainings[sr_no]["sub_training_training_type"],sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"]))
                        # dispatcher.utter_message("<b>Competency:</b> {}<br><b>Assigned to Trainer:</b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Training Type: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>".format(sub_trainings[sr_no]["nameofTopics"], sub_trainings[sr_no]["assigned_name"],
                        #    sub_trainings[sr_no]["sub_training_planned_start_date"],
                        #    sub_trainings[sr_no]["sub_training_planned_end_date"],
                        # #    sub_trainings[sr_no]["sub_training_Actual_start_date"],
                        # #    sub_trainings[sr_no]["sub_training_training_type"],
                        #    sub_trainings[sr_no]["sub_training_trainer_status"],
                        #    sub_trainings[sr_no]["sub_training_trainee_status"]))
                        show_details = "<b>Here is status of Topic {} </b><br><b>Competency Group:</b> {}<br><b>Competency: </b> {}<br><b>Assigned to Trainer: </b> {}<br><b>Planned Start Date: </b> {}<br><b>Planned End Date: </b> {}<br><b>Actual Start Date: </b> {}<br><b>Actual End Date: </b> {}<br><b>Trainer Status: </b> {}<br><b>Trainee Status: </b> {}<br>".format(sub_trainings[sr_no]["nameofTopics"],sub_trainings[sr_no]["comp_group"],
                        sub_trainings[sr_no]["Compentency"],sub_trainings[sr_no]["assigned_name"],sub_trainings[sr_no]["sub_training_planned_start_date"],
                            sub_trainings[sr_no]["sub_training_planned_end_date"],sub_trainings[sr_no]["sub_training_Actual_start_date"],sub_trainings[sr_no]["sub_training_Actual_end_date"],
                            sub_trainings[sr_no]["sub_training_training_type"],sub_trainings[sr_no]["sub_training_trainer_status"],sub_trainings[sr_no]["sub_training_trainee_status"])
                        
                else:
                    # dispatcher.utter_message("I am not able to provide details of sub training")
                    show_details = "I am not able to provide details of training plan of training"
                
                wrong_ordinal2_attempt = 0
                return {"ordinal2": sr_no}

            elif wrong_ordinal2_attempt < 3:

                print("wrong_ordinal2_attempt", wrong_ordinal2_attempt)
                wrong_ordinal2_attempt = wrong_ordinal2_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"ordinal2": None}

            else:
                sub_training_full_detail_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt")
                wrong_ordinal2_attempt = 0
                return self.deactivate()

        except:

            if wrong_ordinal2_attempt < 3:

                print("wrong_ordinal2_attempt", wrong_ordinal2_attempt)
                wrong_ordinal2_attempt = wrong_ordinal2_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"ordinal2": None}

            else:

                sub_training_full_detail_slot = []
                wrong_ordinal2_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt")
                return self.deactivate()


    def validate_ordinal3_training(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_ordinal2_attempt
        global sub_training_full_detail_slot
        global sub_trainings,topics,user
        global allowed
        print("allowed",allowed)

        try:
            print("validate validate_ordinal3 inside if value", value)
            ser_no = value
            

        except:
            print("validate validate_ordinal3 inside except value", value[1])
            ser_no = value[1]
        try:
        
            user_input = [topics for i,topics in enumerate(topics,1) if int(ser_no) == i]
            print(user_input[0])

        except:

            user_input = [topics for i,topics in enumerate(topics,1) if ser_no == topics]
            print(user_input[0])


        try:
            detail = [i+1 for i in range(0,len(sub_trainings)) if user_input[0] == sub_trainings[str(i+1)]["nameofTopics"]]
            print(detail[0])

            # if str(sr_no) in sub_trainings.keys():
            if detail is not None:
                sr_no = str(detail[0])
                print(sub_trainings.keys())

            # if str(sr_no) in sub_trainings.keys():

                print("inside if validate")
                if user == "trainee" and allowed == "Ongoing_trainings":
                    if sub_trainings[sr_no]["sub_training_trainee_status"] == "Pending":
                        sub_training_full_detail_slot.append("training_type_trainee")
                        
                    elif sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":
                        sub_training_full_detail_slot.append("training_type_decision")
                        # sub_training_full_detail_slot.append("status")
                        # dispatcher.utter_message("I am updating training status to Completed")
                    elif sub_trainings[sr_no]["sub_training_trainee_status"] == "Completed":
                        dispatcher.utter_message("You have already completed this tonic.")
                elif user == "trainer" and allowed == "Ongoing_trainings":
                    print("user is ",user)
                    print('elif user == "trainer" and allowed == "Ongoing_trainings":')
                    if sub_trainings[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":
                        dispatcher.utter_message("I am updating training status to In Progress")
                        sub_training_full_detail_slot.append("status")
                    elif sub_trainings[sr_no]["sub_training_trainer_status"] == "Pending":
                        dispatcher.utter_message("I am updating training status to In Progress")
                        sub_training_full_detail_slot.append("status")
                    elif sub_trainings[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings[sr_no]["sub_training_trainee_status"] == "Completed":
                        sub_training_full_detail_slot.append("status")
                        dispatcher.utter_message("I am updating training status to Completed")
                    elif sub_trainings[sr_no]["sub_training_trainee_status"] == "Completed":
                        
                        dispatcher.utter_message("You have already completed this topic.")
                    elif sub_trainings[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings[sr_no]["sub_training_trainee_status"] == "Pending" :
                        sub_training_full_detail_slot.append("status")
                        dispatcher.utter_message("You can not update the status of this training to In progress because the trainee has not yet started training")
                    elif sub_trainings[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings[sr_no]["sub_training_trainee_status"] == "In Progress":
                        
                        dispatcher.utter_message("You can not update the status of this training to Completed because the trainee has not yet completed training")
                    else:
                        
                        dispatcher.utter_message("You can not update the status of this training because the trainee has not yet started training")
                        
                else:
                    
                    dispatcher.utter_message("You can not update the status of this training because the trainee has not yet started training")


                
                
                wrong_ordinal2_attempt = 0
                return {"ordinal3_training": sr_no}

            elif wrong_ordinal2_attempt < 3:

                print("wrong_ordinal2_attempt", wrong_ordinal2_attempt)
                wrong_ordinal2_attempt = wrong_ordinal2_attempt + 1
                dispatcher.utter_message("You have asked for the training which is not available")
                return {"ordinal3_training": None}

            else:
                sub_training_full_detail_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt")
                wrong_ordinal2_attempt = 0
                return self.deactivate()

        except:

            if wrong_ordinal2_attempt < 3:

                print("wrong_ordinal2_attempt", wrong_ordinal2_attempt)
                wrong_ordinal2_attempt = wrong_ordinal2_attempt + 1
                dispatcher.utter_template("utter_wrong_ordinal3",tracker)
                return {"ordinal3_training": None}

            else:

                sub_training_full_detail_slot = []
                wrong_ordinal2_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt")
                return self.deactivate()
    
    
    def validate_training_type_trainee(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global sub_training_full_detail_slot
        global sub_trainings
        global allowed
        print("allowed",allowed)
           
        print("validate training_type_trainee inside value", value.title())
        
        if value.title() in ["Training","Self Study","Practical"]:
            wrong_attempt = 0
            # sub_training_full_detail_slot.append("status")
            sub_training_full_detail_slot.append("training_start_time")
            sub_training_full_detail_slot.append("training_end_time")
            dispatcher.utter_message(f"I am updating training Type to {value.title()}")
            return{"training_type_trainee":value.title()}
        
        elif wrong_attempt < 3:

            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_training_type_trainee",tracker)
            return{"training_type_trainee":None}
        else:
            sub_training_full_detail_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
    
    
    def validate_status(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global sub_training_full_detail_slot
        global sub_trainings
        global allowed
        print("allowed",allowed)
           
        print("validate status inside except value", value.title())
        print("intent",tracker.latest_message['intent'].get('name'))
        
        if tracker.latest_message['intent'].get('name')  == "affirm" :
            num = tracker.get_slot('ordinal3_training')
            if sub_trainings[num]["sub_training_trainee_status"]  == "Pending":
                wrong_attempt = 0
                return{"status":"In+Progress"}
            elif sub_trainings[num]["sub_training_trainee_status"]== "In Progress":
                try:
                    if tracker.get_slot("training_type_decision") == "Yes":
                        wrong_attempt = 0
                        return{"status":"In+Progress"}
                    elif tracker.get_slot("training_type_decision") == "No":
                        wrong_attempt = 0
                        return{"status":"Completed"}
                    else:
                        wrong_attempt = 0
                        return{"status":"Completed"}
                except:
                    wrong_attempt = 0
                    return{"status":"Completed"}
            elif sub_trainings[num]["sub_training_trainer_status"]  == "Pending":
                wrong_attempt = 0
                return{"status":"In+Progress"}
            elif sub_trainings[num]["sub_training_trainer_status"]== "In Progress":
                wrong_attempt = 0
                return{"status":"Completed"}
               
        elif tracker.latest_message['intent'].get('name') == "status_of_training" :
            wrong_attempt = 0
            return{"status":value}
        elif tracker.latest_message['intent'].get('name') == "affirm": 
            num = tracker.get_slot('ordinal3_training')
            if sub_trainings[num]["sub_training_trainee_status"] == "Pending":
                wrong_attempt = 0
                return{"status":"In+Progress"}
            elif sub_trainings[num]["sub_training_trainee_status"] == "In Progress":
                wrong_attempt = 0
                return{"status":"Completed"}
        elif tracker.latest_message['intent'].get('name') == "deny": 
            wrong_attempt = 0
            return{"status":"No"}
        
        elif wrong_attempt < 3:
            num = tracker.get_slot('ordinal3_training')
            if sub_trainings[num]["sub_training_trainee_status"]== "Pending":
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_template("utter_wrong_status",tracker)
                dispatcher.utter_message("I am going to update training status to In Progress")
                return{"status":None}
            elif sub_trainings[num]["sub_training_trainee_status"]  == "In Progress":
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_template("utter_wrong_status",tracker)
                dispatcher.utter_message("I am going to update training status to Completed")
                return{"status":None}
        else:
            sub_training_full_detail_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
        
class ActionSubTrainingfullDetail(Action):
    
    def name(self):
        return "action_Sub_Training_full_Detail_form_submit"
            
    def run(self, dispatcher, tracker, domain):
        global sub_training_full_detail_slot,visit,selection,user,allowed,show_details,training
        visit = 0
        try:
            if user == "trainee":
                try:
                    if tracker.get_slot("training_type_trainee") and tracker.get_slot("status"):
                        print("Inside trainee status with training type")
                        print("Status: "+tracker.get_slot("status")+" <br>Training type: "+tracker.get_slot("training_type_trainee"))
                        # dispatcher.utter_message("Status: "+tracker.get_slot("status")+" <br>Training type: "+tracker.get_slot("training_type_trainee")
                        # +" <br>start time: "+tracker.get_slot("training_start_time")+" <br>end time: "+tracker.get_slot("training_end_time"))
                        print("Status updated successfully")
                        print(tracker.get_slot("ordinal1"),'tracker.get_slot("ordinal1")')
                        print(tracker.get_slot("ordinal3_training"),'tracker.get_slot("ordinal3_training")')
                        sr_no = tracker.get_slot("ordinal1")
                        sr_no1 = tracker.get_slot("ordinal3_training")
                        print('sub_trainings[sr_no1]["sub_training_trainee_status"]',sub_trainings[sr_no1]["sub_training_trainee_status"])
                        print(training[sr_no][0],'training[sr_no][0]')
                        print(sub_trainings[sr_no1]["sub_training id"],'sub_trainings[sr_no1]["sub_training id"]')
                        if sub_trainings[sr_no1]["sub_training_trainee_status"]  == "Pending":
                            today = str(date.today())
                            print(today)
                            print(sub_trainings[sr_no1]["sub_training id"],'sub_trainings[sr_no1]["sub_training id"]')
                            print(training[sr_no][0])
                            print(sub_trainings[sr_no1]["sub_training id"],'sub_trainings[sr_no1]["sub_training id"]')
                            response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Training_Type={}&Status={}&Actual_Start_Date={}&Start_Time={}&End_Time={}&Trainee_Employee_Code={}".format(mindsconnect_url, training[sr_no][0],sub_trainings[sr_no1]["sub_training id"],tracker.get_slot("training_type_trainee"),tracker.get_slot("status"),
                            today,tracker.get_slot("training_start_time"),tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                            data = response.json()
                            print(response)
                            print(len(data))
                            dispatcher.utter_message(data["errorDesc"])     
                        elif tracker.get_slot("training_type_trainee"):
                            today = str(date.today())
                            print(today)
                            print("Updating training type only")
                            response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status=In+Progress&Training_Type={}&End_Time={}&Trainee_Employee_Code={}".format(mindsconnect_url, training[sr_no][0],sub_trainings[sr_no1]["sub_training id"],tracker.get_slot("training_type_trainee"),tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                            data = response.json()
                            print(data)
                            print(len(data))
                            dispatcher.utter_message("Training type updated successfully!")
                            print(data["errorDesc"])    

                    elif tracker.get_slot("status"):
                        print(tracker.get_slot("ordinal1"),'tracker.get_slot("ordinal1")')
                        print(tracker.get_slot("ordinal3_training"),'tracker.get_slot("ordinal3_training")')
                        sr_no = tracker.get_slot("ordinal1")
                        sr_no1 = tracker.get_slot("ordinal3_training")
                        print('sub_trainings[sr_no1]["sub_training_trainee_status"]',sub_trainings[sr_no1]["sub_training_trainee_status"])
                        print(training[sr_no][0],'training[sr_no][0]')
                        print(sub_trainings[sr_no1]["sub_training id"],'sub_trainings[sr_no1]["sub_training id"]')
                        today = str(date.today())
                        print(today)
                        print("Inside trainee only status")
                        print("Status: "+tracker.get_slot("status"))
                        dispatcher.utter_message("Status: "+tracker.get_slot("status"))
                        response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status={}&Actual_End_Date={}&End_Time={}&Trainee_Employee_Code={}".format(mindsconnect_url, training[sr_no][0],sub_trainings[sr_no1]["sub_training id"],tracker.get_slot("status"),
                        today,tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                        data = response.json()
                        print(data)
                        print(len(data))
                        dispatcher.utter_message(data["errorDesc"])  
                except:
                    print(tracker.get_slot("ordinal1"),'tracker.get_slot("ordinal1")')
                    print(tracker.get_slot("ordinal3_training"),'tracker.get_slot("ordinal3_training")')
                    sr_no = tracker.get_slot("ordinal1")
                    sr_no1 = tracker.get_slot("ordinal3_training")
                    print('sub_trainings[sr_no1]["sub_training_trainee_status"]',sub_trainings[sr_no1]["sub_training_trainee_status"])
                    print(training[sr_no][0],'training[sr_no][0]')
                    print(sub_trainings[sr_no1]["sub_training id"],'sub_trainings[sr_no1]["sub_training id"]')
                    today = str(date.today())
                    print(today)
                    print("Inside trainee only status")
                    print("Status: "+tracker.get_slot("status"))
                    dispatcher.utter_message("Status: "+tracker.get_slot("status"))
                    response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status={}&Actual_End_Date={}&End_Time={}&Trainee_Employee_Code={}".format(mindsconnect_url, training[sr_no][0],sub_trainings[sr_no1]["sub_training id"],tracker.get_slot("status"),
                    today,tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    dispatcher.utter_message(data["errorDesc"])  

            elif user == "trainer":
                if tracker.get_slot("status") == "No":
                    print("Out of status update")

                else:
                    sr_no = tracker.get_slot("ordinal3_training")
                    response = requests.get("{}/UpdateStatusOfTraining?Task_Id={}&Trainer_Status={}&Trainer_employee_code={}".format(mindsconnect_url,sub_trainings[sr_no]["sub_training id"],tracker.get_slot("status"),tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    if data["errorDesc"]  == "Please enter proper Status!":
                        print("Status not updated successfully")
                    else:
                        dispatcher.utter_message(data["errorDesc"])
                        print(tracker.get_slot("status")+" <br>")
                        print("Status updated successfully")
        except:
            print("something went wrong in updated status of tarining")
        if len(sub_training_full_detail_slot) < 1:
            print("len(sub_training_full_detail_slot)")
            dispatcher.utter_template("utter_continue_Training_management",tracker)
            # buttons = []
            # buttons.append({"title": "Yes",
            #             "payload": "Yes"})
            # buttons.append({"title": "No",
            #             "payload": "No"})
            # dispatcher.utter_button_message("Do you want get another training details?", buttons)
            return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal1", None),SlotSet("ordinal2", None),SlotSet("ordinal3_training", None)]
        elif user == "trainee" and allowed == "Ongoing_trainings":
            dispatcher.utter_template("utter_continue_Training_management",tracker)
            return [SlotSet("competency",None),SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
        
        elif user == "trainer" and allowed == "Ongoing_trainings":
            # visit = visit + 1
            # selection = tracker.get_slot("ordinal1")
            # buttons = []
            # buttons.append({"title": "Yes", "payload": "Yes"})
            # buttons.append({"title": "No","payload": "No"})
            # dispatcher.utter_button_message("Do you want to update status of next compentency of this training?", buttons)
            dispatcher.utter_message(template="utter_continue_Training_management")
            return [SlotSet("competency",None),SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
        
        else:
            
            # visit = visit + 1
            # selection = tracker.get_slot("ordinal1")
            # buttons = []
            # buttons.append({"title": "Yes", "payload": "Yes"})
            # buttons.append({"title": "No","payload": "No"})
            dispatcher.utter_message(show_details)
            # dispatcher.utter_button_message("Do you want to get status of next compentency of this training?", buttons)
            # return [SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None)]
            dispatcher.utter_message(template="utter_continue_Training_management")
            return [SlotSet("competency",None),SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
        

        print("Inside submit of training details")

        print("submit detail")

        return []

class ActionContinueWithSubTrainingDetails(Action):

    def name(self):
        return "action_continue_with_sub_training_details"

    def run(self, dispatcher, tracker, domain):
        current_intent = tracker.latest_message['intent'].get('name')
        print(current_intent)
        global sub_training_detail_slot,sub_training_full_detail_slot,user
        # if len(sub_training_detail_slot) < 1:
        #     sub_training_full_detail_slot = []
            
        # elif (user == "trainee" and allowed == "Ongoing_trainings") or  (user == "trainer" and allowed == "Ongoing_trainings"):
        #     sub_training_full_detail_slot = ["ordinal3"]
            
            
        # else:
        #     sub_training_full_detail_slot = ["ordinal2"]
        #     current_intent = "None"
       

        if current_intent == "affirm":
            print("if current_intent is 'affirm':")
            if len(sub_training_detail_slot) < 1:
                sub_training_full_detail_slot = []
            
            elif user == "trainee" and allowed == "Ongoing_trainings":
                print('traine  sub_training_full_detail_slot = ["ordinal3_training"]')
                sub_training_full_detail_slot = ["ordinal3_training"]
            elif user == "trainer" and allowed == "Ongoing_trainings":
                print('trainer sub_training_full_detail_slot = ["ordinal3_training"]')
                sub_training_full_detail_slot = ["ordinal3_training"]
            else:
                sub_training_full_detail_slot = ["ordinal2"]
                
            current_intent = "None"
            return [SlotSet("specific_training",None),SlotSet("competency",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
        elif current_intent == "deny":
            print("if current_intent is 'deny':")
            current_intent = "None"
            dispatcher.utter_message(template="utter_continue_Training_management")
            return [SlotSet("competency",None),SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision",None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee",None)]
        else:
            print("else current_intent")
            current_intent = "None"
            dispatcher.utter_message(template="utter_continue_Training_management")
            return [SlotSet("competency",None),SlotSet("specific_training",None),SlotSet("compentency_group",None),SlotSet("trainings_period",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees", None),SlotSet("number_of_trainee", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3_training", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
        
class trainingRequestsListForm(FormValidationAction):

    def name(self):

        return "validate_Training_request_list_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot of trining _request list form")
        trainees_emp_code = []
        trainees_name = []
        global Training_request_list_form_slot
        global current_intent_of_training_request
        global allowed_request,user_request,selection_request,visit_request
        visit_request = 0
        user_request = "None"
        if tracker.get_slot("emp_code") in ["OMI-0001","OMI-0086"]:
            user_request = "admin"
       
        try:
            print("Inside Try")
            response = requests.get("{}/ListofTrainees?Training_Type=Periodic".format(mindsconnect_url))
            data = response.json()
            # print(data)
            print(data[0]['emp_code'])

            for i in range(0, len(data)):
                trainees_emp_code.append(data[i]['emp_code'])
                trainees_name.append(data[i]['emp_first_name'] + " " + data[i]['emp_last_name'])

            print(trainees_emp_code)
            print(trainees_name)

            try:
                response1 = requests.get("{}/ListofTrainees?Training_Type=Inhouse".format(mindsconnect_url))
                data1 = response1.json()
                for i in range(0, len(data1)):
                    trainees_emp_code.append(data1[i]['emp_code'])
                    trainees_name.append(data1[i]['emp_first_name'] + " " + data1[i]['emp_last_name'])
                print(trainees_emp_code)
                print(trainees_name)
            except:
                print("no inhouse training")

        except:
            Training_request_list_form_slot = []
            print("No one is trainee")

        try:
           
            current_intent_of_training_request = tracker.latest_message['intent'].get('name')
            print(current_intent_of_training_request, "current_intent_of_training_request")
            if current_intent_of_training_request == "Approved_list":
                allowed_request = "Approved_list"

                response = requests.get("{}/TrainingRequestofAll?Training_request_name=Approved&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                data = response.json()
                print(data)
                print(len(data))
                print(data["errorCode"], "data['errorCode']")
                training = len(data)
                print(training)
            elif current_intent_of_training_request == "Pending_list":
                    allowed_request = "Pending_list"
                    response = requests.get(
                    "{}/TrainingRequestofAll?Training_request_name=Pending&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                    data = response.json()
                    print(data)
                    print(len(data))
                    print(data["errorCode"], "data['errorCode']")
                    training = len(data)
                    print(training)
                    # allowed_request = "Pending_for_approval_list"
                    response1 = requests.get(
                    "{}/TrainingRequestofAll?Training_request_name=Pending for Approval&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot('emp_code')))
                    data1 = response1.json()
                    print(data1)
                    print(len(data1))
                    print(data["errorCode"], "data['errorCode']")
                    training1 = len(data1)
                    print(training1)

            else:
                print("other intent")
                data = "other intent"

            try:
                if data['errorCode'] and data1['errorCode']:
                    print("inside try if")
                    print(data["errorCode"], "data['errorCode']")
                    allowed_request = "No"
                    # dispatcher.utter_message("Trainings not available!")
                    Training_request_list_form_slot = []
                    return Training_request_list_form_slot
            except:
                print(tracker.get_slot("number_of_trainee_for_request"),'tracker.get_slot("number_of_trainee_for_request")')
                print(tracker.get_slot("trainees_for_request"),'tracker.get_slot("trainees_for_request")')
                if tracker.get_slot("number_of_trainee_for_request") == "all":
                    if allowed_request == "Approved_list":
                        print("Inside tracker of number of trainee",tracker.get_slot("number_of_trainee_for_request"))
                        Training_request_list_form_slot = ["number_of_trainee_for_request","trainings_period"]
                        return Training_request_list_form_slot
                    else:
                        
                        print("Inside tracker of number of trainee",tracker.get_slot("number_of_trainee_for_request"))
                        Training_request_list_form_slot = ["number_of_trainee_for_request"]
                        return Training_request_list_form_slot

                # elif tracker.get_slot("number_of_trainee_for_request") == "trainee":
                #     print("Inside tracker of number of trainee",tracker.get_slot("number_of_trainee_for_request"))
                #     # Training_request_list_form_slot = ["number_of_trainee_for_request","trainees_for_request"]
                #     Training_request_list_form_slot = ["trainees_for_request"]
                #     return Training_request_list_form_slot

                elif tracker.get_slot("emp_code") in trainees_emp_code:
                    print("User is trainee")
                    user_request = "trainee"
                    Training_request_list_form_slot = []
                    return Training_request_list_form_slot
                 
                elif tracker.get_slot("emp_code") in trainees_emp_code and tracker.get_slot("trainees_for_request"):
                    print("User is trainee asking for trainee")
                    Training_request_list_form_slot = ["trainees_for_request"]
                    # Training_request_list_form_slot = []
                    SlotSet("number_of_trainee_for_request","trainee")
                    return Training_request_list_form_slot

                elif tracker.get_slot("emp_code") in trainees_emp_code and tracker.get_slot("number_of_trainee_for_request") == "all":
                    print("User is trainee asking for all training")
                    user_request = "trainee"
                    SlotSet("number_of_trainee_for_request","all")
                    Training_request_list_form_slot = ["number_of_trainee_for_request"]
                    return Training_request_list_form_slot

                elif tracker.get_slot("number_of_trainee_for_request") == "trainee" and tracker.get_slot("trainees_for_request") is None:
                    print("User is other asking for trainee")
                    Training_request_list_form_slot = ["trainees_for_request"]
                    SlotSet("number_of_trainee_for_request","trainee")
                    return Training_request_list_form_slot

                elif tracker.get_slot("trainees_for_request"):
                    if allowed_request == "Approved_list":
                        print("Inside tracker of trainees_for_request",tracker.get_slot("trainees_for_request"))
                        Training_request_list_form_slot = ["trainees_for_request","trainings_period"]
                        return Training_request_list_form_slot
                    else:
                        print("User is other asking for trainee")
                        Training_request_list_form_slot = ["trainees_for_request"]
                        SlotSet("number_of_trainee_for_request","trainee")
                        return Training_request_list_form_slot                   


            # elif data["errorCode"] is 105:
            #     print(data["errorCode"], "data['errorCode']")
            #     print('Trainings are not available!')
            #     dispatcher.utter_message(data["errorDesc"])
            #     Training_list_form_slot = []
            #     return Training_list_form_slot

                elif data == "other intent":
                    if tracker.latest_message['intent'].get('name') == "Training_specification":
                        if  tracker.get_slot("specific_training") == "Trainee Specific":
                            Training_request_list_form_slot = ["number_of_trainee_for_request"]
                        elif  tracker.get_slot("specific_training") == "Period Specific":
                            Training_request_list_form_slot = ["trainings_period"]
                        elif  tracker.get_slot("specific_training") == "Competency Specific":
                            Training_request_list_form_slot = ["compentency_group","trainings_period"]
                    return Training_request_list_form_slot

                elif allowed_request == "Approved_list":
                    print("Inside else")
                    Training_request_list_form_slot = ["specific_training"]
                    return Training_request_list_form_slot
                
                else:
                    print("Inside else")
                    Training_request_list_form_slot = ["number_of_trainee_for_request"]
                    return Training_request_list_form_slot

        except:
        
            print("Inside else")
            Training_request_list_form_slot = ["number_of_trainee_for_request"]
            return Training_request_list_form_slot


        return  Training_request_list_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        print("slot mapping")

        return {

            "number_of_trainee_for_request": [
                self.from_entity(entity="number_of_trainee_for_request"),
                self.from_text(intent="number_of_trainee_details"),
                self.from_text()
            ],

            "trainees_for_request":[
                self.from_entity(entity="PERSON"),
                self.from_entity(entity="trainees_for_request"),
                self.from_entity(entity="ORG"),
                self.from_entity(entity="name2"),
                self.from_text(intent="data"),
                self.from_text(intent="number_of_trainee_details"),
                self.from_text(intent="trainee_details"),
                self.from_text(intent="Training_request"),
                self.from_text(intent="Approved_list"),
                self.from_text(intent="Pending_list"),
                self.from_text()
            ],
            "compentency_group":
            [
                self.from_text()

            ],

            "trainings_period":[
                
                self.from_entity(entity="daterange"),
                self.from_entity(entity="trainings_period"),
                self.from_text()

            ],

            "specific_training":[
                self.from_text(),
                self.from_text(intent="Training_specification"),
                self.from_text()
                
            ]
        }
    

    def validate_specific_training(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:

        print("Value",value)
        global wrong_attempt
        global Training_request_list_form_slot

        if value.title() in ["Competency Specific","Competency","Technology","Languages","Skills","Competency Specific","Compentency Specific","Compentency"]:
            print("Inside if")
            wrong_attempt = 0
            Training_list_form_slot.append("compentency_group")
            return{"specific_training":"Competency Specific"}

        elif value.title() in ["Period Specific","Period","Time","Month","Weekly"]:
            print("Inside elif")
            wrong_attempt = 0
            Training_request_list_form_slot.append("trainings_period")
            return{"specific_training":"Period Specific"}

        elif value.title() in ["Trainee Specific","Trainee","A Trainee","A Particular Trainee"]:
            print("Inside elifif")
            wrong_attempt = 0
            Training_request_list_form_slot.append("number_of_trainee_for_request")
            return{"specific_training":"Trainee Specific"}
        
        elif value.title() in ["All","All Trainings"]:
            print("Inside elifif")
            wrong_attempt = 0
            Training_request_list_form_slot.append("trainings_period")
            return{"specific_training":"All"}

        elif wrong_attempt < 3:
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_specific_training",tracker)
            return {"specific_training": None}

        else:
            Training_request_list_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()

    def validate_compentency_group(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        
        print("competency group Value",value)
        global wrong_attempt
        global Training_request_list_form_slot
        global Compentency_group_dict
        Compentency_group_dict = {}
        # Compentency_group_dict = {'Dot Net':[1,'DNET'],'Python':[11,'PY'],'Javascript':[12,'JS'],'Java':[13,'JAVA'],'VBA':[21,'VBA'],'Automation Anywhere':[22,'AAP'],'RASA Chatbot Platform':[41,'RCP'],'Java':[61,'JAV'],'Database':[62,'DTB'],'UI':[63,'UIT'],'Server':[64,'SVR'],'ODA':[81,'ODA'],'OPA Training':[101,'OPA'],'Test Engineering':[102,'STE'],'R  Programming Language':[103,'RPL'],'RPA for Sales Professionals':121,'Oracle Digital Assistant Certification':141,'OPA Cloud Service 2017 Sales Specialist':165,'OPA Cloud Service 2019 Sales Specialist':166,'OPA Cloud Service 2019 Solution Engineer':167,'OPA 2019 Implementation Essentials Certification':183,'AA Partner Sales Professional Accreditation ':202,'AA Partner Sales Engineer Accreditation ':204,'Connector Development':[221,'OCD']}
        
        response = requests.get("{}/getCompetencyGroupInformation".format(mindsconnect_url))
        data = response.json()
        for i in range(0,len(data)):

            Compentency_group_dict.update({data[i]['comp_name']:[data[i]['comp_gr_id'],data[i]['abbreviation']]})
       

        if value.title() in Compentency_group_dict.keys():

            print("Inside elif")
            wrong_attempt = 0
            Training_request_list_form_slot.append("trainings_period")
            return{"compentency_group":value.title()}

        elif value.upper() in Compentency_group_dict.keys():
            print("Inside elif")
            wrong_attempt = 0
            Training_request_list_form_slot.append("trainings_period")
            return{"compentency_group":value.upper()}
        
        elif wrong_attempt < 3:
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_compentency_group",tracker)
            return {"compentency_group": None}

        else:
            Training_request_list_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()


    def validate_trainings_period(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) -> Optional[Text]:
        
        print("Value",value)
        global wrong_attempt
        global Training_request_list_form_slot
        global s_date_training,e_date_training

        s_date_training = None
        e_date_training = None

        

        try:
            try:    
                try:

                    print("Inside first try")
                    print(dateparser.parse(value['start_date']))
                    print(dt.datetime.strptime(str(dateparser.parse(value['start_date'])), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
                    s_date_training = dt.datetime.strptime(str(dateparser.parse(value['start_date'])), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    # s_date_training = ((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                    e_date_training = dt.datetime.strptime(str(dateparser.parse(value['end_date'])), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                    # e_date_training= 	((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                    print(s_date_training)
                    print(e_date_training)

                except:
                    try:

                        print("Inside first else")
                        print(dateparser.parse(value[1]['start_date']))
                        print(dateparser.parse(value[1]['end_date']))
                        print(dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                     "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
                        s_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # s_date_training = ((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        e_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['end_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # e_date_training= 	((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        s_date_training = ((cal.nlp(value[1]['start_date']))[0][0]).strftime("%d/%m/%Y")
                        e_date_training = ((cal.nlp(value[1]['end_date']))[0][0]).strftime("%d/%m/%Y")
                        print(s_date_training)
                        print(e_date_training)
                    except:
                        print("Inside 2nd else")
                        print(dateparser.parse(value[1]['start_date']))
                        print(dateparser.parse(value[1]['end_date']))
                        print(dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                     "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y"))
                        s_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['start_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # s_date_training = ((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        e_date_training = dt.datetime.strptime(str(dateparser.parse(value[1]['end_date'])),
                                                         "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y")
                        # e_date_training= 	((cal.nlp(value['start_date']))[0][0]).strftime("%b %Y")
                        # s_date_training = ((cal.nlp(value[0]['start_date']))[0][0]).strftime("%d/%m/%Y")
                        # e_date_training = ((cal.nlp(value[1]['end_date']))[0][0]).strftime("%d/%m/%Y")
                        print(s_date_training)
                        print(e_date_training)


            except:

                try:
                    print("Inside 2nd try")
                    s_date_training = ((cal.nlp(value))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(today))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                except:

                    print("Inside 2nd except")
                    s_date_training = ((cal.nlp(value[0]))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(value[1]))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)
        except:
            print(value)
            if value.title() in ["All","All Trainings"]:
                value = "last month"
            else:
                pass
            print("Not matching")

        if s_date_training and e_date_training:
            if s_date_training == e_date_training:
                print("Inside if")
                wrong_attempt = 0
                return{"trainings_period":"single"}

            elif s_date_training < e_date_training:
                print("Inside elif")
                wrong_attempt = 0
                return{"trainings_period":"double"}
        
        elif wrong_attempt < 3:
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_trainings_period",tracker)
            return {"trainings_period": None}

        else:
            Training_request_list_form_slot = []
            wrong_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()

    
    
    def validate_number_of_trainee_for_request(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                          domain: Dict[Text, Any]) ->Optional[Text]:
        print("Value",value)
        global wrong_number_of_trainee_for_request_attempt
        global Training_request_list_form_slot
        if value.lower() in ["all","all trainees","i want all trainees training detail"]:
            print("Inside if")
            Training_request_list_form_slot.append("trainings_period")
            wrong_number_of_trainee_attempt = 0
            return{"number_of_trainee_for_request": "all"}
        elif value == "trainee":
            print("inside else")
            
            Training_request_list_form_slot.append("trainees_for_request")
            Training_request_list_form_slot.append("trainings_period")
            wrong_number_of_trainee_attempt = 0
            return{"number_of_trainee_for_request": "trainee"}
        elif wrong_number_of_trainee_attempt < 3:
            wrong_number_of_trainee_attempt = wrong_number_of_trainee_for_request_attempt + 1
            dispatcher.utter_template("utter_wrong_number_of_trainee_for_request",tracker)
            return {"number_of_trainee_for_request": None}
        else:
            Training_request_list_form_slot = []
            wrong_number_of_trainee_attempt = 0
            dispatcher.utter_message("You reached to maximum limit of attempt")
            return self.deactivate()


    def validate_trainees_for_request(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                       domain: Dict[Text, Any]) -> Optional[Text]:
        print('validate value of trainee ', value)

        global wrong_trainees_attempt
        global name_of_employee
        global valid
        valid = "false"
        u = value.upper()
        print(u.rfind('OMI-'))
        try:
            if u.title() in name_of_employee:
                print(u.title()," u.title()")
                print("name_of_employee[u.title()]",name_of_employee[u.title()])
                valid = "true"
        except:
            valid = "flase"
            print("No name")
        if valid == "true":
            wrong_trainees_attempt = 0
            return {"trainees_for_request": name_of_employee[u.title()]}
        elif u.rfind('OMI-') == 0:
            print("inside if validate trainee employee code")
            wrong_trainees_attempt = 0
            return {"trainees_for_request": u}

        # elif u.title() in name_of_employee:
        #     print( u.title()," u.title()")
        #     return {"trainees_for_request": name_of_employee[u.title()]}

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
                        # dispatcher.utter_message("Are you looking for  ")
                        for number in range(len1):
                            name_of_employee.update({"{} {}".format(data[number]['emp_first_name'],data[number]['emp_last_name']):data[number]['emp_code']})
                            buttons.append({"title": data[number]['emp_first_name'] + " " +
                                                     data[number]['emp_last_name'],
                                            "payload": "" + data[number]['emp_code']})

                    dispatcher.utter_button_message("Could you please select appropriate trainee?", buttons)
                    return {"trainees_for_request": None}

                elif len(data) is 1:
                    wrong_trainees_attempt = 0
                    return {"trainees_for_request": data[0]['emp_code']}

                else:
                    dispatcher.utter_template('utter_wrong_trainees', tracker)
                    return {"trainees_for_request": None}
            
            except:

                if wrong_trainees_attempt < 3:

                    wrong_trainees_attempt = wrong_trainees_attempt + 1
                    dispatcher.utter_message(data['errorDesc'])
                    return {"trainees_for_request": None}

                else:

                    global Training_request_list_form_slot
                    Training_request_list_form_slot = []
                    wrong_trainees_attempt = 0
                    dispatcher.utter_message("You reached to maximum limit of attempt")
                    return self.deactivate()

class ActiontrainingRequestsListForm(Action):
    
    def name(self):

        return "action_Training_request_list_form_submit"

    def run(self, dispatcher, tracker, domain):

        global Training_request_list_form_slot,user_request
        if len(Training_request_list_form_slot) < 1:
            if user_request == "trainee":
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request","all"),SlotSet("specific_training","Trainee Specific")]
            else:
                # buttons = []
                # buttons.append({"title": "Yes",
                #                 "payload": "Yes"})
                # buttons.append({"title": "No",
                #                 "payload": "No"})
                # dispatcher.utter_button_message("Do you want to get status of next compentency of this training?", buttons)
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


        print("Inside submit of training details")

        print("submit detail")

        return []


class ActionShowApprovedTrainings(Action):

    def name(self):
        return "action_show_approved_training_request"

    def run(self, dispatcher, tracker, domain):

        global Training_request_list_form_slot
        global training_request
        global user_request,EMP_name,EMP_last_name,s_date_training,e_date_training
               
        print("action_show_Approved_trainings")
        print("tracker.get_slot('number_of_trainee_for_request')",tracker.get_slot('number_of_trainee_for_request'))

        try:
            print("Inside try")
            if tracker.get_slot('specific_training') == "Trainee Specific":
                if tracker.get_slot('number_of_trainee_for_request') == "all":
                    print("all approved training")
                    response = requests.get("{}/TrainingRequestofAll?Training_request_name=Approved&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    len1 = (len(data))
                    print(EMP_name+" "+EMP_last_name)
                    print("{} {}".format(data[0]["trainerFirstName"],data[0]["trainerLastName"]))
                
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))
                            print('data[each_training]["tr_id"]',data[0]["tr_id"])

                            training_request = {}
                            gt = []


                            for each_training in range(0, len(data)):
                                if user_request == "trainee":
                                    serial_num = len(training_request)
                                    print(serial_num,"serial_num")
                                    
                                    training_request.update({serial_num + 1: {"training_id":data[each_training]["tr_id"],
                                                                "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Approved"}})
                                    print("After training requests")

                                    gt.append({
                                    "type": "List",
                                    "level": "third level",
                                    "title": "Following are Approved training requests. You may get details by clicking on link. Please enter Serial number to get details",
                                    "number": each_training,
                                    "links":
                                    [
                                        {
                                            "display_text": "more",
                                            "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],
                                                                           data[each_training]["traineeFirstName"],data[each_training]["traineeLastName"]),
                                            "link_href": "{}".format(each_training+1),
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

                                else:
                                    print("user is other")
                                    print("Inside for loop")
                                    print(s_date_training,"s_date_training")
                                    tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                    tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                    print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                    print(e_date_training,'e_date_training')
                                    if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                        serial_num = len(training_request)
                                        print(serial_num,"serial_num")
                                    
                                        training_request.update({serial_num + 1: {"training_id":data[each_training]["tr_id"],
                                                                "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Approved"}})
                                        print("After training requests")
                                        gt.append({
                                        "type": "List",
                                        "level": "third level",
                                        "title": "Following are Approved training requests. You may get details by clicking on link. Please enter Serial number to get details",
                                        "number": each_training,
                                        "links":
                                        [
                                            {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],
                                                                               data[each_training]["traineeFirstName"],data[each_training]["traineeLastName"]),
                                                "link_href": "{}".format(each_training+1),
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
                            if gt:
                                print(gt)
                                print(training_request)
                                dispatcher.utter_custom_json(gt)
                            else:
                                Training_request_list_form_slot = []
                                dispacther.utter_message("Approved Trainings are not available of given duration")

                        elif data["errorDesc"]:
                            print("Inside elif of show aprroved training")
                            Training_request_list_form_slot = []
                            dispatcher.utter_message("There is no approved training request available!")
                            # dispatcher.utter_message(data["errorDesc"])
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                        else:
                            print("Inside else of show Approved training")
                            Training_request_list_form_slot = []
                            print("response for completed training", response)
                            dispatcher.utter_message("Sorry! in")
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                    except:

                        print("Inside except of show Approved training")
                        Training_request_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("There is no approved training request available!")
                        # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                        return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]

                elif tracker.get_slot('trainees_for_request') is not None:
                    response = requests.get("{}/TrainingRequestofParticularEmployee?Training_request_name=Approved&User_Employee_Code={}&Trainee_Employee_code={}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("trainees_for_request")))
                

                    data = response.json()
                    print(len(data))
                    len1 = (len(data))
                    try:
                        print(EMP_name+" "+EMP_last_name)
                        print("{} {}".format(data[0]["trainerFirstName"],data[0]["trainerLastName"]))
                        if EMP_name+" "+EMP_last_name  == "{} {}".format(data[0]["trainerFirstName"],
                                                                                    data[0]["trainerLastName"]):
                            print("user_request is trainer")
                            user_request = "trainer"

                    except:
                        pass
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            training_request = {}
                            gt = []
                            for each_training in range(0, len(data)):
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                    serial_num = len(training_request)
                                    print(serial_num,"serial_num")
                                    training_request.update({serial_num + 1: {"training_id":data[each_training]["tr_id"],
                                                                 "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Approved"}})
                                    print("training requests updated")
                                    gt.append({
                                    "type": "List",
                                    "level": "third level",
                                    "title": "Following are Approved training requests. You may get details by clicking on link. Please enter Serial number to get details",
                                    "number": each_training,
                                    "links":
                                        [
                                            {
                                            "display_text": "more",
                                            "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],
                                                                                
                                                                                  data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                            "link_href": "{}".format(each_training+1),
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
                            print(training_request)
                            dispatcher.utter_custom_json(gt)
                            

                        elif data["errorDesc"]:
                            Training_request_list_form_slot = []
                            dispatcher.utter_message("There is no approved training request available for this trainee!")
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                        else:
                            Training_request_list_form_slot = []
                            print("response for APPROVED training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                    except:
                        Training_request_list_form_slot = []
                        print("response for approved training", response)
                        dispatcher.utter_message("There is no approved training request available for this trainee!")
                        # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                        return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
            
            elif tracker.get_slot('specific_training') == "Period Specific":
                if s_date_training and e_date_training:
                    print("all approved training")
                    response = requests.get("{}/TrainingRequestofAll?Training_request_name=Approved&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    len1 = (len(data))
                    print(EMP_name+" "+EMP_last_name)
                    print("{} {}".format(data[0]["trainerFirstName"],data[0]["trainerLastName"]))
                
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))
                            print('data[each_training]["tr_id"]',data[0]["tr_id"])

                            training_request = {}
                            gt = []

                            for each_training in range(0, len(data)):
                                
                                print("Inside for loop")
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                    serial_number = len(training_request) + 1
                                    training_request.update({serial_number: {"training_id":data[each_training]["tr_id"],
                                                                "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Approved"}})
                                    print("After training requests")
                                    gt.append({
                                    "type": "List",
                                    "level": "third level",
                                    "title": "Following are Approved training requests. You may get details by clicking on link. Please enter Serial number to get details",
                                    "number": each_training,
                                    "links":
                                    [
                                        {
                                            "display_text": "more",
                                            "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],
                                                                           data[each_training]["traineeFirstName"],data[each_training]["traineeLastName"]),
                                            "link_href": "{}".format(serial_number),
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
                            print(training_request)
                            dispatcher.utter_custom_json(gt)

                        elif data["errorDesc"]:
                            print("Inside elif of show aprroved training")
                            Training_request_list_form_slot = []
                            dispatcher.utter_message("There is no approved training request available!")
                            # dispatcher.utter_message(data["errorDesc"])
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                        else:
                            print("Inside else of show Approved training")
                            Training_request_list_form_slot = []
                            print("response for completed training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SSlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),lotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                    except:

                        print("Inside except of show Approved training")
                        Training_request_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("I am sorry! There is no approved training request available.")
                        # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                        return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]

            elif tracker.get_slot("specific_training") == "Competency Specific":
                
                if s_date_training and e_date_training:
                    print("all approved training Competency Specific")
                    response = requests.get("{}/TrainingRequestofAll?Training_request_name=Approved&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    len1 = (len(data))
                    print(EMP_name+" "+EMP_last_name)
                    print("{} {}".format(data[0]["trainerFirstName"],data[0]["trainerLastName"]))
                
                    try:
                        if response.status_code is 200:
                            data = response.json()
                            print(len(data))
                            len1 = (len(data))
                            print('data[each_training]["tr_id"]',data[0]["tr_id"])

                            training_request = {}
                            gt = []

                            for each_training in range(0, len(data)):
                                print("Inside for loop")
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                print("Competency group",tracker.get_slot("compentency_group"))
                                c_grp = tracker.get_slot("compentency_group")
                                global Compentency_group_dict
                                tr_code = Compentency_group_dict[c_grp][1]
                                print(tr_code,"tr_code")
                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                    if (data[each_training]["tr_code"]).find(tr_code) != -1:
                                        serial_number = len(training_request) + 1
                                        training_request.update({serial_number: {"training_id":data[each_training]["tr_id"],
                                                                "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Approved"}})
                                        print("After training requests")
                                        gt.append({
                                            "type": "List",
                                        "level": "third level",
                                        "title": "Following are Approved training requests of Competency group {}. You may get details by clicking on link. Please enter Serial number to get details".format(c_grp),
                                        "number": each_training,
                                        "links":
                                        [
                                            {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],
                                                                           data[each_training]["traineeFirstName"],data[each_training]["traineeLastName"]),
                                                "link_href": "{}".format(serial_number),
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
                            if gt:
                                print("gt",gt)
                                dispatcher.utter_custom_json(gt)
                            else:
                                dispatcher.utter_message("I am sorry! There is no Approved training available of given competancy.")
                                Training_list_form_slot = []
                                print("Training ",training)
                            return []

                        elif data["errorDesc"]:
                            print("Inside elif of show aprroved training")
                            Training_request_list_form_slot = []
                            dispatcher.utter_message("I am sorry! There is no approved training request available.")
                            # dispatcher.utter_message(data["errorDesc"])
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                        else:
                            print("Inside else of show Approved training")
                            Training_request_list_form_slot = []
                            print("response for completed training", response)
                            dispatcher.utter_message("Sorry! Something went wrong")
                            # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                            return [SSlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),lotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


                    except:

                        print("Inside except of show Approved training")
                        Training_request_list_form_slot = []
                        print("response for completed training", response)
                        dispatcher.utter_message("I am sorry! There is no approved training request available.")
                        # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                        return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]

            elif tracker.get_slot("specific_training") == "All":

                try:
                    print("Inside 2nd try")
                    s_date_training = ((cal.nlp("last month"))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp("today"))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                except:

                    print("Inside 2nd except")
                    s_date_training = ((cal.nlp(value[0]))[0][0]).strftime("%d/%m/%Y")
                    e_date_training = ((cal.nlp(value[1]))[0][0]).strftime("%d/%m/%Y")
                    print(s_date_training)
                    print(e_date_training)

                
                print("all Approved training all Specific")
                response = requests.get("{}/TrainingRequestofAll?Training_request_name=Approved&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                data = response.json()
                # print(data)
                print(len(data))
                len1 = (len(data))
                try:
                    if response.status_code is 200:
                        data = response.json()
                        print(len(data))
                        len1 = (len(data))

                        training = {}
                        gt = []

                        for each_training in range(0, len(data)):
                                print("Inside for loop")
                                print(s_date_training,"s_date_training")
                                tr_sdate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                tr_edate = dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")
                                print(dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),'dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y")')
                                print(e_date_training,'e_date_training')
                                
                                if s_date_training >= tr_sdate <= e_date_training or s_date_training >= tr_edate <= e_date_training or s_date_training <= tr_sdate >= e_date_training or s_date_training >= tr_edate <= e_date_training:
                                    serial_number = len(training_request) + 1
                                    training_request.update({serial_number: {"training_id":data[each_training]["tr_id"],
                                                                "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Approved"}})
                                    print("After training requests")
                                    gt.append({
                                            "type": "List",
                                        "level": "third level",
                                        "title": "Following are Approved training requests of Competency group {}. You may get details by clicking on link. Please enter Serial number to get details".format(c_grp),
                                        "number": each_training,
                                        "links":
                                        [
                                            {
                                                "display_text": "more",
                                                "more_link": "{} {} training to {} {}".format(data[each_training]["tr_code"],data[each_training]["subject"],
                                                                           data[each_training]["traineeFirstName"],data[each_training]["traineeLastName"]),
                                                "link_href": "{}".format(serial_number),
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
                        if gt:
                            print("gt",gt)
                            dispatcher.utter_custom_json(gt)
                        else:
                            dispatcher.utter_message("I am sorry! There is no Approved training available in given duration.")
                            Training_list_form_slot = []
                            print("Training ",training)
                        return []
                    elif data["errorDesc"]:
                        print("Inside elif of show Approved training")
                        Training_list_form_slot = []
                        dispatcher.utter_message("I am sorry! There is no Approved training available")
                        # dispatcher.utter_message(data["errorDesc"])
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)                            
                        # return [SlotSet("trainees", None), SlotSet("number_of_trainee", None),SlotSet("ordinal1", None),SlotSet("ordinal2", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

                    else:
                        print("Inside else of show Approved training")
                        Training_list_form_slot = []
                        print("response for Approved training", response)
                        dispatcher.utter_message("Sorry! Something went wrong")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("trainees", None), SlotSet("number_of_trainee", None),SlotSet("ordinal1", None),SlotSet("ordinal2", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

                except:
                        print("Inside except of show Approved training")
                        Training_list_form_slot = []
                        print("response for Approved training", response)
                        dispatcher.utter_message("I am sorry! There is no Approved training available..")
                        # dispatcher.utter_template("utter_continue_Training_management",tracker)
                        return [SlotSet("trainees", None), SlotSet("number_of_trainee", None),SlotSet("ordinal1", None),SlotSet("ordinal2", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]
        
        except:
            Training_request_list_form_slot = []
            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


class ActionShowPendingTrainingrequests(Action):

    def name(self):
        return "action_show_pending_training_request"

    def run(self, dispatcher, tracker, domain):

        global Training_request_list_form_slot
        global training_request
        global user_request,EMP_name,EMP_last_name
        training_request = {}
        gt = []

        print("all pending trainings")
        print("tracker.get_slot('number_of_trainee_for_request')",tracker.get_slot('number_of_trainee_for_request'))
        print("tracker.get_slot('trainees')",tracker.get_slot('trainees'))

        try:
            if tracker.get_slot('number_of_trainee_for_request') == "all":
                print("all trainings")
                response = requests.get("{}/TrainingRequestofAll?Training_request_name=Pending&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                data = response.json()
                try:
                
                    print(EMP_name)
                    print(EMP_last_name)
                    print("{} {}".format(data[0]["trainerFirstName"],data[0]["trainerLastName"]))
                    if EMP_name+" "+EMP_last_name  == "{} {}".format(data[0]["trainerFirstName"],
                                                                                data[0]["trainerLastName"]):
                        print("user is trainer")
                        user_request = "trainer"
                    else:
                        pass
                except:
                    pass
               
                try:
                    if response.status_code is 200:
                        data = response.json()
                        print(len(data))
                        len1 = (len(data))

                        training_request = {}
                       
                        for each_training in range(0,len(data)):
                            try:
                                serial_number = len(training_request) + 1
                                training_request.update({serial_number + 1: {"training_id":data[each_training]["tr_id"],
                                                                 "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":dt.datetime.strptime(data[each_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
																 "status":"Pending"}})
                                print("training reuest updated1 pending")
                                
                            except:
                                serial_number = len(training_request) + 1
                                training_request.update({serial_number: {"training_id":data[each_training]["tr_id"],
                                                                 "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
																 "status":"Pending"}})
                                print("training reuest updated2 for pending")

                        # for i in range(0,len(training_request)):
                        #     gt.append({
                        #         "type": "List",
                        #         "level": "third level",
                        #         "title": "Following is completed training list. You may download it for better view by clicking on link. Please enter Serial number to get details",
                        #         "number": i,
                        #         "links":
                        #             [
                        #                 {
                        #                     "display_text": "more",
                        #                     "more_link": "{} to {} {} {}".format(training_request[i+1][1],training_request[i+1][2],training_request[i+1][8]),
                        #                     "download": "{}/DownloadTrainingSheet?Training_Id={}".format(mindsconnect_url,training_request[i+1][0]),
                        #                     "button":
                        #                         [
                        #                             {
                        #                                 "title": "Approve",
                        #                                 "payload": "approve"

                        #                             },
                        #                             {

                        #                                 "title": "Reject",
                        #                                 "payload": "reject"

                        #                             }
                        #                         ]

                        #                 }
                        #             ]
                        #     }
                        #     )
                        print(gt)
                        print(training_request)
                        # dispatcher.utter_custom_json(gt)

                    # elif data["errorDesc"]:

                    #     Training_request_list_form_slot = []
                    #     dispatcher.utter_message(data["errorDesc"])
                    #     dispatcher.utter_template("utter_continue_Training_requests",tracker)
                    #     return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]

                    # else:
                    #     Training_request_list_form_slot = []
                    #     print("response for ongoing training", response)
                    #     dispatcher.utter_message("Sorry! Something went wrong")
                    #     dispatcher.utter_template("utter_continue_Training_requests",tracker)
                    #     return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]
                except:
                    pass
                    
                    print(data["errorDesc"])
                    print("No pending for approval training requests")
                    # Training_request_list_form_slot = []
                    print("response for ongoing training", response)
                    # dispatcher.utter_message(data["errorDesc"])
                    # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                    # return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]
                try:
                    response_pending_for_approval = requests.get("{}/TrainingRequestofAll?Training_request_name=Pending for Approval&User_Employee_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))
                    data_pending_for_approval = response_pending_for_approval.json()
                    print(len(data_pending_for_approval))
                    len1 = (len(data_pending_for_approval))
                    print("length of data pending for approval",len(data_pending_for_approval))
                    
                    for each_training in range(0,len(data_pending_for_approval)):									
                        try:
                            if data_pending_for_approval["errorCode"]:
                                print(data_pending_for_approval["errorDesc"])
                                print("No pending for approval training requests")
                                    
                        except:
                            try:
                
                                print(EMP_name)
                                print(EMP_last_name)
                                print("{} {}".format(data_pending_for_approval[0]["trainerFirstName"],data_pending_for_approval[0]["trainerLastName"]))
                                if EMP_name+" "+EMP_last_name  == "{} {}".format(data_pending_for_approval[0]["trainerFirstName"],
                                                                                data_pending_for_approval[0]["trainerLastName"]):
                                    print("user is trainer")
                                    user_request = "trainer"
                                else:
                                    pass
                            except:
                                pass
                            print(len(training_request),"len(training_request)")
                            print("Inside except pending for approval")
                            serial_number = len(training_request) + 1
                            training_request.update({serial_number: {"training_id":data_pending_for_approval[each_training]["tr_id"],
                                                                "training_code":data_pending_for_approval[each_training]["tr_code"],
                                                                "training_subject":data_pending_for_approval[each_training]["subject"],
                                                                 "trainee_name":"{} {} Pending for Approval".format(data_pending_for_approval[each_training]["traineeFirstName"],
                                                                                data_pending_for_approval[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data_pending_for_approval[each_training]["trainerFirstName"],
                                                                                data_pending_for_approval[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":data_pending_for_approval[each_training]["plStartDateStrFormate"],
                                                                 "training_planned_end_date":data_pending_for_approval[each_training]["plEndDateStrFormate"],
																 "status":"Pending for Approval"}})
                            print("training reuest updated pending for approval")

                except:
                    pass

       
            elif tracker.get_slot('trainees_for_request'):
                print("all pending trainings for trainee")
                response = requests.get("{}/TrainingRequestofParticularEmployee?Training_request_name=Pending&User_Employee_Code={}&Trainee_Employee_code={}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("trainees_for_request")))
                data = response.json()
                print(len(data))
                len1 = (len(data))
                training_request = {}
                gt = []
                try:
                    print(EMP_name+" "+EMP_last_name)
                    print("{} {}".format(data[0]["trainerFirstName"],data[0]["trainerLastName"]))
                    if EMP_name+" "+EMP_last_name  == "{} {}".format(data[0]["trainerFirstName"],
                                                                                data[0]["trainerLastName"]):
                        print('user_request = "trainer"')
                        user_request = "trainer"
                except:
                    pass
                try:
                    if response.status_code is 200:
                        data = response.json()
                        print("length of data of pending for a trainee",len(data))
                        
                        
                        for each_training in range(0, len(data)):
                            
                            try:
                                serial_number = len(training_request) + 1
                                training_request.update({serial_number: {"training_id":data[each_training]["tr_id"],
                                                               "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":dt.datetime.strptime(data[each_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                 "training_planned_end_date":data[each_training]["plEndDateStrFormate"],
																 "status":"Pending"}})
                                print("training reuest updated pending")
                            except:
                                serial_number = len(training_request) + 1
                                training_request.update({serial_number: {"training_id":data[each_training]["tr_id"],
                                                                 "training_code":data[each_training]["tr_code"],
                                                                 "training_subject":data[each_training]["subject"],
                                                                 "trainee_name":"{} {}".format(data[each_training]["traineeFirstName"],
                                                                                data[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data[each_training]["trainerFirstName"],
                                                                                data[each_training]["trainerLastName"]),
																 "status":"Pending"}})
                                print("training reuest updated2 for pending")
                    
                    # elif data["errorDesc"]:
                    #     Training_request_list_form_slot = []
                    #     dispatcher.utter_message(data["errorDesc"])
                    #     dispatcher.utter_template("utter_continue_Training_requests",tracker)
                    #     return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]
                    # else:
                    #     Training_request_list_form_slot = []
                    #     print("response for ongoing training", response)
                    #     dispatcher.utter_message("Sorry! Something went wrong")
                    #     dispatcher.utter_template("utter_continue_Training_requests",tracker)
                    #     return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]
                except:
                    print("no trainings")
                    pass
                    # Training_request_list_form_slot = []
                    print("response for ongoing training", response)
                    # dispatcher.utter_message(data["errorDesc"])
                    # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                    # return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]
                print("all pending trainings for trainee")
                try:
                    response_pending_for_approval = requests.get("{}/TrainingRequestofParticularEmployee?Training_request_name=Pending for Approval&User_Employee_Code={}&Trainee_Employee_code={}".format(mindsconnect_url,tracker.get_slot("emp_code"),tracker.get_slot("trainees_for_request")))
                    data_pending_for_approval = response_pending_for_approval.json()
                    print("length of data for pending approval",len(data_pending_for_approval))
                    len2 = (len(data_pending_for_approval))
                    for each_training in range(0,len(data_pending_for_approval)):									
                        try:
                            if data_pending_for_approval["errorCode"]:
                                print(data_pending_for_approval["errorDesc"])
                                print("No pending for approval training requests")
                        except:
                            try:
                
                                print(EMP_name)
                                print(EMP_last_name)
                                print("{} {}".format(data_pending_for_approval[0]["trainerFirstName"],data_pending_for_approval[0]["trainerLastName"]))
                                if EMP_name+" "+EMP_last_name  == "{} {}".format(data_pending_for_approval[0]["trainerFirstName"],
                                                                                data_pending_for_approval[0]["trainerLastName"]):
                                    print("user is trainer")
                                    user_request = "trainer"
                                else:
                                    pass
                            except:
                                pass
                            print(len(training_request),"len(training_request)")
                            print("Inside exceptpending for approval")
                            serial_number = len(training_request) + 1
                            training_request.update({serial_number: {"training_id":data_pending_for_approval[each_training]["tr_id"],
                                                            "training_code":data_pending_for_approval[each_training]["tr_code"],
                                                                 "training_subject":data_pending_for_approval[each_training]["subject"],
                                                                 "trainee_name":"{} {} Pending for Approval".format(data_pending_for_approval[each_training]["traineeFirstName"],
                                                                                data_pending_for_approval[each_training]["traineeLastName"]),
                                                                  "trainer_name":"{} {}".format(data_pending_for_approval[each_training]["trainerFirstName"],
                                                                                data_pending_for_approval[each_training]["trainerLastName"]),
                                                                 "training_planned_start_date":data_pending_for_approval[each_training]["plStartDateStrFormate"],
                                                                 "training_planned_end_date":data_pending_for_approval[each_training]["plEndDateStrFormate"],
																 "status":"Pending for Approval"}})
                    print("training reuest updated pending for approval")
                    print(tracker.get_slot("ordinal1","trackerget_slot('ordinal1')"))
                    return []
                except:
                    pass

            if len(training_request) is not 0:
                print("Show pending training requests")
                print(training_request[1])
                gt = []
                for i in range(0,len(training_request)):
                    print("inside for loop")
                    gt.append({
                                "type": "List",
                                "level": "third level",
                                "title": "Following are pending training requests. You may get details by clicking on link. Please enter Serial number to get details",
                                "number": i,
                                "links":
                                    [
                                        {
                                            "display_text": "more",
                                            "more_link": "{} {} to {}".format(training_request[i+1]["training_code"],training_request[i+1]["training_subject"],training_request[i+1]["trainee_name"]),
                                               
                                               
                                            "link_href": "{}".format(i+1),
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
                print(training_request)
                dispatcher.utter_custom_json(gt)

            else:
                print("No one pending training requests")
                Training_request_list_form_slot = []
                print("response for pending training", response)
                dispatcher.utter_message("There is no pending training request")
                # dispatcher.utter_template("utter_continue_Training_requests",tracker)
                return [SlotSet("trainees_for_request", None), SlotSet("number_of_trainee_for_request", None)]


        except:
            Training_request_list_form_slot = []
            # return [SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]


class SubTrainingRequestDetailForm(FormValidationAction):

    def name(self):
        return "validate_Sub_Training_request_Detail_form"

    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot")
        global Training_request_list_form_slot
        global sub_training_request_detail_slot,user_request
       
        print("len(Training_list_form_slot)",len(Training_request_list_form_slot))
        if len(Training_request_list_form_slot) < 1:
            if user_request == "trainee":
                sub_training_request_detail_slot = ["ordinal1"]
                return sub_training_request_detail_slot
            elif user_request == "trainer":
                sub_training_request_detail_slot = ["ordinal1"]
                return sub_training_request_detail_slot
            else:
                sub_training_request_detail_slot = []
                return sub_training_request_detail_slot
        else:
            sub_training_request_detail_slot = ["ordinal1"]
            return sub_training_request_detail_slot


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping")
        return {

            "ordinal1":
                [
                    # self.from_entity(entity="ordinal"),
                    self.from_entity(entity="ordinal1"),
                    self.from_text()
            
                ]
            }
    
    def validate_ordinal1(self, value: Text, 
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_ordinal1_attempt
        global sub_training_request_detail_slot
        global training_request,allowed_request
        global sub_trainings_request,user_request

        sub_trainings_request = {}
        gt = []
        try:
            print("validate ordinal1 inside if value",value)
            ser_no = value
            print(ser_no,"ser_no")
        except:
            print("Validate ordinal1 inside except value",value[1])
            ser_no = value[1]

        try:
            print("inside try")
            print(training_request.keys(),"training.keys()")
            if int(ser_no) in training_request.keys():
                sr_no = int(ser_no)
                print("inside if validate")
                training_id = training_request[sr_no]["training_id"]
                trainer_name = training_request[sr_no]["trainer_name"]
                print("user",user_request)
                print("Status of main training reuest",training_request[sr_no]["status"])
                print(training_id)
                response = requests.get("{}/TrainingRequestDetails?Training_id={}".format(mindsconnect_url,training_id))
                data = response.json()
                print(len(data))
                len1 = (len(data))
                gt = []
                print(data[0]["tr_lines_id"],"data[0]['tr_lines_id']")
                try:
                    if EMP_name+" "+EMP_last_name  == "{}".format(data[0]["trainerName"]):
                        print("user is trainer")
                        user_request = "trainer"
                except:

                    pass

                sub_trainings_request = {}

                for sub_training in range(0,len1):

                    if allowed_request == "Approved_list":
                        sub_trainings_request.update({"{}".format(sub_training+1):{"sub_training id":data[sub_training]["tr_lines_id"],"trainerName":data[sub_training]["trainerName"],
                                                          "trainerEmpCode":data[sub_training]["trainerEmpCode"],
                                                          "traineeName":data[sub_training]["traineeName"],
                                                          "traineeEmpCode":data[sub_training]["traineeEmpCode"],
                                                          "Compentency":data[sub_training]["compentenice"],
                                                         "CompGroupName":data[sub_training]["compGroupName"],

                                                        
                                                        # "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                                                         "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                    "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                                      "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                                      "sub_training_trainee_status":data[sub_training]["status"]}})
						
                    elif allowed_request == "Pending_list":
                        print(data[sub_training]["status"],"data[sub_training]['status']")
                        try:
                            print("try")
                            # if data[sub_training]["status"] == "Pending":
                            #     print("completed")
                            #     sub_trainings_request.update({"{}".format(sub_training+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                        
                            #                             # "assigned_name":"{} {}".format(data[sub_training]["assigned_to_emp"]["emp_first_name"],data[sub_training]["assigned_to_emp"]["emp_last_name"]),
                            #                              "nameofTopics":data[sub_training]["nameOfTopics"],
                            #                              "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                            #                                           "sub_training_planned_end_date":data[sub_training]["plEndDate"],
                            #                                           "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                            #                                           "sub_training_trainee_status":data[sub_training]["status"]}})
                                
                            if data[sub_training]["trainerStatus"] == "Pending":
                                try:
                                    print("Inside pending")
                                    sub_trainings_request.update({"{}".format(sub_training+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                        
                                                        "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "Compentency":data[sub_training]["compentenice"],
                                                         "CompGroupName":data[sub_training]["compGroupName"],
                                                         "trainerName":data[sub_training]["trainerName"],
                                                          "trainerEmpCode":data[sub_training]["trainerEmpCode"],
                                                          "traineeName":data[sub_training]["traineeName"],
                                                          "traineeEmpCode":data[sub_training]["traineeEmpCode"],
                                                         "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                        "sub_training_trainee_status":data[sub_training]["status"]}})
                                    print("after pending updated")
                                except:
                                    print("pending except")
                                    sub_trainings_request.update({"{}".format(sub_training+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                        
                                                        "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "Compentency":data[sub_training]["compentenice"],
                                                         "CompGroupName":data[sub_training]["compGroupName"],
                                                         "trainerName":data[sub_training]["trainerName"],
                                                          "trainerEmpCode":data[sub_training]["trainerEmpCode"],
                                                          "traineeName":data[sub_training]["traineeName"],
                                                          "traineeEmpCode":data[sub_training]["traineeEmpCode"],
                                                        #  "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        # "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                        "sub_training_trainee_status":data[sub_training]["status"]}})
                                    
                                    print("after pending except updated")
                            elif data[sub_training]["status"] == "Approved":
                                print("Approved elif")
                                sub_trainings_request.update({"{}".format(sub_training+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                        
                                                        "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "Compentency":data[sub_training]["compentenice"],
                                                         "CompGroupName":data[sub_training]["compGroupName"],
                                                         "trainerName":data[sub_training]["trainerName"],
                                                         "trainerEmpCode":data[sub_training]["trainerEmpCode"],
                                                          "traineeName":data[sub_training]["traineeName"],
                                                          "traineeEmpCode":data[sub_training]["traineeEmpCode"],
                                                         "sub_training_planned_start_date":dt.datetime.strptime(data[sub_training]["plStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        # "sub_training_actual_start_date":dt.datetime.strptime(data[sub_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                        "sub_training_trainee_status":data[sub_training]["status"]}})
                                    
                               

                            else: 
                                print("inside else")
                                sub_trainings_request.update({"{}".format(sub_training+1):{"sub_training id":data[sub_training]["tr_lines_id"],
                                                        
                                                         "nameofTopics":data[sub_training]["nameOfTopics"],
                                                         "Compentency":data[sub_training]["compentenice"],
                                                         "CompGroupName":data[sub_training]["compGroupName"],
                                                         "trainerName":data[sub_training]["trainerName"],
                                                         "trainerEmpCode":data[sub_training]["trainerEmpCode"],
                                                          "traineeName":data[sub_training]["traineeName"],
                                                          "traineeEmpCode":data[sub_training]["traineeEmpCode"],
                                                         "sub_training_planned_start_date":data[sub_training]["plStartDateStrFormate"],
                                                        "sub_training_planned_end_date":dt.datetime.strptime(data[sub_training]["plEndDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        # "sub_training_actual_start_date":dt.datetime.strptime(data[sub_training]["acStartDateStrFormate"],"%d-%m-%Y").strftime("%d/%m/%Y"),
                                                        "sub_training_trainer_status":data[sub_training]["trainerStatus"],
                                                        "sub_training_trainee_status":data[sub_training]["status"]}})

                                
                        except:
                            print("no training")
                    
                if len(sub_trainings_request) is not 0:
                    global display_pending_for_approval
                    display_pending_for_approval = []
                    print("len(sub_trainings_request) is not 0:")
                    print(len(sub_trainings_request),'len(sub_trainings_request)')
                    

                    for i in range(0,len(sub_trainings_request)):
                        try:
                            try:
                                print(sub_trainings_request[str(i+1)]["nameofTopics"])
                            except:
                                print(sub_trainings_request[str(i+1)]["nameofTopics"])
                            print("inside try")
                            
                            print(training_request[sr_no]["status"])
                            if user_request == "admin" and training_request[sr_no]["status"] == "Pending for Approval":
                                display_pending_for_approval.append("<b>{} </b> {} From {} to {} - {}<br>".format(
                                sub_trainings_request[str(i+1)]["nameofTopics"],
                               
                                sub_trainings_request[str(i+1)]["CompGroupName"],
                                sub_trainings_request[str(i+1)]["Compentency"],
                                sub_trainings_request[str(i+1)]["sub_training_planned_start_date"],
                                # "not given",
                                sub_trainings_request[str(i+1)]["sub_training_planned_end_date"],
                                sub_trainings_request[str(i+1)]["sub_training_trainee_status"]))

                                gt.append({
                                "type": "List",
                                "level": "third level",
                                "title": "Following are competencies planned by training co-ordinator {} with planned start date and planned end date".format(sub_trainings_request[str(i+1)]["trainerName"]),
                                "number": i,
                                "links":
                                    [
                                    {
                                        "display_text": "more",
                                        "more_link":
                                        "<b>{}</b> {} From {} to {}".format(
                                        
                                        #  sub_trainings_request[str(i+1)]["Compentency"],
                                        # sub_trainings_request[str(i+1)]["CompGroupName"],
                                        sub_trainings_request[str(i+1)]["Compentency"],
                                        sub_trainings_request[str(i+1)]["nameofTopics"],
                                        sub_trainings_request[str(i+1)]["sub_training_planned_start_date"],
                                        # "not given",
                                        sub_trainings_request[str(i+1)]["sub_training_planned_end_date"],
                                        ),

                                    "link_href":str(i+1),
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
                                 })

                            else:
                                print("sub training inside else")

                                gt.append({
                                "type": "List",
                                "level": "third level",
                                "title": "Following are competencies planned by training co-ordinator {} with planned start date and planned end date".format(sub_trainings_request[str(i+1)]["trainerName"]),
                                "number": i,
                                "links":
                                    [
                                    {
                                        "display_text": "more",
                                       "more_link":
                                        "<b>{}</b> {} From {} to {}".format(
                                        #  sub_trainings_request[str(i+1)]["Compentency"],
                                        # sub_trainings_request[str(i+1)]["CompGroupName"],
                                         sub_trainings_request[str(i+1)]["Compentency"],
                                        sub_trainings_request[str(i+1)]["nameofTopics"],
                                        sub_trainings_request[str(i+1)]["sub_training_planned_start_date"],
                                        # "not given",
                                        sub_trainings_request[str(i+1)]["sub_training_planned_end_date"],
                                        ),
                                    "link_href":str(i+1),
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
                                 })
                        except:
                            gt.append({
                            "type": "List",
                            "level": "third level",
                            "title": "Following are competencies planned by training co-ordinator {}".format(trainer_name),
                            "number": i,
                            "links":
                                [
                                {
                                    "display_text": "more",
                                    "more_link":
                                        "<b>{} </b> {} ".format(
                                        sub_trainings_request[str(i+1)]["nameofTopics"],
                                        #  sub_trainings_request[str(i+1)]["Compentency"],
                                        # sub_trainings_request[str(i+1)]["CompGroupName"],
                                        sub_trainings_request[str(i+1)]["Compentency"],
                                        sub_trainings_request[str(i+1)]["nameofTopics"]),
                                        # sub_trainings_request[str(i+1)]["sub_training_planned_start_date"],
                                        # "not given",
                                        # sub_trainings_request[str(i+1)]["sub_training_planned_end_date"],
                                        # sub_trainings_request[str(i+1)]["sub_training_trainee_status"]),
                                    "link_href":str(i+1),
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
                                })

                    print(gt)
                    dispatcher.utter_custom_json(gt)
                wrong_ordinal1_attempt = 0
                return {"ordinal1":ser_no}

            elif wrong_ordinal1_attempt < 3:

                print("wrong_ordinal1_attempt", wrong_ordinal1_attempt)
                wrong_ordinal1_attempt = wrong_ordinal1_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"ordinal1": None}

            else:
                sub_training_request_detail_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt1")
                wrong_ordinal1_attempt = 0
                return self.deactivate()
        except:
            if wrong_ordinal1_attempt < 3:
                print("wrong_ordinal1_attempt", wrong_ordinal1_attempt)
                wrong_ordinal1_attempt = wrong_ordinal1_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training detail with me")
                return {"ordinal1": None}

            else:
                sub_training_request_detail_slot = []
                wrong_ordinal1_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt2")
                return self.deactivate()
            
class ActionSubTrainingRequestDetailForm(Action):
    
    def name(self):
        return "action_Sub_Training_request_Detail_form_submit"

    def run(self, dispatcher, tracker, domain):
        global sub_training_detail_slot,allowed_request,visit_request,training_request,user_request
        
        if len(sub_training_request_detail_slot) < 1:
            if allowed_request == "No":
                dispatcher.utter_message("I am sorry! There is no training request available.")
            print("Inside if of form")
            dispatcher.utter_template("utter_continue_Training_requests",tracker)
            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
            

        else:
            if (user_request == "trainee" and allowed_request != "Pending_list") or (user_request == "trainer" and allowed_request != "Pending_list"):
                buttons = []
                buttons.append({"title": "Yes",
                        "payload": "Yes"})
                buttons.append({"title": "No",
                        "payload": "No"})
                dispatcher.utter_button_message("Do you want to update status of this training plan?", buttons)
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None)]
            
            elif user_request == "admin" and training_request[int(tracker.get_slot("ordinal1"))]["status"] == "Pending for Approval":
                buttons = []
                buttons.append({"title": "Yes",
                        "payload": "Yes"})
                buttons.append({"title": "No",
                        "payload": "No"})
                dispatcher.utter_button_message("Do you want approve/reject training plan of training request?", buttons)
                return [SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None)]
            
            else:
                # buttons = []
                # buttons.append({"title": "Yes",
                #         "payload": "Yes"})
                # buttons.append({"title": "No",
                #         "payload": "No"})
                # dispatcher.utter_button_message("Do you want to get details of training plan of training request?", buttons)
                dispatcher.utter_template("utter_continue_Training_requests",tracker)
                # return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("ordinal1",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None)]
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None) ]
            

#---------------------------------------------------------------------------Update status by trainer------------------------------------------------------------------------------


class ActionContinueWithSubTrainingUpdate(Action):

    def name(self):
        return "action_continue_with_sub_training_update"

    def run(self, dispatcher, tracker, domain):
        current_intent = tracker.latest_message['intent'].get('name')
        print(current_intent)
        global allowed_request,user_request,update_status_of_training_form_slot,training_request
        if current_intent == "affirm":
            current_intent = "None"
            try:

                if (user_request == "trainee" and allowed_request == "Approved_list"):
                    if len(sub_training_request_detail_slot) < 1:
                        update_status_of_training_form_slot = []
                    
                    elif (user_request == "trainee" and allowed_request == "Approved_list"):
                        update_status_of_training_form_slot = ["ordinal3"]
                    
                    else:
                        update_status_of_training_form_slot = ["ordinal3"]
                    return [FollowupAction("update_status_of_training_form")]
                elif (user_request == "trainer" and allowed_request == "Approved_list"):
                    if len(sub_training_request_detail_slot) < 1:
                        update_status_of_training_form_slot = []
                    
                    elif (user_request == "trainer" and allowed_request == "Approved_list"):
                        update_status_of_training_form_slot = ["ordinal3"]

                    else:
                        update_status_of_training_form_slot = ["ordinal3"]
                    return [FollowupAction("update_status_of_training_form")]
                elif user_request == "admin" and training_request[int(tracker.get_slot("ordinal1"))]["status"] == "Pending for Approval":
                    buttons = []

                    buttons.append({"title": "Approve",
                                    "payload": "approve"})
                    buttons.append({"title": "Reject",
                                    "payload": "reject"})
                    # pending_for_approval = "<b>Following trainings are pending for approval</b>"
                    pending_for_approval = "<b>Could you please let me know your decision?</b>"
                    global display_pending_for_approval
                    for i in range(0,len(display_pending_for_approval)):
                        pending_for_approval = pending_for_approval + '<br>'+display_pending_for_approval[i]
                    dispatcher.utter_button_message(pending_for_approval,buttons)
                                  
                    update_status_of_training_form_slot = ["command"]
                    return [FollowupAction("update_status_of_training_form")]
                else: 

                    return [FollowupAction("action_check_logged_for_training_request")]
            except:

                return [FollowupAction("action_show_pending_training_request")]

        elif current_intent == "deny":
            current_intent = "None"
            print("Inside deny to requests")
            dispatcher.utter_message(template="utter_continue_Training_requests")
            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

        else:
            current_intent = "None"
            dispatcher.utter_message(template="utter_continue_Training_requests")
            return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]


class UpdateStatusofTrainingForm(FormValidationAction):

    def name(self):
        return "validate_update_status_of_training_form"


    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot")
        global Training_request_list_form_slot
        global sub_training_request_detail_slot
        global update_status_of_training_form_slot,user_request,allowed_request
        return update_status_of_training_form_slot


    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping ordinal2")
        return {
            "command":
            [
                self.from_entity(entity="command"),
                self.from_text(intent="emp_code_i"),
                self.from_text()

            ],
            "ordinal3":
                [
                    # self.from_entity(entity="ordinal"),
                    self.from_text()
                ],
            "training_type_trainee": [
                self.from_entity(entity="training_type_trainee"),
                self.from_text(intent="training_type"),
                self.from_text(intent="update"),
                self.from_text()
            ],
            "training_start_time": [
        
                self.from_text()
            ],
            "training_end_time": [
                
                self.from_text()
            ],
            "status":[
                self.from_entity(entity="training_type_trainee"),
                self.from_text(intent="status"),
                self.from_text(intent="update"),
                self.from_text()
            ],
            "reason":
            [
                self.from_text()
            ],
            "training_type_decision":
            [
                self.from_text()
            ]

            }
    
     
    
    def validate_command(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of command ', value)
        if value in ["approve","Approve" ,"Reject","reject"]:
            if value in ["Reject","reject"]:
                print("inside if validate commmand")
                global update_status_of_training_form_slot
                update_status_of_training_form_slot.append("reason")
            elif value in ["approve","Approve"]:
                sr_no = int(tracker.get_slot("ordinal1"))
                print("sr_no",sr_no)
                print('training_request[sr_no]["training_id"]',training_request[sr_no]["training_id"])
                training_id = training_request[sr_no]["training_id"]
                response = requests.get("{}/ApprovalRejectionofTrainingRequest?Training_id={}&Action=Approve&Comment=Approved&User_Emp_Id={}".format(mindsconnect_url,int(training_id),tracker.get_slot("emp_code")))
                data = response.json()
                print(data)
                print(len(data))

                dispatcher.utter_message(data['errorDesc'])
            return {"command": value}

        else:
            dispatcher.utter_template('utter_wrong_command',tracker)
            return {"command": None}

    
    
    
    def validate_ordinal3(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global update_status_of_training_form_slot
        global sub_trainings_request
        global allowed_request
        print("allowed",allowed_request)

        try:
            print("validate ordinal3 inside if value", value)
            sr_no = value

        except:
            print("validate ordinal3 inside except value", value[1])
            sr_no = value[1]

        try:

            if sr_no in sub_trainings_request.keys():

                print("inside if validate")
                if user_request == "trainee" and allowed_request == "Approved_list":
                # if allowed_request != "Pending_list":
                    if sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Pending":
                        update_status_of_training_form_slot.append("training_type_trainee")
                        
                    elif sub_trainings_request[sr_no]["sub_training_trainee_status"] == "In Progress":
                        # dispatcher.utter_message(text= "Do you want to add training type")
                        update_status_of_training_form_slot.append("training_type_decision")
                        # update_status_of_training_form_slot.append("training_end_time")
                        # dispatcher.utter_message("I am updating training status to Completed")
                    elif sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Completed":
                        dispatcher.utter_message("You have already completed this training.")
                elif user_request == "trainer" and allowed_request == "Approved_list":
                    print("Inside elif")
                    if sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "In Progress" :
                        dispatcher.utter_message("I am updating training status to In Progress")
                        update_status_of_training_form_slot.append("status")
                    elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Pending":
                        dispatcher.utter_message("I am updating training status to In Progress")
                        update_status_of_training_form_slot.append("status")
                    elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Completed":
                        update_status_of_training_form_slot.append("status")
                        update_status_of_training_form_slot.append("training_end_time")
                        dispatcher.utter_message("I am updating training status to Completed")
                    elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "In Progress" :
                        dispatcher.utter_message("I am updating training status to In Progress")
                        update_status_of_training_form_slot.append("status")
                    elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Completed":
                        dispatcher.utter_message("Trainee have already completed this training.")
                    elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Pending" :
                        dispatcher.utter_message("You can not update the status of this training to Completed because the trainee has not yet started training")
                    elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "In Progress":
                        dispatcher.utter_message("You can not update the status of this training to completed because the trainee has not yet completed training")
                    else:
                        dispatcher.utter_message("You can not update the status of this training because the trainee has not yet started training")
                else:
                    dispatcher.utter_message("You can not update the status of this training")

                
                wrong_attempt = 0
                return {"ordinal3": sr_no}

            elif wrong_attempt < 3:

                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have training details")
                return {"ordinal3": None}

            else:
                update_status_of_training_form_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt")
                wrong_ordinal2_attempt = 0
                return self.deactivate()

        except:

            if wrong_attempt < 3:

                print("wrong_ordinal2_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_message("I am sorry! I do not have trainings")
                return {"ordinal3": None}

            else:

                update_status_of_training_form_slot = []
                wrong_attempt = 0
                dispatcher.utter_message("You reached to maximum limit of attempt")
                return self.deactivate()
    
    
    def validate_training_type_trainee(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global update_status_of_training_form_slot
        global sub_trainings_request
        global allowed_request
        print("allowed",allowed_request)
           
        print("validate training_type_trainee inside except value", value.title())
        
        if value.title() in ["Training","Self Study","Practical"]:
            wrong_attempt = 0
            update_status_of_training_form_slot.append("training_start_time")
            update_status_of_training_form_slot.append("training_end_time")
            # update_status_of_training_form_slot.append("status")
            # dispatcher.utter_message("I am updating training status to ongoing")
            return{"training_type_trainee":value.title()}
        
        elif wrong_attempt < 3:

            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("I am sorry! I do not have trainings")
            return{"training_type_trainee":None}
        else:
            update_status_of_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
    
    def validate_training_start_time(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of training_start_time ', value)
        if value is not None:
    
            return {"training_start_time": value}

        else:
            dispatcher.utter_template('utter_wrong_training_start_time',tracker)
            return {"training_start_time": None}
        
    
    def validate_training_end_time(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:
        global user_request,allowed_request

        print('validate value of training_end_time ', value)
        if value is not None:
            sr_no = tracker.get_slot("ordinal3")
            if user_request == "trainee" and allowed_request == "Pending_list":
                # if allowed_request != "Pending_list":
                if sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Pending":
                    update_status_of_training_form_slot.append("status")
                    dispatcher.utter_message("I am updating training status to In Progress")

                elif sub_trainings_request[sr_no]["sub_training_trainee_status"] == "In Progress":
                    try:
                        if tracker.get_slot("training_type_decision") == "Yes":
                            update_status_of_training_form_slot.append("status")
                            dispatcher.utter_message("I am updating training type only")
                        elif tracker.get_slot("training_type_decision") == "No":
                            update_status_of_training_form_slot.append("status")
                            dispatcher.utter_message("I am updating training status to Completed")
                        else:
                            update_status_of_training_form_slot.append("status")
                            dispatcher.utter_message("I am updating training status to Completed") 
                    except:
                        update_status_of_training_form_slot.append("status")
                        dispatcher.utter_message("I am updating training status to Completed")                                    


                elif sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Completed":
                    dispatcher.utter_message("You have already completed this training.")
            elif user_request == "trainer" and allowed_request != "Pending_list":
                if sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "In Progress" :
                    dispatcher.utter_message("I am updating training status to In Progress")
                    update_status_of_training_form_slot.append("status")
                elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "In Progress" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Completed":
                    update_status_of_training_form_slot.append("status")
                    update_status_of_training_form_slot.append("training_end_time")
                    dispatcher.utter_message("I am updating training status to Completed")

                elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Completed":
                    dispatcher.utter_message("Trainee have already completed this training.")
                elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Pending" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Pending" :
                    dispatcher.utter_message("You can not update the status of this training because the trainee has not yet started training")
                elif sub_trainings_request[sr_no]["sub_training_trainer_status"] == "Ongoing" and sub_trainings_request[sr_no]["sub_training_trainee_status"] == "Ongoing":
                    dispatcher.utter_message("You can not update the status of this training because the trainee has not yet completed training")

    
            return {"training_end_time": value}

        else:
            dispatcher.utter_template('training_end_time',tracker)
            return {"training_end_time": None}
    
    def validate_training_type_decision(
            self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> Optional[Text]:

        print('validate value of training_type_decision ', value)
        if tracker.latest_message["intent"].get("name") == "affirm":
            update_status_of_training_form_slot.append("training_type_decision")
                       
            wrong_attempt = 0
            return {"training_type_decision": "Yes"}

        elif tracker.latest_message["intent"].get("name") == "deny":
            update_status_of_training_form_slot.append("training_end_time")
            wrong_attempt = 0
            return {"training_type_decision":"No"}
        
        elif wrong_attempt < 3:
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_template("utter_wrong_training_type_decision",tracker)
                return{"training_type_decision":None}
        else:
            update_status_of_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()

    
    def validate_status(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global update_status_of_training_form_slot
        global sub_trainings_request
        global allowed_request
        print("allowed",allowed_request)
           
        print("validate status inside except value", value.title())
        print("intent",tracker.latest_message['intent'].get('name'))
        
        if tracker.latest_message['intent'].get('name')  == "affirm" :
            num = tracker.get_slot('ordinal3')
            if sub_trainings_request[num]["sub_training_trainee_status"]  == "Pending":
                wrong_attempt = 0
                return{"status":"In+Progress"}
            elif sub_trainings_request[num]["sub_training_trainee_status"]  == "In Progress":
                try:
                    if tracker.get_slot("training_type_decision") == "Yes":
                        wrong_attempt = 0
                        return{"status":"In+Progress"}
                    elif tracker.get_slot("training_type_decision") == "No":
                        wrong_attempt = 0
                        return{"status":"Completed"}
                    else:
                        wrong_attempt = 0
                        return{"status":"Completed"}
                except:
                    wrong_attempt = 0
                    return{"status":"Completed"}

        elif tracker.latest_message['intent'].get('name') == "status_of_training" :
            wrong_attempt = 0
            return{"status":value}
        elif tracker.latest_message['intent'].get('name') == "affirm": 
            num = tracker.get_slot('ordinal3')
            if sub_trainings_request[num]["sub_training_trainee_status"] == "Pending":
                wrong_attempt = 0
                return{"status":"In+Progress"}
            elif sub_trainings_request[num]["sub_training_trainee_status"] == "In Progress":
                wrong_attempt = 0
                return{"status":"Completed"}
        elif tracker.latest_message['intent'].get('name') == "deny": 
            wrong_attempt = 0
            return{"status":"No"}
        
        # if user_request = "trainer":
        #     if tracker.latest_message['intent'].get('name')  == "affirm" :
        #         num = tracker.get_slot('ordinal3')
        #         if sub_trainings_request[num]["sub_training_trainee_status"]  == "Pending":
        #             wrong_attempt = 0
        #             return{"status":"Ongoing"}
        #         elif sub_trainings_request[num]["sub_training_trainee_status"]  == "Ongoing":
        #             wrong_attempt = 0
        #             return{"status":"Completed"}
        #         elif tracker.latest_message['intent'].get('name') == "status_of_training" :
        #         wrong_attempt = 0
        #         return{"status":value}
        #     elif tracker.latest_message['intent'].get('name') == "affirm": 
        #         num = tracker.get_slot('ordinal3')
        #         if sub_trainings_request[num]["sub_training_trainee_status"] == "Pending":
        #             wrong_attempt = 0
        #             return{"status":"Ongoing"}
        #         elif sub_trainings_request[num]["sub_training_trainee_status"] == "Ongoing":
        #             wrong_attempt = 0
        #             return{"status":"Completed"}
        #     elif tracker.latest_message['intent'].get('name') == "deny": 
        #         wrong_attempt = 0
        #         return{"status":"No"}
            
        
        elif wrong_attempt < 3:
            num = tracker.get_slot('ordinal3')
            if sub_trainings_request[num]["sub_training_trainee_status"]  == "Pending":
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_template("utter_wrong_status",tracker)
                dispatcher.utter_message("I am going to update training status to Ongoing")
                return{"status":None}
            elif sub_trainings_request[num]["sub_training_trainee_status"]  == "Ongoing":
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_template("utter_wrong_status",tracker)
                dispatcher.utter_message("I am going to update training status to Completed")
                return{"status":None}
        else:
            update_status_of_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
        
    
    def validate_reason(self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
                domain: Dict[Text, Any]) -> Optional[Text]:

            print("validate reason value", value)
            value.upper()
            try:
                if value is not None:
                    sr_no = int(tracker.get_slot("ordinal1"))
                    print("inside if validate")
                    sr_no = tracker.get_slot("ordinal1")
                    training_request[sr_no]["training_id"]
                    response = requests.get("{}/ApprovalRejectionofTrainingRequest?Training_id={}&Action=Reject&Comment={}&User_Emp_Id={}".format
                    (mindsconnect_url, training_request[sr_no]["training_id"],value,tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    dispatcher.utter_message("I have Rejected training request successfully")
                    return {"reason": value}
            except:
                dispatcher.utter_message('Please enter reason of rejection', tracker)
                return {"reason": None}
            
class ActionUpdateStatusofTraining(Action):
    
    def name(self):
        return "action_update_status_of_training_form_submit"
            

    def run(self, dispatcher, tracker, domain):
        global  update_status_of_training_form_slot,visit_request,selection,user_request,allowed_request,sub_trainings_request,training_request
        try:
            if user_request == "trainee":
                try:
                    if tracker.get_slot("training_type_trainee") and tracker.get_slot("status"):
                        print("Inside trainee status with training type")
                        print("Status: "+tracker.get_slot("status")+" <br>Training type: "+tracker.get_slot("training_type_trainee"))
                        dispatcher.utter_message("Status: "+tracker.get_slot("status")+" <br>Training type: "+tracker.get_slot("training_type_trainee")
                        +" <br>Start time: "+tracker.get_slot("training_start_time")+" <br>End time: "+tracker.get_slot("training_end_time"))
                        print("Status updated successfully")
                        sr_no = tracker.get_slot("ordinal1")
                        sr_no1 = tracker.get_slot("ordinal3")
                        if sub_trainings_request[num]["sub_training_trainee_status"]  == "Pending":
                            today = str(date.today())
                            print(today)
                            response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status={}&Actual_Start_Date={}&Actual_End_Date=''&Start_Time={}&End_Time={}&Trainee_Employee_Code={}".format
                            (mindsconnect_url, training_request[sr_no]["training id"],sub_trainings_request[sr_no1]["sub_training id"],tracker.get_slot("status"),
                            today,tracker.get_slot("training_start_time"),tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                            data = response.json()
                            print(data)
                            print(len(data))
                            dispatcher.utter_message("Status changed successfully")     
                        else:
                            response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status={}&Actual_Start_Date=''&Actual_End_Date=''&Start_Time={}&End_Time={}&Trainee_Employee_Code={}".format
                            (mindsconnect_url, training_request[sr_no]["training id"],sub_trainings_request[sr_no1]["sub_training id"],tracker.get_slot("status"),
                            tracker.get_slot("training_start_time"),tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                            data = response.json()
                            print(data)
                            print(len(data))
                            # dispatcher.utter_message(data["errorDesc"]) 
                            dispatcher.utter_message("Status changed successfully")  

                    elif tracker.get_slot("status"):
                        today = str(date.today())
                        print(today)
                        print("Inside trainee only status")
                        print("Status: "+tracker.get_slot("status"))
                        dispatcher.utter_message("Status: "+tracker.get_slot("status"))
                        response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status={}&Actual_Start_Date=''&Actual_End_Date={}&Start_Time=''&End_Time={}&Trainee_Employee_Code={}".format
                        (mindsconnect_url, training_request[sr_no]["training id"],sub_trainings_request[sr_no1]["sub_training id"],tracker.get_slot("status"),
                        today,tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                        data = response.json()
                        print(data)
                        print(len(data))
                        # dispatcher.utter_message(data["errorDesc"])
                        print("Status updated successfully")
                        dispatcher.utter_message("Status changed successfully")
                except:
                    today = str(date.today())
                    print(today)
                    print("Inside trainee only status")
                    print("Status: "+tracker.get_slot("status"))
                    dispatcher.utter_message("Status: "+tracker.get_slot("status"))
                    response = requests.get("{}/UpdateTraineeStatusOfTraining?Training_id={}&Task_id={}&Status={}&Actual_Start_Date=''&Actual_End_Date={}&Start_Time=''&End_Time={}&Trainee_Employee_Code={}".format
                    (mindsconnect_url, training_request[sr_no]["training id"],sub_trainings_request[sr_no1]["sub_training id"],tracker.get_slot("status"),
                    today,tracker.get_slot("training_end_time"),tracker.get_slot("emp_code")))
                    data = response.json()
                    print(data)
                    print(len(data))
                    # dispatcher.utter_message(data["errorDesc"])
                    print("Status updated successfully")
                    dispatcher.utter_message("The training plan Status changed successfully")

            elif user_request == "trainer":
                print('user_request == "trainer":')
                sr_no = tracker.get_slot("ordinal3")
                print('user_request == "trainer":')
                response = requests.get("{}/UpdateStatusOfTraining?Task_Id={}&Trainer_Status={}&Trainer_employee_code={}".format(mindsconnect_url, sub_trainings_request[sr_no]["sub_training id"],tracker.get_slot("status"),tracker.get_slot("emp_code")))
                data = response.json()
                print(data)
                print(len(data))
                # dispatcher.utter_message(data["errorDesc"])        
                dispatcher.utter_message("Status changed successfully")       
                print(tracker.get_slot("status")+" <br>")
                print("The training plan Status changed successfully")
        except:
            print("something went wrong in updated status of training")
        try:
            if len( update_status_of_training_form_slot) < 1:
                dispatcher.utter_template("utter_continue_Training_requests",tracker)
                # buttons = []
                # buttons.append({"title": "Yes",
                #             "payload": "Yes"})
                # buttons.append({"title": "No",
                #             "payload": "No"})
                # dispatcher.utter_button_message(" Do you want to get training plan of this training request?", buttons)
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]
            elif user_request == "trainee" and allowed_request != "Pending_list" or user_request == "trainer" and allowed_request != "Pending_list":
                # visit_request = visit_request + 1
                # selection = tracker.get_slot("ordinal1")
                # buttons = []
                # buttons.append({"title": "Yes", "payload": "Yes"})
                # buttons.append({"title": "No","payload": "No"})
                # dispatcher.utter_button_message("Do you want to update status of topic in this training plan?", buttons)
                # return [SlotSet("status", None),SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("ordinal3", None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None)]
                dispatcher.utter_template("utter_continue_Training_requests",tracker)
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

            elif user_request == "admin" and training_request[tracker.get_slot("ordinal1")]["status"] == "Pending for Approval":
                # visit_request = visit_request + 1
                # selection = tracker.get_slot("ordinal1")
                # buttons = []
                # buttons.append({"title": "Yes", "payload": "Yes"})
                # buttons.append({"title": "No","payload": "No"})
                # dispatcher.utter_button_message("Do you want to Approve training plan of training request?", buttons)

                # return [SlotSet("status", None),SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("command", None),SlotSet("reason", None),SlotSet("training_type_decision", None),SlotSet("command", None),SlotSet("ordinal3", None),SlotSet("ordinal2", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None)]
                dispatcher.utter_template("utter_continue_Training_requests",tracker)
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

            else:
            
                # visit_request = visit_request + 1
                # selection = tracker.get_slot("ordinal1")
                # buttons = []
                # buttons.append({"title": "Yes", "payload": "Yes"})
                # buttons.append({"title": "No","payload": "No"})
                # dispatcher.utter_button_message("Do you want to get detail status of training plan?", buttons)
                # return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal1", None)]
                dispatcher.utter_template("utter_continue_Training_requests",tracker)
                return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]

        except:
            dispatcher.utter_message(template="utter_continue_Training_requests")
        print("Inside submit of training details")

        print("submit detail")

        return [SlotSet("trainings_period",None),SlotSet("compentency_group",None),SlotSet("specific_training",None),SlotSet("training_type_decision", None),SlotSet("training_start_time", None),SlotSet("training_end_time", None),SlotSet("trainees_for_request", None),SlotSet("number_of_trainee_for_request", None),SlotSet("ordinal2", None),SlotSet("ordinal1", None),SlotSet("ordinal3", None),SlotSet("status", None),SlotSet("training_type_trainee", None)]




# --------------------------------------------------------------------------------Request for training---------------------------------------------------------------
global request_for_training_training_form_slot
request_for_training_training_form_slot =["required_training_title","compentencies","required_training_type"]

class RequestforTrainingForm(FormValidationAction):

    def name(self):
        return "validate_request_for_training_training_form"


    
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
        ) -> Optional[List[Text]]:
        print("Inside required slot")
        global request_for_training_training_form_slot
        # request_for_training_training_form_slot =["required_training_title","required_training_type","required_training_mode"]
        return request_for_training_training_form_slot

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict[Text, Any]]]]:
        print("Inside slot mapping ordinal2")
        return {
            "required_training_title":
            [
                    self.from_text()
            ],
            "required_training_type":
            [
                    self.from_text()
            ],
            "required_training_mode":
            [
                    self.from_text()
            ],
            "required_training_trainer":
            [
                self.from_entity(entity="required_training_trainer"),
                self.from_entity(entity="PERSON"),
                self.from_entity(entity="ORG"),
                self.from_text()
            ],
            "required_training_exttrainer":
            [
                self.from_entity(entity="required_training_trainer"),
                self.from_entity(entity="PERSON"),
                self.from_entity(entity="ORG"),
                self.from_text()
            ],
            "required_training_exttrainer_mb_no":
            [
                self.from_entity(entity="required_training_trainer"),
                self.from_entity(entity="PERSON"),
                self.from_entity(entity="ORG"),
                self.from_text()
            ],
            "required_training_exttrainer_email_id":
            [
                self.from_entity(entity="required_training_trainer"),
                self.from_entity(entity="PERSON"),
                self.from_entity(entity="ORG"),
                self.from_text()
            ],
            "required_start_date":
            [
                    self.from_text()
            ],
            "required_end_date":
            [
                    self.from_text()
            ],
            "required_training_link":
            [
                    self.from_text()
            ],
            "required_training_cost":
            [
                    self.from_text(),
                    self.from_entity(entity="number"),
                    self.from_entity(entity="ordinal")
            ],
            "compentencies":
            [
                self.from_text()
            ],
            "required_training_delivery":
            [
                self.from_text()
            ]

            }
    
    
    
    def validate_required_training_title(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate title ",value)

        if value is not None:
            wrong_attemp = 0
            return {"required_training_title": value}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_required_training_title",tracker)
            return {"required_training_title": None}
        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()

    def validate_compentencies(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate title ",value)

        if value is not None:
            wrong_attemp = 0
            return {"compentencies": value}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_compentencies",tracker)
            return {"compentencies": None}
        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return []
    
    
    def validate_required_training_type(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate classification ",value.title())
        if value.title() in ["Internal","External"]:
            wrong_attemp = 0
            if value.title() == "Internal":
                request_for_training_training_form_slot.append("required_training_mode")
                # request_for_training_training_form_slot.append("required_training_link")
                # request_for_training_training_form_slot.append("required_training_cost")
                wrong_attempt = 0
                return {"required_training_type": "Internal"}
            elif value.title() == "External":
                request_for_training_training_form_slot.append("required_training_mode")
                return {"required_training_type": "External"}

        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("You have asked for ")
            return {"required_training_type": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_ordinal2_attempt = 0
            return self.deactivate()
    
    def validate_required_training_exttrainer(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate classification ",value.title())
        if value.title():
            wrong_attemp = 0
            return {"required_training_exttrainer": value.title()}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("You have asked for ")
            return {"required_training_exttrainer": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_ordinal2_attempt = 0
            return self.deactivate()
    
    def validate_required_training_exttrainer_mb_no(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate ext mb no ",value.title())
        regex = "^[0-9]{10}$"
        if re.search(regex,value):
            wrong_attemp = 0
            return {"required_training_exttrainer_mb_no": value.title()}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("Please enter 10 digits")
            return {"required_training_exttrainer_mb_no": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_ordinal2_attempt = 0
            return self.deactivate()
        
    def validate_required_training_exttrainer_email_id(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate ext trainer ",value.title())
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if re.search(regex,value):
            wrong_attemp = 0
            return {"required_training_exttrainer_email_id": value}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("Please provide valid email id")
            return {"required_training_exttrainer_email_id": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_ordinal2_attempt = 0
            return self.deactivate()
    
    
    def validate_required_training_mode(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print("Inside validate mode ",value.title())
        if value.title() in ["Web Portal","Face To Face","Video Conference","Through Web Portal","Video","Website","Video Lectures","Video Conferencing"]:
            wrong_attemp = 0
            if value.title() in ["Through web portal","Website","Web Portal"]:
                if tracker.get_slot("required_training_type") == "Internal":
                    request_for_training_training_form_slot.append("required_training_link")
                    request_for_training_training_form_slot.append("required_training_cost")
                    request_for_training_training_form_slot.append("required_start_date")
                    request_for_training_training_form_slot.append("required_end_date")
                    
                elif tracker.get_slot("required_training_type") == "External":
                    request_for_training_training_form_slot.append("required_training_link")
                    request_for_training_training_form_slot.append("required_training_cost")
                    request_for_training_training_form_slot.append("required_start_date")
                    request_for_training_training_form_slot.append("required_end_date")
                return {"required_training_mode": "Web Portal"}

            elif value.title() in ["Video Conference","Video","Video Lectures","Video Conferencing"]:
                
                if tracker.get_slot("required_training_type") == "Internal":
                    request_for_training_training_form_slot.append("required_training_link")
                    request_for_training_training_form_slot.append("required_training_trainer")
                    request_for_training_training_form_slot.append("required_start_date")
                    request_for_training_training_form_slot.append("required_end_date")
                    
                elif tracker.get_slot("required_training_type") == "External":
                    request_for_training_training_form_slot.append("required_training_link")
                    request_for_training_training_form_slot.append("required_training_exttrainer")
                    request_for_training_training_form_slot.append("required_training_exttrainer_mb_no")
                    request_for_training_training_form_slot.append("required_training_exttrainer_email_id")
                    request_for_training_training_form_slot.append("required_training_cost")
                    request_for_training_training_form_slot.append("required_start_date")
                    request_for_training_training_form_slot.append("required_end_date")
                return {"required_training_mode": "Video Conferencing"}
            
            elif value.title() in ["Face To Face"]:
                
                if tracker.get_slot("required_training_type") == "Internal":
                    request_for_training_training_form_slot.append("required_training_trainer")
                    request_for_training_training_form_slot.append("required_start_date")
                    request_for_training_training_form_slot.append("required_end_date")
                elif tracker.get_slot("required_training_type") == "External":
                    request_for_training_training_form_slot.append("required_training_exttrainer")
                    request_for_training_training_form_slot.append("required_training_exttrainer_mb_no")
                    request_for_training_training_form_slot.append("required_training_exttrainer_email_id")
                    request_for_training_training_form_slot.append("required_training_cost")
                    request_for_training_training_form_slot.append("required_start_date")
                    request_for_training_training_form_slot.append("required_end_date")
                    
                return {"required_training_mode": "Face To Face"}
        elif wrong_attempt < 3:
            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_message("Please enter correct response")
            return {"required_training_mode": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_ordinal2_attempt = 0
            return self.deactivate()
    
    def validate_required_training_trainer(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
    
        u = value.upper()
        print(u.rfind('OMI-'))
        try:
            if value.title() in name_of_employee:
                print(u.title()," u.title()")
                print("name_of_employee[u.title()]",name_of_employee[u.title()])
                valid = "true"
        except:
            valid = "flase"
            print("No name")
        if valid == "true":
            return {"required_training_trainer": name_of_employee[u.title()]}
        elif u.rfind('OMI-') == 0:
            print("inside if validate other employee code")
            wrong_attemp = 0
            return {"required_training_trainer": u}

        # elif u.title() in name_of_employee:
        #     wrong_attemp = 0
        #     print( u.title()," u.title()")
        #     return {"required_training_trainer": name_of_employee[u.title()]}
        else:
            response = requests.get("{}/empDetails?empdata={}".format(mindsconnect_url, value))
            data = response.json()
            print(len(data))
            len1 = (len(data))
            buttons = []
            name_of_employee = {}
            try:
                if len(data) > 1:
                    if len(data[0]) is 11:
                        # dispatcher.utter_message("Whom are you looking for  ")
                        for number in range(len1):
                            name_of_employee.update({"{} {}".format(data[number]['emp_first_name'],data[number]['emp_last_name']):data[number]['emp_code']})
                            buttons.append({"title": data[number]['emp_first_name'] + " " +
                                                     data[number]['emp_last_name'],
                                            "payload": "" + data[number]['emp_code']})

                    dispatcher.utter_button_message("Could you please select appropriate trainer?", buttons)
                    return {"required_training_trainer": None}
                elif len(data) is 1:
                    wrong_attemp = 0
                    return {"required_training_trainer": data[0]['emp_code']}
                else:
                    dispatcher.utter_template('utter_wrong_other_emp_code', tracker)
                    return {"required_training_trainer": None}
            except:
                if wrong_attempt < 3:
                    print("wrong_attempt",wrong_attempt)
                    wrong_attempt= wrong_attempt +1
                    dispatcher.utter_message(data['errorDesc'])
                    return {"required_training_trainer": None}
                else:
                    request_for_training_training_form_slot = []
                    wrong_attempt = 0
                    dispatcher.utter_message("You reached to maximum limit of attempt of providing trainer employee code/name. You should provide valid employee code[E.g OMI-XXXX]")
                    return self.deactivate()
    
    def validate_required_start_date(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print('value of required_start_date ', value)
        print('required_start_date ', value)

        current_intent = tracker.latest_message['intent'].get('name')
        print('current intent is ', tracker.latest_message['intent'].get('name'))

        if current_intent == 'stop':
            request_for_training_training_form_slot = []
            return self.deactivate()

        try:
            date_format = '%d-%m-%Y'
            # s_date = datetime.strptime(value, date_format)
            s_date = ((cal.nlp(value))[0][0]).strftime("%Y-%m-%d")
            print('Start date inside validate: ', s_date.strftime('%Y-%m-%d'))
            print('Start date inside validate:', s_date)
            wrong_attemp = 0
            return {"required_start_date": s_date}
        except Exception as e:
            if wrong_attempt <  3:
                print("wrong_attempt",wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                print('Exception from start date ', str(e))
                dispatcher.utter_template('utter_wrong_required_start_date', tracker)
                return {"required_start_date": None}
            else:
                request_for_training_training_form_slot = []
                wronge_attempt = 0
                dispatcher.utter_message("You have reached to maximum limit of attempts of date. You should give the date in valid format[e.g YYYY-MM-DD,23rd May]")
                return self.deactivate()  

    def validate_required_end_date(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        print('value of required_end_date ', value)
        print('required_end_date ', value)

        current_intent = tracker.latest_message['intent'].get('name')
        print('current intent is ', tracker.latest_message['intent'].get('name'))

        if current_intent == 'stop':
            request_for_training_training_form_slot = []
            return self.deactivate()

        try:
            date_format = '%d-%m-%Y'
            # s_date = datetime.strptime(value, date_format)
            s_date = ((cal.nlp(value))[0][0]).strftime("%Y-%m-%d")
            print('Start date inside validate: ', s_date.strftime('%Y-%m-%d'))
            print('Start date inside validate:', s_date)
            wrong_attemp = 0
            return {"required_end_date": s_date}
        except Exception as e:
            if wrong_attempt <  3:
                print("wrong_attempt",wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                print('Exception from start date ', str(e))
                dispatcher.utter_template('utter_wrong_required_end_date', tracker)
                return {"required_end_date": None}
            else:
                request_for_training_training_form_slot = []
                wronge_attempt = 0
                dispatcher.utter_message("You have reached to maximum limit of attempts of date. You should give the date in valid format[e.g YYYY-MM-DD,23rd May]")
                return self.deactivate()                      
    
    def validate_required_training_link(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        validate = URLValidator()
        try:
            validate(value)
            print("String is a valid URL")
            wrong_attemp = 0
            return {"required_training_link": value}
        except ValidationError as exception:
            
            if wrong_attempt < 3:
                print("String is not valid URL")
                print("wrong_attempt", wrong_attempt)
                wrong_attempt = wrong_attempt + 1
                dispatcher.utter_message("Entered Link/Website is not valid URL.")
                return {"required_training_link": None}

            else:
                request_for_training_training_form_slot = []
                dispatcher.utter_message("You reached to maximum limit of attempt. You should give URL in valid format[e.g http://www._____.___/]")
                wrong_attempt = 0
                return self.deactivate()
    
    def validate_required_training_cost(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        
        if value is not None:
            wrong_attemp = 0
            return {"required_training_cost":value}
        elif wrong_attempt < 3:

            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_required_training_cost",tracker)
            return {"required_training_cost": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
    
    def validate_required_training_delivery(
        self, value: Text, dispatcher: CollectingDispatcher, tracker: Tracker,
        domain: Dict[Text, Any]) -> Optional[Text]:

        global wrong_attempt
        global request_for_training_training_form_slot
        
        if value.title() in ["Video Conference","Through web portal","Video","Website","Video Lectures","Video Conferencing"]:
            if value.title() in ["Video Conference","Video","Video Lectures","Video Conferencing"]:
                assign = "Video Conferencing"
                request_for_training_training_form_slot.append("required_training_exttrainer")
                request_for_training_training_form_slot.append("required_training_exttrainer_mb_no")
                request_for_training_training_form_slot.append("required_training_exttrainer_email_id")
                request_for_training_training_form_slot.append("required_training_link")
                request_for_training_training_form_slot.append("required_training_cost")
                request_for_training_training_form_slot.append("required_start_date")
                request_for_training_training_form_slot.append("required_end_date")
            elif ["Through Web Portal","Website","Courses","Course","Web Portal"]:
                assign = "Web Portal"
                request_for_training_training_form_slot.append("required_training_link")
                request_for_training_training_form_slot.append("required_training_cost")
                request_for_training_training_form_slot.append("required_start_date")
                request_for_training_training_form_slot.append("required_end_date")

            wrong_attemp = 0
            return {"required_training_delivery":assign}
        elif wrong_attempt < 3:

            print("wrong_attempt", wrong_attempt)
            wrong_attempt = wrong_attempt + 1
            dispatcher.utter_template("utter_wrong_required_training_delivery",tracker)
            return {"required_training_cost": None}

        else:
            request_for_training_training_form_slot = []
            dispatcher.utter_message("You reached to maximum limit of attempt")
            wrong_attempt = 0
            return self.deactivate()
    
    
class ActionRequestforTraining(Action):
    
    def name(self):
        return "action_request_for_training_training_form_submit"
    
    
    def run(self, dispatcher, tracker, domain):
        global  request_for_training_training_form_slot
        if len( request_for_training_training_form_slot) < 1:
            buttons = []
            buttons.append({"title": "Yes", "payload": "Yes"})
            buttons.append({"title": "No","payload": "No"})
            dispatcher.utter_button_message("Do you want to request for training?", buttons)
        else:
            
            print("submit detail")
            
            print("training_title: ",tracker.get_slot("required_training_title"))
            print("training_type: ",tracker.get_slot("required_training_type"))
            print("training_mode: ",tracker.get_slot("required_training_mode"))
            print("training_start_date: ",tracker.get_slot("required_start_date"))
            print("training_end_date: ",tracker.get_slot("required_end_date"))
            print("compentencies: ",tracker.get_slot("compentencies"))
            if tracker.get_slot("required_training_type") == "Internal":
                if tracker.get_slot("required_training_mode") == "Video Conferencing":
        
                    print("training_link: ",tracker.get_slot("required_training_link"))
                    print("Internal_trainer",tracker.get_slot("required_training_trainer"))
                    
                    response = requests.get("{}/RequestforTrainingAPI?Title={}&Training_Type={}&Trainer_emp_code={}&Training_Mode={}&Start_Date={}&End_Date={}&Requested_By={}&Compentencies={}&Web_Link={}".format(mindsconnect_url,tracker.get_slot("required_training_title"),tracker.get_slot("required_training_type"),tracker.get_slot("required_training_trainer"),
                    tracker.get_slot("required_training_mode"),tracker.get_slot("required_start_date"),tracker.get_slot("required_end_date"),
                    tracker.get_slot("emp_code"),tracker.get_slot("compentencies"),tracker.get_slot("required_training_link")))
                    print(response)

                    dispatcher.utter_message("Thanks! I have received your request")
                elif tracker.get_slot("required_training_mode") == "Web Portal":
                   
                    print("training_link: ",tracker.get_slot("required_training_link"))
                    print("training_cost: ",tracker.get_slot("required_training_cost"))
                    response = requests.get('{}/RequestforTrainingAPI?Title={}&Training_Type={}&Training_Mode={}&Start_Date={}&End_Date={}&Requested_By={}&Compentencies={}&Cost={}&Web_Link={}'.format(mindsconnect_url, tracker.get_slot("required_training_title"),
                    tracker.get_slot("required_training_type"),tracker.get_slot("required_training_mode"),tracker.get_slot("required_start_date"),tracker.get_slot("required_end_date"),
                    tracker.get_slot("emp_code"),tracker.get_slot("compentencies"),tracker.get_slot("required_training_cost"),tracker.get_slot("required_training_link")))
                    print(response)
                    dispatcher.utter_message("Thanks! I have received your request")

                elif tracker.get_slot("required_training_mode") == "Face To Face":
                    print("elif tracker.get_slot('required_training_mode') == 'Face To Face':")
                    print("trainer: ",tracker.get_slot("required_training_trainer"))
                    response = requests.get('{}/RequestforTrainingAPI?Title={}&Training_Type={}&Trainer_emp_code={}&Training_Mode={}&Start_Date={}&End_Date={}&Requested_By={}&Compentencies={}'.format(mindsconnect_url, 
                    tracker.get_slot("required_training_title"), tracker.get_slot("required_training_type"),tracker.get_slot("required_training_trainer"),
                    tracker.get_slot("required_training_mode"),
                    tracker.get_slot("required_start_date"),tracker.get_slot("required_end_date"),
                    tracker.get_slot("emp_code"),tracker.get_slot("compentencies")))
                    print(response)
                    dispatcher.utter_message("Thanks! I have received your request")


            
            elif tracker.get_slot("required_training_type") == "External":
                if tracker.get_slot("required_training_mode") == "Web Portal":
                    print(' tracker.get_slot("required_training_delivery") == "Web Portal":')
                    print("training_link: ",tracker.get_slot("required_training_link"))
                    print("training_cost: ",tracker.get_slot("required_training_cost"))

                    response = requests.get('{}/RequestforTrainingAPI?Title={}&Training_Type={}&Training_Mode={}&Start_Date={}&End_Date={}&Requested_By={}&Compentencies={}&Cost={}&Web_Link={}'.format(mindsconnect_url, tracker.get_slot("required_training_title"), tracker.get_slot("required_training_type"),
                    tracker.get_slot("required_training_mode"),
                    tracker.get_slot("required_start_date"),tracker.get_slot("required_end_date"),
                    tracker.get_slot("emp_code"),tracker.get_slot("compentencies"),tracker.get_slot("required_training_cost"),tracker.get_slot("required_training_link")))
                    print(response)
                    print(response)
                    dispatcher.utter_message("Thanks! I have received your request")
                elif tracker.get_slot("required_training_mode") == "Video Conferencing":
                    print('if tracker.get_slot("required_training_mode") == "Online" and tracker.get_slot("required_training_delivery") == "Web Portal":')
                    print("training_link: ",tracker.get_slot("required_training_link"))
                    print("training_cost: ",tracker.get_slot("required_training_cost"))
                    print("ext trainer: ",tracker.get_slot("required_training_exttrainer"))
                    print("ext mb no: ",tracker.get_slot("required_training_exttrainer_mb_no"))
                    print("ext email id: ",tracker.get_slot("required_training_exttrainer_email_id"))
                    response = requests.get('{}/RequestforTrainingAPI?Title={}&Training_Type={}&EXTrainer_Name={}&EXTrainer_Email={}&EXTrainer_Mob={}&Training_Mode={}&Start_Date={}&End_Date={}&Requested_By={}&Compentencies={}&Cost={}&Web_Link={}'.format(mindsconnect_url, tracker.get_slot("required_training_title"), tracker.get_slot("required_training_type"),tracker.get_slot("required_training_exttrainer"),tracker.get_slot("required_training_exttrainer_email_id"),tracker.get_slot("required_training_exttrainer_mb_no"),
                    tracker.get_slot("required_training_mode"),tracker.get_slot("required_start_date"),tracker.get_slot("required_end_date"),
                    tracker.get_slot("emp_code"),tracker.get_slot("compentencies"),tracker.get_slot("required_training_cost"),tracker.get_slot("required_training_link")))
                    print(response)
                    print(response)
                    dispatcher.utter_message("Thanks! I have received your request")
                
                elif tracker.get_slot("required_training_mode") == "Face To Face":
                    print('tracker.get_slot("required_training_mode") == "Face To Face":')
                    print("ext trainer: ",tracker.get_slot("required_training_exttrainer"))
                    print("ext mb no: ",tracker.get_slot("required_training_exttrainer_mb_no"))
                    print("ext email id: ",tracker.get_slot("required_training_exttrainer_email_id"))
                    print("training_cost: ",tracker.get_slot("required_training_cost"))

                    response = requests.get('{}/RequestforTrainingAPI?Title={}&Training_Type={}&EXTrainer_Name={}&EXTrainer_Email={}&EXTrainer_Mob={}&Training_Mode={}&Start_Date={}&End_Date={}&Requested_By={}&Compentencies={}&Cost={}'.format(mindsconnect_url, tracker.get_slot("required_training_title"), tracker.get_slot("required_training_type"),tracker.get_slot("required_training_exttrainer"),tracker.get_slot("required_training_exttrainer_email_id"),tracker.get_slot("required_training_exttrainer_mb_no"),
                    tracker.get_slot("required_training_mode"),
                    tracker.get_slot("required_start_date"),tracker.get_slot("required_end_date"),
                    tracker.get_slot("emp_code"),tracker.get_slot("compentencies"),tracker.get_slot("required_training_cost")))
                    print(response)
                    dispatcher.utter_message("Thanks! I have received your request")
            request_for_training_training_form_slot =["required_training_title","compentencies","required_training_type"]
                
            buttons = []
            buttons.append({"title": "Yes", "payload": "Yes"})
            buttons.append({"title": "No","payload": "No"})
            dispatcher.utter_button_message("Do you want to request for one more training?", buttons)
            
        return [SlotSet("required_training_title",None),SlotSet("required_training_type",None),SlotSet("required_training_mode",None),SlotSet("required_training_trainer",None),SlotSet("required_training_exttrainer",None),SlotSet("required_training_exttrainer_mb_no",None),SlotSet("required_training_exttrainer_email_id",None),SlotSet("required_start_date",None),SlotSet("required_end_date",None),SlotSet("required_training_link",None), SlotSet("required_training_cost",None),SlotSet("compentencies",None),SlotSet("required_training_delivery",None)]

##----------------------------------------------------------Requested training list------------------------------------------------

class ActionProfileInfo(Action):

    def name(self):
        return 'action_show_requested_trainings'

    def run(self, dispatcher, tracker, domain):
        end_date,start_date = None,None
       
        try:
            if tracker.get_slot('daterange'):
                tracker.get_slot('daterange')
                date1 = tracker.get_slot('daterange')
                print(date1)
                start_date = date1['start_date']
                print('start_date',date1['start_date'])
                end_date = date1['end_date']
                print('end_date', date1['end_date'])
                print('end_date', date1['end_date'])
        except:
            start_date = (dt.datetime.now()).strftime("%d/%m/%Y")
            print('start_date', start_date)
            end_date = (dt.datetime.now()).strftime("%d/%m/%Y")
            print('end_date', end_date)

        response = requests.get("{}/ListofRequestedTraining?User_Emp_Code={}".format(mindsconnect_url,tracker.get_slot("emp_code")))

        print(response)
        data1 = response.json()
        print(data1)
        print(len(data1))
        global requested_training,tb,display_requested_training_data
        display_requested_training_data = {}
        requested_training = {}
        tb = []
        global display_requested_training
        display_requested_training = []
        try:
            for requestedTraining in data1:
                requested_training.update({requestedTraining['retr_id']:[requestedTraining['training_Topic'],
                requestedTraining['training_type'],dt.datetime.strptime(requestedTraining['startDate'],"%b %d, %Y %H:%M:%S %p").strftime("%d/%m/%Y"),
                dt.datetime.strptime(requestedTraining['endDate'],"%b %d, %Y %H:%M:%S %p").strftime("%d/%m/%Y"),requestedTraining['training_Mode'],
                requestedTraining['compentencies'],"{} {}".format(requestedTraining['requested_by']['emp_first_name'],requestedTraining['requested_by']['emp_last_name']),requestedTraining['status'],dt.datetime.strptime(requestedTraining['requested_by']['creation_date'],"%b %d, %Y %H:%M:%S %p").strftime("%d/%m/%Y")]})
        
        except:
            dispatcher.utter_message(data1['errorDesc'])
        
        try:
            array_count_month = 1

            for key in requested_training.keys():

                print("requested_training[key][1]",requested_training[key][1])
                print("requested_training[key][2]",requested_training[key][2])

                if start_date <= requested_training[key][1] and end_date >= requested_training[key][2] or start_date <= requested_training[key][2]  and end_date != None:

                    print("start_date <= requested_training[key][1]",start_date <= requested_training[key][1])
                    print("end_date >= requested_training[key][2]", end_date >= requested_training[key][2])

                    if tracker.get_slot("emp_code") == "OMI-0076":

                        display_requested_training_data.update({array_count_month:{"sr.no":array_count_month,"topic":requested_training[key][0],"requestedDate":requested_training[key][8],"status":requested_training[key][7]}})
                        display_requested_training.append("<td style='padding: 2% 2%;'>{}.</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 3%;'>{}</td>".format(array_count_month,
                        requested_training[key][0],
                        requested_training[key][8],                                     
                        requested_training[key][7]))

                    else:

                        display_requested_training_data.update({array_count_month:{"sr.no":array_count_month,"topic":requested_training[key][0],"requestedDate":requested_training[key][8],"status":requested_training[key][7]}})
                        
                        display_requested_training.append("<td style='padding: 2% 2%;'>{}.</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 3%;'>{}</td>".format(array_count_month,
                        requested_training[key][0],
                        requested_training[key][8],                                     
                        requested_training[key][7]))
                    

                elif start_date <= approved_leaves[key][1] or end_date <= approved_leaves[key][2] or start_date <= approved_leaves[key][2]  and end_date != None:

                    print("start_date == approved_leaves[key][1]", start_date == approved_leaves[key][1])
                    print("end_date == approved_leaves[key][2]", end_date == approved_leaves[key][2])
                    if tracker.get_slot("emp_code") == "OMI-0076":
                        display_requested_training_data.update({array_count_month:{"sr.no":array_count_month,"topic":requested_training[key][0],"requestedDate":requested_training[key][8],"status":requested_training[key][7]}})
                         
                        display_requested_training.append("<td style='padding: 2% 2%;'>{}.</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 3%;'>{}</td>".format(array_count_month,
                        requested_training[key][0],
                        requested_training[key][8],                                     
                        requested_training[key][7]))
                    else:
                        display_requested_training_data.update({array_count_month:{"sr.no":array_count_month,"topic":requested_training[key][0],"requestedDate":requested_training[key][8],"status":requested_training[key][7]}})
                         
                        display_requested_training.append("<td style='padding: 2% 2%;'>{}.</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 3%;'>{}</td>".format(array_count_month,
                        requested_training[key][0],
                        requested_training[key][8],                                     
                        requested_training[key][7]))
                array_count_month = array_count_month + 1


        except:

            if start_date == None and end_date == None:
                print("end_date == None", end_date == None)
                array_count_month = 1
                for key in requested_training.keys():
        
                    if tracker.get_slot("emp_code") == "OMI-0076":
                        display_requested_training_data.update({array_count_month:{"sr.no":array_count_month,"topic":requested_training[key][0],"requestedDate":requested_training[key][8],"status":requested_training[key][7]}})
                          
                        display_requested_training.append("<td style='padding: 2% 2%;'>{}.</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 3%;'>{}</td>".format(array_count_month,
                            requested_training[key][1],
                            requested_training[key][8],                                     
                            requested_training[key][7]))
        
                    else:
                        display_requested_training_data.update({array_count_month:{"sr.no":array_count_month,"topic":requested_training[key][0],"requestedDate":requested_training[key][8],"status":requested_training[key][7]}})
                        
                        display_requested_training.append("<td style='padding: 2% 2%;'>{}.</td><td style='padding: 2% 2%;'>{}</td><td style='padding: 2% 3%;'>{}</td><td>{}</td>".format(array_count_month,
                            requested_training[key][1],
                            requested_training[key][8],                                     
                            requested_training[key][7]))
                    array_count_month = array_count_month + 1
        try:
        
            if len(display_requested_training_data) != 0:
                print(display_requested_training_data)
                requested_training = "<b>Following is Requested training list</b><table style='width:min-content;font-size:85%'><tr><th style='padding: 2% 2%;'>Sr.No</th><th style='padding: 2% 2%;'>Title</th><th style='padding: 2% 2%;'>Requested Date</th><th style='padding: 2% 3%;'>Status</th></tr>"
        
                for i in range(0,len(display_requested_training_data)):
                    print("table data")

                    tb.append({
                        "type": "table",
                        "title": "Following is Requested training list",
                        "table_row_head":
                                        [
                                            {
                                                "title": "Sr. No"
												
											},
											{
                                                "title": "Title"
												
											},
											{
                                                "title": "Requested Date"
												
											},
											{
                                                "title": "Status"
												
											}
                                        ],

                                    "row_data":
                                        [
                                            {
                                                "title": display_requested_training_data[i+1]["sr.no"]
												
											},
											{
                                                "title": display_requested_training_data[i+1]["topic"]
												
											},
											{
                                                "title": display_requested_training_data[i+1]["requestedDate"]
												
											},
											{
                                                "title": display_requested_training_data[i+1]["status"]
												
											}
                                        ]
                            })
                dispatcher.utter_custom_json(tb)
            else:
                pass
        
        except:
            pass
        dispatcher.utter_template("utter_continue_Training_management", tracker)
        return [SlotSet("daterange",None)]
# -------------------------------------------------------set login slots-----------------------------------------------------

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
        print(EMP_name)
        print("setting employee code is", emp_code)
        print("password is", password)
        return [SlotSet('emp_code',emp_code),SlotSet('password',password)]
    