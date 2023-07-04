
from flask import Flask,request
from flask_cors import CORS, cross_origin
from rasa.core.agent import Agent
from rasa.core.utils import EndpointConfig
import asyncio
from rasa.core.interpreter import RasaNLUInterpreter
import json
import threading
import logging
import tensorflow as tf

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
###----------------------------------------------------------logging--------------------------------------------
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

##-----------------------------------------------------logging end---------------------------------------------

global state,current_model,prev_msg,prev_skill

state = "None"
current_model = "None"
prev_msg = ""
prev_skill = ""

def agent_get(orgid,action_endpoint):
  
  orgId = {
  # "agent_one": "training_management.tar.gz", # Model trained for training management
  "agent_two": "tte.tar.gz", # model trainined for tte
  "agent_three": "login_logout.tar.gz", #model trained for initial process of login and logout
  "agent_four": "leave_mgmt.tar.gz", # leave management process model trained
  "agent_five": "Profile_info.tar.gz", # employee profile related model
  "agent_six": "faq.tar.gz", # employee profile related model
  "agent_seven": "leave_approval.tar.gz" # employee profile related model

  }

  
  logger.debug(orgId)
  
# loading each agent as per the input from 
  
  agent = Agent.load(orgId[orgid],action_endpoint = EndpointConfig(action_endpoint))
  # logger.info(agent)
  print(agent)
  return agent

async def process(agent, msg,sender):
  output = await agent.handle_text(text_message = msg, output_channel = None, sender_id = sender)
  # interpreter = NaturalLanguageInterpreter.create(model_dir)
  
  ##logger.info(output)
  return output
  
# current_agent_training=agent_get("agent_one","http://140.238.226.29:5007/webhook")
#current_agent_tte=agent_get("agent_two","http://140.238.226.29:5055/webhook")
#current_agent_login_logout=agent_get("agent_three","http://140.238.226.29:5008/webhook")
#current_agent_leave_mgmt=agent_get("agent_four","http://140.238.226.29:5009/webhook")
#current_agent_profile_info=agent_get("agent_five","http://140.238.226.29:5010/webhook")
#current_agent_faq=agent_get("agent_six","http://140.238.226.29:5012/webhook")
#current_agent_leave_approval=agent_get("agent_seven","http://140.238.226.29:5013/webhook")

#152.67.3.60
# current_agent_training=agent_get("agent_one","http://localhost:5007/webhook")
current_agent_tte=agent_get("agent_two","http://localhost:5055/webhook")
# current_agent_login_logout=agent_get("agent_three","http://152.67.3.60:5008/webhook")
current_agent_login_logout=agent_get("agent_three","http://localhost:5008/webhook")
current_agent_leave_mgmt=agent_get("agent_four","http://localhost:5009/webhook")
current_agent_profile_info=agent_get("agent_five","http://localhost:5010/webhook")
current_agent_faq=agent_get("agent_six","http://localhost:5012/webhook")
current_agent_leave_approval=agent_get("agent_seven","http://localhost:5013/webhook")

async def confidence(agent,msg):

  nlu_data = await agent.parse_message_using_nlu_interpreter(msg)
  
  # logger.info(nlu_data)
  # sample data {'text': 'I want to provide dealer id', 'intent': {'id': -7037397904428323475, 'name': 'tte_details', 
  # 'confidence': 1.0}, 'entities': [], 'intent_ranking': [{'id': -7037397904428323475, 'name': 'tte_details', 'confidence': 1.0}, {'id': 8819404522623617675, 'name': 'tte_data', 'confidence': 0.0}, {'id': -4803468243789877574, 'name': 'greet', 'confidence': 0.0}, {'id': 3991193620824245297, 'name': 'deny', 'confidence': 0.0}, {'id': 155160037092916469, 'name': 'affirm', 'confidence': 0.0}, {'id': -2473950508863265022, 'name': 'Thanksgving', 'confidence': 0.0}], 'response_selector': {'all_retrieval_intents': [], 'default': {'response': {'id': None, 'responses': None, 'response_templates': None, 'confidence': 0.0, 'intent_response_key': None, 'utter_action': 'utter_None', 'template_name': 'utter_None'}, 'ranking': []}}}
  
  intent_name = nlu_data['intent']['name']
  confidence = nlu_data['intent']['confidence']
  return confidence,intent_name

async def predict(agent,sender_id):

  predict_action = await agent.predict_next(sender_id)
  print(predict_action)
  # logger.info(predict_action)
  next_action = predict_action['tracker']['latest_action_name']
  return next_action

@app.route("/message", methods=["POST"])
@cross_origin(origin="*")
def new_message():  
  
  if not request.json:
    abort(400)
    
  global current_model,state,prev_msg,prev_skill
  # logger.info("request.json",request.json)
  print("request.json",request.json)
  user = request.json["sender"]
  user_message = request.json["message"]
  
  intent_name_training = "None"
  intent_name_tte = "None"
  intent_name_login_logout = "None"
  intent_name_leave_mgmt = "None"
  intent_name_profile_info = "None"
  intent_name_faq = "None"
  intent_name_leave_approval = "None"
  
  # res_training = (current_agent_training.handle_text(text_message=message, sender_id=user))
  # res_tte = (current_agent_tte.handle_text(text_message=message, sender_id=user))
  
  try:
    
    loop = asyncio.get_event_loop()
  
  except RuntimeError as ex:
  
      if "There is no current event loop in thread" in str(ex):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
  
  loop = asyncio.get_event_loop()
  
  # # creating thread
  # t1 = threading.Thread(target=loop.run_until_complete(confidence), args=((current_agent_login_logout, user_message,)))
  # t2 = threading.Thread(target=loop.run_until_complete(confidence), args = (current_agent_training, user_message))
  # t3 = threading.Thread(target=loop.run_until_complete(confidence), args=(current_agent_tte, user_message,))
  
  # # starting thread 1
  # t1.start()
  # # starting thread 2
  # t2.start()
  # # starting thread 3
  # t3.start()
  
  # # wait until thread 1 is completely executed
  # confidence_login_logout,intent_name_login_logout = t1.join()
  # # wait until thread 2 is completely executed
  # confidence_training,intent_name_training = t2.join()
  # # wait until thread 3 is completely executed
  # confidence_tte,intent_name_tte = t3.join()
  # # three threads executed
  
  # confidence_training,intent_name_training = loop.run_until_complete(confidence(current_agent_training, user_message))
  confidence_login_logout,intent_name_login_logout = loop.run_until_complete(confidence(current_agent_login_logout, user_message))
  confidence_tte,intent_name_tte = loop.run_until_complete(confidence(current_agent_tte, user_message))
  confidence_leave_mgmt,intent_name_leave_mgmt = loop.run_until_complete(confidence(current_agent_leave_mgmt, user_message))
  confidence_profile_info,intent_name_profile_info = loop.run_until_complete(confidence(current_agent_profile_info, user_message))
  confidence_faq,intent_name_faq = loop.run_until_complete(confidence(current_agent_faq, user_message))
  confidence_leave_approval,intent_name_leave_approval = loop.run_until_complete(confidence(current_agent_leave_approval, user_message))
  # finding max confidence
  # confidences = [confidence_training,confidence_tte,confidence_leave_mgmt,confidence_profile_info,confidence_faq,confidence_leave_approval]
  
  confidences = [confidence_tte,confidence_leave_mgmt,confidence_profile_info,confidence_faq,confidence_leave_approval]

  #allskill = ["Training_Skill","TTE Skill","Leave Management","Profile Info","FAQ Skill","Leave Approval"]
  allskill = ["TTE Skill","Leave Management","Profile Info","FAQ Skill","Leave Approval"]
  max_confidence_index = confidences.index(max(confidences))
  skill_name = allskill[max_confidence_index]
  print("max_confidence_index",max_confidence_index)
  print("skill with max confidence",allskill[max_confidence_index])
  
  # logger.info("max_confidence_index",max_confidence_index)

  # print(intent_name_training,"intent_name_training")
  print(intent_name_tte,"intent_name_tte")
  print(intent_name_login_logout,"intent_name_login_logout")
  print(intent_name_leave_mgmt,"intent_name_leave_mgmt")
  print(intent_name_profile_info,"intent_name_profile_info")
  print(intent_name_faq,"intent_name_faq")
  print(intent_name_leave_approval,"intent_name_leave_approval")

  # print(f'''{confidence_leave_approval} confidence leave approval <br>{confidence_faq} confidence faq <br>{confidence_profile_info} confidence profile info <br>{confidence_leave_mgmt} confidence leave management <br>{confidence_login_logout} confidence_login_logout<br>{confidence_training} confidence_training<br>{confidence_tte} confidence_tte''')
  
  # print(confidence_tte,"-------------------------confidence of tte")
  # logger.info(intent_name_training,"intent_name_training")
  # logger.info(intent_name_tte,"intent_name_tte")
  # logger.info(intent_name_login_logout,"intent_name_login_logout")
  # logger.info(intent_name_leave_mgmt,"intent_name_leave_mgmt")
  # logger.info(intent_name_profile_info,"intent_name_profile_info")

  # logger.info(f'''{confidence_profile_info} confidence profile info <br>{confidence_leave_mgmt} confidence leave management <br>{confidence_login_logout} confidence_login_logout<br>{confidence_training} confidence_training<br>{confidence_tte} confidence_tte''')
  
  # logger.info(confidence_tte,"-------------------------confidence of tte")

  if confidence_login_logout > 0.7 and intent_name_login_logout in ['greet','user_login','logout','main_menu']:

    # logger.info("greet or login")
    print("greet or login")
    current_model = "login"
  
    if intent_name_login_logout == 'logout':
      # print("hello")
      loop.run_until_complete(process(current_agent_profile_info, "/restart",user))
      
      # loop.run_until_complete(process(current_agent_tte, "/restart",user))
    # message = [{'recipient_id': user, 'text': 'Congratulations! You are to avail my assistance. You can choose features to get started or type in a direct message.', 'buttons': [{'title': 'TTE', 'payload': 'TTE'}, {'title': 'Training Management', 'payload': 'Training Management'}]}]
  
  elif state == "switch_to_desired_model":
  
    if user_message in ["yes","Yes","YES"] or intent_name_tte == "affirm":
      
      print(f"prev skill {prev_skill}")
      #state = None
      current_model = prev_skill
      user_message = prev_msg
      print("current model=------",current_model)
      print("user_message=------",user_message)
      #message = [{'recipient_id': user, 'text': f'Do you want me to go in {skill_name} service?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    elif user_message in ["no","No","NO"] or intent_name_tte == "deny":
    
      state = "desired_model_no_match"
      current_model = "login"
      user_message = "main menu"
      print("current model no no=------",current_model)
      print("user_message no no=------",user_message)
      
  elif state == "switch_TTE" or state == "switch_Training"or state == "switch_leave_approval" or state == "switch_Leave_mgmt" or state == "switch_profile_info" or state == "switch_faq":
    
    print(state,"----state----")
    if user_message in ["yes","Yes","YES"] or intent_name_tte == "affirm":
    
      print("affirm",user_message)
      state = "switch_to_desired_model"
      user_message = prev_msg
      current_model = ""
      message = [{'recipient_id': user, 'text': f'Do you want me to go in {skill_name} service?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    elif user_message in ["no","No","NO"] or intent_name_tte == "deny":
    
      state = "cancel_switch"
      print(prev_msg,"prev_msg")
      # logger.info(prev_msg,"prev_msg")
      user_message = prev_msg
  
  # elif confidence_login_logout > 0.7 and intent_name_login_logout == "Training_Management":
    
  #   print("User message Training")
  #   # logger.info("User message Training")
  #   current_model = "Training_Skill"

  elif confidence_login_logout > 0.7 and intent_name_login_logout == "faq":
    
    print("User message FAQ")
    # logger.info("User message Training")
    current_model = "FAQ_Skill"
      
  elif confidence_login_logout > 0.7 and intent_name_login_logout == "tte_mgmt":
    
    # logger.info("User message TTE")
    print("User message TTE")
    current_model = "TTE_Skill"

  elif confidence_leave_approval > 0.7 and intent_name_leave_approval == "asking_for_pending_leaves":
    
    # logger.info("User message TTE")
    print("User message leave approval")
    current_model = "Leave_Approval"
    
  elif confidence_login_logout > 0.7 and intent_name_login_logout == "leaves":
    
    # logger.info("User message leave management")
    print("User message leave management")
    current_model = "Leave_Management"
  
  elif confidence_login_logout > 0.7 and intent_name_login_logout == "prof_info":
    
    # logger.info("User message Profile Info")
    print("User message Profile Info")
    current_model = "Profile_Info"
  
  else:
  
    user_message

  if current_model == "Training_Skill":
    
    print("Training user_message",user_message)
    # logger.info("Training user_message",user_message)
    confidence_training,intent_name_training = loop.run_until_complete(confidence(current_agent_training, user_message))
    # logger.info("Training confidence",confidence_training)
    print("Training confidence",confidence_training)
    
    if state == "cancel_switch":
      
      state = None
      message_training = loop.run_until_complete(process(current_agent_training, user_message,user))
      message = message_training 
    
    elif state == "desired_model_no_match":
      
      user_message = prev_msg
      state = None
      message_training = loop.run_until_complete(process(current_agent_training, user_message,user))
      message = message_training 
    
    elif confidence_training < 0.3:
      
      prev_skill = skill_name.replace(" ","_")
      state = "switch_Training"
      prev_msg = user_message
      message = [{'recipient_id': 'default', 'text': 'Have you done with questions related to Training?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    else:
      
      message_training = loop.run_until_complete(process(current_agent_training, user_message,user))
      message = message_training 
  
  elif current_model == "TTE_Skill":
    
    print("TTE user_message",user_message)
    # logger.info("TTE user_message",user_message)
    confidence_tte,intent_name_tte = loop.run_until_complete(confidence(current_agent_tte, user_message))
    print("TTE confidence",confidence_tte)
    # logger.info("TTE confidence",confidence_tte)
    
    if state == "cancel_switch":
      
      state = None
      message_tte = loop.run_until_complete(process(current_agent_tte, user_message,user))
      message = message_tte 
    elif state == "desired_model_no_match":
      user_message = prev_msg
      state = None
      message_tte = loop.run_until_complete(process(current_agent_tte, user_message,user))
      message = message_tte 
    elif confidence_tte < 0.7:
      prev_skill = skill_name.replace(" ","_")
      state = "switch_TTE"
      prev_msg = user_message
      message = [{'recipient_id': user, 'text': 'Have you done with questions related to Project Management?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    else:
      
      message_tte = loop.run_until_complete(process(current_agent_tte, user_message,user))
      message = message_tte 
  
  elif current_model == "Leave_Management":
    
    print("leave mgmt user_message",user_message)
    # logger.info("leave mgmt user_message",user_message)
    confidence_leave_mgmt,intent_name_leave_mgmt = loop.run_until_complete(confidence(current_agent_leave_mgmt, user_message))
    print("leave mgmt confidence",confidence_leave_mgmt)
    # logger.info("leave mgmt confidence",confidence_leave_mgmt)
    
    if state == "cancel_switch":
      
      state = None
      message_leave_mgmt = loop.run_until_complete(process(current_agent_leave_mgmt, user_message,user))
      message = message_leave_mgmt
    
    elif confidence_leave_mgmt < 0.7:
      
      prev_skill = skill_name.replace(" ","_")
      state = "switch_Leave_mgmt"
      prev_msg = user_message
      message = [{'recipient_id': user, 'text': 'Have you done with questions related to Leave Management?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    elif state == "desired_model_no_match":
      user_message = prev_msg
      state = None
      message_leave_mgmt = loop.run_until_complete(process(current_agent_leave_mgmt, user_message,user))
      message = message_leave_mgmt
    else:
      
      message_leave_mgmt = loop.run_until_complete(process(current_agent_leave_mgmt, user_message,user))
      message = message_leave_mgmt
      
  elif current_model == "Profile_Info":
    
    print("profile info user_message",user_message)
    # logger.info("profile info user_message",user_message)
    confidence_profile_info,intent_name_profile_info = loop.run_until_complete(confidence(current_agent_profile_info, user_message))
    print("profile info confidence",confidence_profile_info)
    # logger.info("profile info confidence",confidence_profile_info)
    
    if state == "cancel_switch":
      
      state = None
      message_profile_info = loop.run_until_complete(process(current_agent_profile_info, user_message,user))
      message = message_profile_info
    
    elif confidence_profile_info < 0.7:
      prev_skill = skill_name.replace(" ","_")
      state = "switch_profile_info"
      prev_msg = user_message
      message = [{'recipient_id': user, 'text': 'Have you done with questions related to Profile Info?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    elif state == "desired_model_no_match":
      user_message = prev_msg
      state = None
      message_profile_info = loop.run_until_complete(process(current_agent_profile_info, user_message,user))
      message = message_profile_info
      
    else:
      
      message_profile_info = loop.run_until_complete(process(current_agent_profile_info, user_message,user))
      message = message_profile_info
     
  elif current_model == "FAQ_Skill":
    
    print("faq user_message",user_message)
    # logger.info("profile info user_message",user_message)
    confidence_faq,intent_name_faq = loop.run_until_complete(confidence(current_agent_faq, user_message))
    print("faq confidence",confidence_faq)
    # logger.info("profile info confidence",confidence_profile_info)
    
    if state == "cancel_switch":
      
      state = None
      message_faq = loop.run_until_complete(process(current_agent_faq, user_message,user))
      message = message_faq
    
    elif confidence_faq < 0.7:
      prev_skill = skill_name.replace(" ","_")
      state = "switch_faq"
      prev_msg = user_message
      message = [{'recipient_id': user, 'text': 'Have you done with questions related to FAQ?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    elif state == "desired_model_no_match":
      user_message = prev_msg
      state = None
      message_faq = loop.run_until_complete(process(current_agent_faq, user_message,user))
      message = message_faq
    else:
      
      message_faq = loop.run_until_complete(process(current_agent_faq, user_message,user))
      message = message_faq
    
  elif current_model == "Leave_Approval":
    
    print("leave approval user_message",user_message)
    # logger.info("profile info user_message",user_message)
    confidence_leave_approval,intent_name_leave_approval = loop.run_until_complete(confidence(current_agent_leave_approval, user_message))
    print("leave approval confidence",confidence_leave_approval)
    # logger.info("profile info confidence",confidence_profile_info)
    
    if state == "cancel_switch":
      
      state = None
      message_leave_approval = loop.run_until_complete(process(current_agent_leave_approval, user_message,user))
      message = message_leave_approval
    
    elif confidence_leave_approval < 0.7:
    
      prev_skill = skill_name.replace(" ","_")
      state = "switch_leave_approval"
      prev_msg = user_message
      message = [{'recipient_id': user, 'text': 'Have you done with questions related to Leave Approval?', 'buttons': [{'title': 'Yes', 'payload': 'yes'}, {'title': 'No', 'payload': 'no'}]}]
    
    # elif state == "switch_leave_approval" and user_message.lower() in ['yes',"y","yeah","yep","yup"]:
    #   message = prev_msg
    
    elif state == "desired_model_no_match":
    
      user_message = prev_msg
      state = None
      message_leave_approval = loop.run_until_complete(process(current_agent_leave_approval, user_message,user))
      message = message_leave_approval
   
    else:
      print("inside else of leave approval")
      message_leave_approval = loop.run_until_complete(process(current_agent_leave_approval, user_message,user))
      message = message_leave_approval
      print(message,"---------------- message of leave approval")
    
  elif current_model == "login":
    
    print(intent_name_login_logout,"intent_name_login_logout")
    print("login user_message",user_message)
    # logger.info("login user_message",user_message)
    confidence_login_logout,intent_name_login_logout = loop.run_until_complete(confidence(current_agent_login_logout, user_message))
    # logger.info("login confidence",confidence_login_logout)
    print("login confidence",confidence_login_logout)
    
    message_login_logout= loop.run_until_complete(process(current_agent_login_logout, user_message,user))
    # message = message_login_logout
    sent_msg = message_login_logout                                                                                                                                                                                                                                                                                                            
    print(message_login_logout)
    # logger.info(message_login_logout)
    
    try:
    
      sent_msg = [] 
      
      for x in message_login_logout:    
        
        if x['text'].find("employee code is") != -1:
          # logger.info("inside try if",x)s nj;p-
          print("inside try if",x)
          #message_tte = loop.run_until_complete(process(current_agent_tte, x['text'],user))
          # message_training = loop.run_until_complete(process(current_agent_training,x['text'],user))
          message_leave_mgmt = loop.run_until_complete(process(current_agent_leave_mgmt,x['text'],user))
          message_leave_approval = loop.run_until_complete(process(current_agent_leave_approval,x['text'],user))
          message_profile_info = loop.run_until_complete(process(current_agent_profile_info,x['text'],user))
          print("#######################################################################################")
          # logger.info("#######################################################################################")
          
          
          # logger.info("########################################################################################")
          #print("########################################################################################")
        
        elif x['text'].find("Successfully logged out!")!=-1:
          # logger.info("inside try elif",x)
          print("inside try elif",x)
          message_tte = loop.run_until_complete(process(current_agent_tte, "/restart",user))
          # message_training = loop.run_until_complete(process(current_agent_training,"/restart",user))
          message_login_logout= loop.run_until_complete(process(current_agent_login_logout, "logout",user))
          message_leave_mgmt = loop.run_until_complete(process(current_agent_leave_mgmt,"/restart",user))
          message_profile_info = loop.run_until_complete(process(current_agent_profile_info,"/restart",user))
          sent_msg.append(x)
        
        else:
          # logger.info("inside try else")
          print("inside try else")
          sent_msg.append(x)
          
    except:
      
      # logger.info("inside except")
      print("inside except")
      sent_msg = message_login_logout
    
    message = sent_msg
  
  elif state == "switch_to_desired_model":
    print(f"state is {state}")
    
  else:
    
    message = {"text":"I could not understand could you please repeat?."}
    
  print("*******************************************",message,"**********************************************************")
  # logger.info("*******************************************",message,"**********************************************************")
  message= json.dumps(message)
  return message

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=True)
 # app.run(host='0.0.0.0', port=5000,ssl_context=("bundle_latest.crt", "wildcard_omfysgroup_com.key"),debug=True, use_reloader=True)

# payload: 
# {
# "message": "Hi",
# "sender": "user",
# "agent": "agent_one"
# }

# [{
# "recipient_id": "default",
# "text": "Hi, I am your virtual assistant\n\n* How can I help you?"
# }]
