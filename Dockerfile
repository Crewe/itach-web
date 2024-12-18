FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

ADD . /app

RUN uv venv --no-config # ignore .python-version because uv will throw an error
ENV PATH="/app/.venv/bin:$PATH"
RUN uv pip install .

ENTRYPOINT []

CMD ["itachweb"]
