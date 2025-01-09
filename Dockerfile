FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

RUN uv venv /app/kdhs_env

ENV PATH="/app/kdhs_env/bin:$PATH"
ENV GRADIO_SERVER_NAME="0.0.0.0"

RUN uv pip install crewai
RUN uv pip install 'crewai[tools]'
