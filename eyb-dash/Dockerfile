FROM python:3.10.9
ENV DASH_DEBUG_MODE True

COPY ../assets /assets/
COPY application.py /application.py
COPY requirements.txt /requirements.txt

WORKDIR /

RUN set -ex && \
    pip install -r requirements.txt
EXPOSE 8080
CMD ["python", "application.py"]