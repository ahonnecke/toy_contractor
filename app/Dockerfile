FROM python:3.12-slim
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml /app/
RUN uv sync --frozen
COPY contractgen_api /app/contractgen_api
ENV PATH="/app/.venv/bin:${PATH}"
CMD ["uvicorn", "contractgen_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
