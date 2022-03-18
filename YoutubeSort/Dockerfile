FROM python:3.10.2
WORKDIR /code/YoutubeSort
ENV PYTHONUNBUFFERED 1
RUN apt-get update
RUN apt-get install libc-dev musl-dev vim -y
# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /code/

# System deps:
RUN pip install --upgrade pip
RUN pip install poetry

# Project initialization:
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi


# Creating folders, and files for a project:
COPY . /code

