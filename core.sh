

cd /home/ubuntu/ALAN_2

. venv/bin/activate

rasa run -m models --enable-api --cors "*" -p 5005
