# moca-server

This is the server component of MOCA, which includes the client connector and the service connector.

## Requirements

- Python 3.6+

## Setup

These instructions are for a linux installation. You may have to alter these instructions yourself for Windows, or use the Windows Subsystem for Linux (WSL).

1. Create a virtual environment: `python -m venv venv` (this is optional, but highly recommended)
2. Activate venv: `source venv/bin/activate`
3. Install dev dependencies: `pip install -r requirements-dev.txt`

```
(venv) $ python
>>> from server import db
>>> db.create_all()
>>> exit()
```


## Development Guides

Here you can find a list of snippets or examples which are useful for developing on the server.

### Generate code
Just run `make`. You can also clean the generated files by running `make clean`.

## Architecture

Client --c o-- [ClientConnector] Server --c o-- [ServiceConnector] Service


Client SendMessage --> Server --> SendMessage to Service
Client SubMsg --> Server SubMsg --> Service
Client Login --> Server Login --> Service

## Official Services

| Service  | UUID                                 | Default Port |
|----------|--------------------------------------|--------------|
| Telegram | 0aed2fc7-29b3-4193-9a66-393d325c7846 | 50061        |
| WhatsApp | 2f307683-0e2d-42c8-9498-b82fa0989bfc | 50062        |
