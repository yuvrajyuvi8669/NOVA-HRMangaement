# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
#
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import SlotSet
import requests
import re
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

mindsconnect_url ="http://uat.omfysgroup.com/mindsconnect/"

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
        dispatcher.utter_message(text="login successfully")
        return [SlotSet('emp_code',emp_code),SlotSet('password',password)]
        
        


class Actionofficetiming(Action):

    def name(self) -> Text:
        return "action_attendance"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message(text="Office starts at 09:30 AM and closes at 06:30 PM")

        return [FollowupAction("utter_attendance")]


class Actiongeneral(Action):
#
    def name(self) -> Text:
        return "action_general"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message(text="Hello World!")

        return [FollowupAction("utter_general")]

class Actionactiontravel(Action):

    def name(self) -> Text:
        return "action_travel"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message(text="Hello World!")

        return [FollowupAction("utter_travel")]

class Actionleave(Action):

    def name(self) -> Text:
        return "action_leave"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # dispatcher.utter_message(text="Hello World!")

        return [FollowupAction("utter_leave")]


# class Actionleave(Action):

#     def name(self) -> Text:
#         return "action_timing"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         # dispatcher.utter_message(text="Hello World!")

#         return [FollowupAction("utter_timing")]



