FROM python:3.10
RUN pip3 install requests
RUN pip3 install boto3
COPY check.py check.py
CMD ["python3", "/check.py"]

