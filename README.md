
# Talao.co API Certificates issuer Demo v0.1

This is a demo for talao.co's API

This demo shows how to create an identity, issue certificates for this identity and get access to those certificates. When creating an identity with the API you automatically will be added to it's partner and referent list. This allows you to issue certificates without having to ask the user to connect to talao.co and add you himself.

## Documentation
https://talao.readthedocs.io/en/latest/api/
## Installation

Clone this repository : 

```bash
git clone https://github.com/AlexLeclerc102/talao_api_certificates_issuer.git
```

## Requirements

[Flask](https://flask.palletsprojects.com/en/1.1.x/) : `$ pip install Flask`

jwt : `pip install Flask-JWT`

## Usage

Launch using python

```bash
python main.py
```

By default this app will launch on 127.0.0.1:5000 you can change it at the bottom of main.py
