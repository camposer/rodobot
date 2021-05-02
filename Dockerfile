FROM continuumio/miniconda3

# Install os requirements
RUN apt update
RUN apt install -y build-essential

# Configure TA Lib
COPY config config
RUN bash config/ta-lib.sh

# Install requirements
COPY requirements requirements
RUN pip install \
      --no-cache-dir \
      --disable-pip-version-check \
      -r requirements/common.txt

# TODO Copy app resources under app folder
# TODO Create user and use it
