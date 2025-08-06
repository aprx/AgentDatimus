FROM python:3.12-bookworm

WORKDIR /usr/app/
RUN pip install -U pip

COPY pyproject.toml README.md /usr/app/
COPY src/ /usr/app/src/

RUN pip install .

CMD ["agentdatimus", "-c", "conf/agent.ini-sample"]