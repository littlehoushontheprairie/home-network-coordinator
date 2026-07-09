FROM python:trixie

WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY src/requirements.txt .
COPY src/IpUpdateOrchestrator.py .
COPY src/entities ./entities
COPY src/clients ./clients
COPY src/helpers ./helpers

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "IpUpdateOrchestrator.py"]
