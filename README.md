# Identfy-Backend

## 1. Services

### Backend

This project provides an Enterprise wallet and an Issuer to credential issuance in different networks.

## 2. Requirements

- Python 3.12
- You can install all the requirements with:

```bash
pip install -r requirements.txt
or
pip3 install -r requirements.txt
```

## 3. Deployment

To deploy this repo locally, you need to follow these steps

### step-0

You need firstly to pay attention to continue config vars

```bash
BACKEND_DOMAIN: "https://example.com" # URL of deployed instance
DID: "did:ebsi:zzpYmwyZhHEyDUgKKXmEjeW" # EBSI Did
VC_SERVICE_URL: "https://vc_service_example.com" # URL of Verifiable Credentials Service
DEVELOPER_MOCKUP_ENTITIES: True # If you want to check it, without real data active.
ENTITY_URL: "https://external-data.com" # URL of the Authentic Source. Needed for the required integration
ENTITY_API_KEY: # Api Key to include in each request to the backend with the user data
EBSI_DIDR_URL: "https://api-pilot.ebsi.eu/did-registry/v5/identifiers" # URL of EBSI DID Registry
EBSI_TIR_URL: "https://api-pilot.ebsi.eu/trusted-issuers-registry/v5/issuers" # URL of EBSI TI Registry
```

### step-1

The backend runs in Docker. We need to have docker (docker-engine) and docker-compose installed

To build Docker images (remember that you have to do this everytime you add a new dependency to Pipfile too)

```bash
docker compose build
```

### step-2

The first time we start the project locally it will be necessary to migrate the data and create a superuser

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

### step-3

Start everything (redis, postgress, server, celery and rest of things written in docker-compose.yml)

```bash
docker compose up --build
```
