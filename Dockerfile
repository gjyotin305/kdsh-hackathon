FROM python:3.11-slim

WORKDIR /app

COPY agent.py /app/agent.py
COPY main.py /app/main.py
COPY constants.py /app/constants.py
COPY extraction.py /app/extraction.py
COPY task_1_agent.py /app/task_1_agent.py

RUN pip install uv

RUN uv venv /app/kdhs_env

ENV PATH="/app/kdhs_env/bin:$PATH"

RUN uv pip install  pypdf openai pypdf asyncio uvicorn fastapi

CMD ["python", "main.py"]