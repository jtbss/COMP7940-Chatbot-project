FROM python
COPY chatbot.py .
COPY requirements.txt .
ENV TELEGRAM_ACCESS_TOKEN 6160653421:AAHGzKhMkgInIyZ0ES2hHDDTAs2ldiZ-yi0 
ENV REDIS_HOST redis-13094.c282.east-us-mz.azure.cloud.redislabs.com 
ENV REDIS_PASSWORD s7JHCuaUPxQ3ROZQDGMBS2ZM0llfYZ9n
ENV REDIS_PORT 13094
RUN pip install pip update
RUN pip install -r requirements.txt
CMD python chatbot.py
