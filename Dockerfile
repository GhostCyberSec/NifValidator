FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN useradd -m user
USER user
WORKDIR /home/user
ENV PATH="/home/user/.local/bin:${PATH}"

COPY --chown=user:user requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=user:user . .
EXPOSE 9046

CMD ["python", "app.py"]