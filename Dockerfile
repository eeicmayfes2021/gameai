FROM python:3.7
WORKDIR /usr/src/app

ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src src
RUN cd src && python setup.py build_ext --inplace

CMD bash