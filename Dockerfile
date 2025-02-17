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

ENV ENV=PROD
ENV SECRET_KEY=X
ENV SQLALCHEMY_DATABASE_URI=X
ENV SEND_GRID_API_KEY=X
ENV TWILIO_API_KEY=X
ENV TWILIO_API_SECRET=X
ENV TWILIO_ACCOUNT_SID=X
ENV TWILIO_VERIFY_SERVICE_SID=X 

ENV PATH="/GasMoney/venv/bin:$PATH"
CMD [ "gunicorn", "-w", "1", "gasmoney:app" ]
