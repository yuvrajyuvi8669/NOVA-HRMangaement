# import spacy
from dateutil.parser import parse
import dateparser
import parsedatetime
import datetime
import re
import requests
import json
import timedelta
from datetime import date, timedelta
import calendar
import duckling
from duckling import DucklingWrapper, Duckling


# data = {'errorCode': 109, 'errorMsg': 'Alert', 'errorDesc': "You don't have authorities to approve leaves!"}
# print(data['errorDesc'])

# x = datetime.datetime.now()

# print(x)

# x = datetime.datetime.now()

# print(x.year)
# print(x.strftime("%A"))

# x = datetime.datetime(2020, 5, 17)

# print(x)

# x = datetime.datetime(2018, 6, 1)

# print(x.strftime("%B"))

# x = datetime.datetime(2018, 6, 1)

# print(x.strftime("%x"))

# x = datetime.datetime(2018, 6, 1)

# print(x.strftime("%d"))

# x = datetime.datetime(2018, 6, 1)

# print(x.strftime("%b"))

# x = datetime.datetime(2018, 6, 1)

# print(x.strftime("%y"))

# x = datetime.datetime(2018, 6, 1)

# print(x.strftime("%Y %b %d"))

# data = '2020-05-17 00:00:00'
# print(datetime.datetime.strptime(data,"%Y-%m-%d %H:%M:%S"))
# data = (datetime.datetime.strptime(data,"%Y-%m-%d %H:%M:%S"))
# print(data.strftime("%Y %b %d"))

# value = "81879 approve"
# print(value.__contains__('approve'))
# print(value.split(" "))
# v = value.split(" ")
# print(v.__contains__('approve'))
# print(type(int(v[0])))

# value = ["81879 approve"]
# print(value[0])
# list1 = [1,22,3,3,3,3,4,55]
# if 3 in list1:
#     print('yes')
#     list1.remove(3)
#     print(list1)
# print(list1)
# print(list1.remove(3))
# print(len(list1))
# tu = (1,2,2,3,3)
# print(tu)
# set1 ={1,2,2,2,3,4,4,5}
# print(set1)

# value = "oMi-1071"
# u=value.upper()
# print(u.rfind('HOMI'))
# print(value,list1)

# value ="44956 sOMI-1055"
# print(value.split(' s'))
# lr_id = value.split('s')[0] 
# emp_code1 = (value.split('s')[1])
# print(lr_id)
# print(emp_code1)

# value = "s44959 sOMI-1051"
# print(value.split(' s'))
# lr_id = (value.split(' s')[0]).split('s')[1] 
# emp_code1 = (value.split(' s')[1])
# print("lr_id",lr_id)
# print("emp_code",emp_code1)

# value = "44959 OMI-1051"
# print(value.split(' '))
# lr_id = (value.split(' ')[0]) 
# emp_code1 = (value.split(' ')[1])
# print("lr_id",lr_id)
# print("emp_code",emp_code1)

# dict1= {12345:'OMI-1051'}
# print(dict1[12345])

# nlp1 = spacy.load('en')
# doc = nlp1(u"tell me details of pawar")

# ent = [(x.text,x.label_) for x in doc.ents]
# print(ent)

# response = requests.get(
# '{}/leaveRequestDetails?emp_id={}&lr_id={}'.format("http://43.231.254.81/MINDS_CONNECT",43,43323))


# data = response.json()
# print(len(data))
# print(data[0]['leave_type'])



# arr = {}
# arr = {'a':[1,2,34,8],'b':[9,8,7,6,5]}
# print(True in [34 in arr[key] for key in arr.keys()])

date1 = {'start_date': '2020-06-01', 'end_date': '2020-07-01'}
# arr = {}
# arr1 = []
# print(date1['start_date'])
# arr = {'a':['2020-06-23','2020-06-24',34,8],'b':['2020-06-20','2020-06-22',7,6,5]}
# print([arr1.extend(arr[key]) for key in arr.keys()])
# print(arr1)
# try:
#     [print(value) for value in arr1 if datetime.datetime.strptime(str(value),'%Y-%m-%d')]
# except ValueError:
#     pass

# if '2020-06-01' is '2020-06-01':
#     print("true")
#
print((datetime.datetime.now()).strftime("%X"))
print((datetime.datetime.now()).strftime("%Y-%m-%d"))

# value = input("enter\n")
# print(dateparser.parse(value).strftime("%d/%m/%Y"))
# print(dateparser.parse("day after tomorrow"))
# print(dateparser.parse("on 22nd feb"))
# print(dateparser.parse("feb 23"))
# print(dateparser.parse("on august 23rd"))

#
# #
cal = parsedatetime.Calendar()
# var1 = input("date details\n")
# print(((cal.nlp(var1))[0][0]).strftime("%Y-%m-%d"))
# print(cal.nlp(var1))
# var3 = input("date details\n")
# print(((cal.nlp(var3))[0][0]).strftime("%Y-%m-%d"))
# print(cal.nlp(var3))
# var2 = input("date details")
# print(((cal.nlp(var2))[0][0]).strftime("%Y-%m-%d"))
# print(cal.nlp(var2))

date1 = ['next month', {'start_date': '2020-08-01', 'end_date': '2020-09-01'}]
print(date1[1]["start_date"])

# d =  DucklingWrapper()
# d1 = input("date details\n")
# print(d.parse(d1))
# d2 = input("date details\n")
# print(d.parse_duration(d2))
# d3 = input("date details\n")
# print(d.parse_time(d2))
# d = DucklingWrapper()
# d1 = input("date details\n")
# print(d.parse(d1))
# d2 = input("date details\n")
# print(d.parse_duration(d2))
# d3 = input("date details\n")
# print(d.parse_time(d2))

# print(cal.nlp("day after tomorrow"))
# print(cal.nlp("on 22nd feb"))
# print(cal.nlp("feb 23"))
# print(((cal.nlp("on august 23rd"))[0][0]).strftime("%Y-%m-%d"))

# ## string comparsion with percentage match
# string1 = "Collection of money"
# string2 = "collect money"
# percent_list = []
# count=0
# str1list = []
# [[str1list.append(char) for char in word ]for word in string1.lower().split()]
# str2list = []
# [[str2list.append(char) for char in word ]for word in string2.lower().split()]
# if len(string1) > len(string2):
#    for ele1 in str1list:
#
#         for ele2 in str2list:
#             if ele1 == ele2:
#                 count = count + 1
#                 break
#
#
#             else:
#                 continue
#    print(count)
#    print(len(string1))
#    percent = (count / len(string1))
#    print(percent)
#    percent_list.append(percent)
#
# else:
#     for ele2 in str2list:
#         for ele1 in str1list:
#
#             if ele1 == ele2:
#                 count = count + 1
#                 print(count)
#             else:
#                 continue
#     print(count)
#     print(len(string2))
#     percent = (count/ len(string2))
#     print(percent)
#     percent_list.append(percent)
# list1 = [45,6.7,9.6]
# print(max(list1))

# value = re.findall("task[\s.\w+]+","task my name")
# print(value)
# response = requests.get('{}/downloadPaySlipApi?emp_code={}'.format("http://43.231.254.81/MINDSCONNECT", "OMI-1036"))
# print(response)
# data1 = response.json()
# global month
# month = []
# global month2
# month2 = []
# for payslip in range(0,len(data1)):
# 				month.append("{}".format(datetime.datetime.strptime(data1[payslip]['last_update_date'],
# 										  "%b %d, %Y %H:%M:%S %p").strftime("%b %Y")))
# print("month",month)

# for payslip in range(0,len(data1)):
# 	payslip_date = (datetime.datetime.strptime(data1[payslip]['last_update_date'],
# 										  "%b %d, %Y %H:%M:%S %p").strftime("%b %Y"))
# 	payslip_start_month = (datetime.datetime.strptime(payslip_date, "%b %Y").month)
# 	payslip_start_year = (datetime.datetime.strptime(payslip_date, "%b %Y").year)
# 	payslip_start_day = (datetime.datetime.strptime(payslip_date, "%b %Y").day)
# 	payslip_days_in_month = calendar.monthrange(payslip_start_year, payslip_start_month)[1]
# 	print(payslip_days_in_month,"days")
# 	payslip_user_date = date(payslip_start_year, payslip_start_month, payslip_start_day)
# 	payslip_date2 = payslip_user_date - timedelta(days=payslip_days_in_month-1)
# 	payslip_user_month = datetime.datetime.strptime(str(payslip_date2), "%Y-%m-%d").strftime("%b %Y")
# 	month.append("{}".format(payslip_user_month))
# print("month2",month)

text = input("Enter date")
print((cal.nlp(text)))
print(((cal.nlp(text))[0][0]).strftime("%d/%m/%Y"))
s_date_training = ((cal.nlp("1st aug"))[0][0]).strftime("%d/%m/%Y")
e_date_training = ((cal.nlp("31st aug"))[0][0]).strftime("%d/%m/%Y")
print(e_date_training)
if s_date_training <= ((cal.nlp("4th aug"))[0][0]).strftime("%d/%m/%Y") >= e_date_training:
    print("today is between given date")
else:
    print("today is not between given date")

