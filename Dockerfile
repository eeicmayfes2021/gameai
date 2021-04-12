FROM python:3.7
WORKDIR /usr/src/app

# ENV PYTHONUNBUFFERED 1
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --upgrade cython

COPY . .
RUN python setup.py build_ext --inplace
