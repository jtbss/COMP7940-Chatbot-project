FROM python:3.9
COPY chatbot.py .
COPY requirements.txt .
COPY config.ini .
RUN pip install pip update
RUN pip install -r requirements.txt
CMD [ "python", "chatbot.py" ]
