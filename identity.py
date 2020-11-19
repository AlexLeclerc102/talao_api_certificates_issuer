import json

def add_identity(username, name, lastname, did):
    identity_list = []
    with open('./identity_list.json', 'r') as json_file:
        data = json.load(json_file)
        for id in data:
            if id['username'] != username:
                identity_list.append(id)

    if bool:
        identity_list.append({"username" : username, "name" : name, "lastname": lastname, "did" : did})

    with open('./identity_list.json', 'w') as outfile:
        json.dump(identity_list, outfile)

    print("New identity added")
    return True

def get_list():
    identity_list = []
    with open('./identity_list.json', 'r') as json_file:
        data = json.load(json_file)
        for id in data:
            identity_list.append(id)
    return identity_list
# def search_user(session):
#     username = session['username']
#     name = session['name']
#     profillist = []
#     with open('./static/username.json', 'r') as json_file:
#         data = json.load(json_file)
#         for id in data:
#             if id['username'] == username:
#                 return True
#     return False
