FROM python:3.8-slim-buster

RUN echo "now image building..."

RUN apt update && apt upgrade -y
RUN apt install git -y

RUN pip install discord.py
RUN pip install python-dotenv

RUN git clone https://github.com/toy101/dicord-bot-py-template.git
RUN rm -rf dicord-bot-py-template/.git
RUN rm -rf dicord-bot-py-template/README.md
RUN mkdir /workspace
RUN mv dicord-bot-py-template /workspace

CMD [ "/bin/bash" ]