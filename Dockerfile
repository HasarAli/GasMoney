# syntax=docker/dockerfile:1

FROM python:3-slim AS builder

WORKDIR /GasMoney

RUN python3 -m venv venv
ENV PATH="/GasMoney/venv/bin:$PATH"

COPY . .
RUN pip install -e .


FROM python:3-slim

COPY --from=builder /GasMoney/venv /GasMoney/venv
COPY --from=builder /GasMoney/gasmoney /GasMoney/gasmoney

ENV FLASK_APP=gasmoney
ENV FLASK_ENV=development

# Make sure we use the virtualenv:
ENV PATH="/GasMoney/venv/bin:$PATH"
CMD [ "flask", "run", "--host=0.0.0.0" ]