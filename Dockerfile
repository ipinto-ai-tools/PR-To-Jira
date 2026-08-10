FROM registry.access.redhat.com/ubi9/python-312:latest

COPY requirements.txt /opt/app-root/src/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/app-root/src/
RUN pip install --no-cache-dir .

ENTRYPOINT ["pr-jira"]
