# Talao.co API Demo v0.1
# Usecase : Certificates issuer
# This demo shows how to create an identity, issue certificates for this identity and get access to those certificates.
# When creating an identity with the API you automatically will be added to it's partner and referent list.
# This allows you to issue certificates without having to ask the user to connect to talao.co and add you himself.

from urllib.parse import urlencode
import requests
from flask import Flask, redirect, request, render_template_string, session, send_from_directory
from flask import redirect, render_template
import json
import os
import random
import jwt

import identity

app = Flask(__name__)

# Get your own credentials from talao.co !
with open('./client_credentials.json') as c:
    credentials = json.load(c)[0]

client_id = credentials["id"]
client_secret = credentials["secret"]

# Usefull url
talao_url = " https://talao.co"
# Talao as an OAuth2 Identity Provider
talao_url_authorize = talao_url + '/api/v1/authorize'
talao_url_token = talao_url + '/api/v1/oauth/token'
talao_url_userinfo = talao_url + '/api/v1/user_info'
talao_url_logout = talao_url + '/api/v1/oauth_logout'

@app.route('/', methods=['GET'])
def home():
    # For this demo identities are kept in a json file
    identity_list = identity.get_list()
    return render_template("home.html", identity_list = identity_list)

@app.route('/create_identity', methods=['GET', 'POST'])
def create_identity():
    if request.method == 'GET' :
        return render_template("create_identity.html")
    if request.method == 'POST' :
        data = {
            'grant_type': 'client_credentials',
            'redirect_uri': "",
            'client_id': client_id,
            'client_secret': client_secret,
            'code': "",
            'scope' : 'client:create:identity' # You will need to have this scope allowed by talao.co
        }
        # First ask for a token:
        response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
        print('step 2 : request for a token sent')
        if response.status_code == 200 :
            token_data = response.json()
            print('step 3 : request sent')
            #T hen use it to request the creation of a new identity:
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            # Get the data you need:
            name , lastname, email = request.form['name'], request.form['lastname'], request.form['email']
            send_email = False if request.form.getlist('send_email') == [] else True
            data = {'firstname' : name, 'lastname' : lastname, 'email' : email, "send_email" : send_email}
            # If send_email is True we will send an email to the user to invite him on our platform (talao.co)
            # where he will have acces to all our services
            # Send the request:
            response = requests.post(talao_url + '/api/v1/create_person_identity', data=json.dumps(data), headers=headers)
            response = response.json()
            # Save the username and the did (Decentralized IDentifier) you will need it later!
            identity.add_identity(response["username"],request.form['name'], request.form['lastname'],response['did'])
            return render_template('identity_created.html',
                                    name = name, lastname = lastname,
                                    did = response['did'], username = response['username'])
        return 'Request for token refused'

@app.route('/get_certificate_list', methods=['POST'])
def get_certificate_list():
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : ''
    }
    # First ask for a token:
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : request for a token sent')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 : request sent')
        # Then use it to request the certificate list
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        # You will need to have the did (Decentralized IDentifier) and the type of certificate
        data = {'did' : request.args['did'], 'certificate_type' : request.form['type']}
        response = requests.post(talao_url + '/api/v1/get_certificate_list', data=json.dumps(data), headers=headers)
        response_json = response.json()
        certificate_list = []
        # the response is a list of certificate id you will need to request them if you need the data
        for id in response_json['certificate_list']:
            # get_certificate is used to request the data in the certificate using the certificate id
            certificate = get_certificate(id)
            if certificate == None:
                return "Error during the request of certificate with id : " + id
            else:
                certificate_list.append(certificate)
        return render_template("get_certificate_list.html", certificate_list = certificate_list)
    return 'Request for a token refused'

@app.route('/user_list', methods=['GET'])
def user_list():
    if request.method == 'GET' :
        identity_list = identity.get_list()
        return render_template("user_list.html", identity_list = identity_list)

def get_certificate(id):
    data = {
        'grant_type': 'client_credentials',
        'redirect_uri': "",
        'client_id': client_id,
        'client_secret': client_secret,
        'code': "",
        'scope' : ''
    }
    # First ask for a token:
    response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
    print('step 2 : request for a token sent')
    if response.status_code == 200 :
        token_data = response.json()
        print('step 3 : request sent')
        # Then use it to request the certificate
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
        data = {'certificate_id' : id}
        response = requests.post(talao_url + '/api/v1/get_certificate', data=json.dumps(data), headers=headers)
        return response.json()
    return None

@app.route('/issue_certificate', methods=['POST'])
def issue_certificate():
    if request.form['type'] == "experience":
        return redirect('/issue_experience?did=' + request.args['did'])
    else:
        return "Not implemented"

@app.route('/issue_experience', methods=['GET', 'POST'])
def issue_experience():
    if request.method == 'GET' :
        did = request.args['did']
        identity_list = identity.get_list()
        name, lastname = '', ''
        for id in identity_list:
            if id['did'] == did:
                name, lastname = id['name'], id['lastname']
                break
        return render_template("issue_experience.html", did = did, name = name, lastname = lastname)
    if request.method == 'POST' :
        data = {
            'grant_type': 'client_credentials',
            'redirect_uri': "",
            'client_id': client_id,
            'client_secret': client_secret,
            'code': '',
            'scope' : 'client:issue:experience'
        }
        # First ask for a token:
        response = requests.post(talao_url_token, data=data, auth=(client_id, client_secret))
        print('step 1 : request for a token sent')
        if response.status_code == 200 :
            token_data = response.json()
            print('step 2 request sent sur final endpoint ')
            # Then use it to issue a certificate
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % token_data['access_token']}
            # The info needed in the certificate depends on the certificate type
            certificate = {
    	    "title" : request.form['title'],
    	    "description" : request.form['description'],
    	    "start_date" : request.form['start_date'],
    	    "end_date" : request.form['end_date'],
    	    "skills" : ["Python", "Flask", "Oauth 2.0", "IODC"],
    	    "score_recommendation" : request.form['score_recommendation'],
    	    "score_delivery" : request.form['score_delivery'],
    	    "score_schedule" : request.form['score_schedule'],
    	    "score_communication" : request.form['score_communication'],
    	    }
            # You will need to have de the user's did (Decentralized IDentifier)
            data = {'did' : request.form['did'], 'certificate' : certificate}
            response = requests.post(talao_url + '/api/v1/issue_experience', data=json.dumps(data), headers=headers)
            return render_template('/certificate_issued.html')
        print('Request for a token refused')
        print('response : ', response.__dict__)
        return 'Request for a token refused'

if __name__ == '__main__':
    app.run(host = "127.0.0.1", port= 5000, debug = True)
