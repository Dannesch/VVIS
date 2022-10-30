FROM mcr.microsoft.com/playwright/python:v1.25.0-focal

LABEL Maintainer="dannesch"
WORKDIR /home
COPY ./templates/index.html ./templates/index.html
COPY ./VVIS.py ./VVIS.py
COPY ./requirements_api.txt ./requirements.txt

RUN python -m pip install pip --upgrade
RUN python -m pip install -r requirements.txt
CMD ["python", "-u", "-m", "uvicorn", "VVIS:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]