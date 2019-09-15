import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)

COLLECTION_NAME = 'map'

stuff = firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .get()

out = {}

for i in stuff:
    out[i.id] = i.to_dict()

with open('dbdump.json', 'w') as file:
    json.dump(out, file)