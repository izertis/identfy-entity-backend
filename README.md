<p align="center">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="./docs/img/identfy-logo-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="./docs/img/identfy-logo-light.svg">
      <img alt="identfy" src="./docs/img/identfy.png" width="350" style="max-width: 100%;">
    </picture>
</p>

<p align="center">
  <h4>
    An all-in-one solution to take control of your digital identity
  </h4>
</p>

<br/>

**[identfy](https://github.com/izertis/identfy)** is a combination of various products that enable building user-centric solutions.

# identfy Entity backend

**identfy Entity backend** is an administration platform to manage VC. The identfy Entity backend does not implement any logic related to VC or identity management. This backend is more the core that connects and manages the communication with others, as well as exposing itself to the network.


## Table of content:

- [How to start using it](#usage)
- [Development guide](#development-guide)
- [License](#license)
- [Trademark](#trademark)


## Usage

The identfy Entity backend can be run in Docker. We need to have docker (docker-engine) and docker-compose installed

### Configuration

Configure the following environment vars:

```bash
# Django envs
ALLOWED_HOSTS = ""
CSRF_TRUSTED_ORIGINS = ""
CORS_ALLOWED_ORIGINS = ""

# OpenID Service
CREDENTIALS_URL = "" # identfy-service

# Own Data
DID = ""
PRIVATE_KEY = "" # Private Key in JWK format and crv P-256
PUBLIC_KEY = "" # Public Key in JWK format and crv P-256
EXTERNAL_URL = "" # To retrieve data to complete the Credential
EXTERNAL_API_KEY = ""
```

### Build

To build Docker images (remember that you have to do this everytime you add a new dependency to Pipfile too)

```bash
docker compose build
```

### User configuration

The first time we start the project locally it will be necessary to migrate the data and create a superuser

```bash
docker compose run --rm backend python manage.py migrate
docker compose run --rm backend python manage.py createsuperuser
```

### Start up

Start everything (redis, postgress, server, celery and rest of things written in docker-compose.yml)

```bash
docker compose up --build
```


## Development guide

If you are interested on testing and building it by yourself or you would like to contribute, you can find here the [development guide](./docs/GETTING_STARTED.md)


## Help and Documentation

- *Contact:* send an email to blockchain@izertis.com
- [Github discussions](https://github.com/izertis/identfy-entity-backend/discussions) - Help and general questions about this project


# License
This software is dual-licensed; you can choose between the terms of the [Affero GNU General Public License version 3 (AGPL-3.0)](./LICENSES/agpl-3.0.txt) or a [commercial license](./LICENSES/commercial.txt). Look at [LICENSE](./LICENSE.md) file for more information.


# Trademark
**identfy** and its logo are registered trademarks of [Izertis](https://www.izertis.com)
