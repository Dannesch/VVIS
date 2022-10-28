FROM mcr.microsoft.com/playwright/python:v1.25.0-focal

LABEL Maintainer="dannesch"
WORKDIR /home
COPY ./templates/index.html ./templates/index.html
COPY ./VVIS.py ./VVIS.py
COPY ./requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
CMD ["python", "-u", "VVIS.py"]