


@echo off

cd /d C:\NEW\Chatbot\all skill\ALLFAQ\actions

rem activate virtual env in cmd
call  ..\..\..\nova_da\Scripts\activate

rem run command in cmd after the activation of virtualenv
rasa run actions -p 5012

