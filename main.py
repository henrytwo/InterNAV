import wifi_manager
import firebase_manager
import calculationshit
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from datetime import datetime

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)

calculationshit.Initialize(firebase_manager.get_nodes(), None, None, firebase_manager.get_edges())

while True:

    shit = wifi_manager.dump_aps('wlp0s20f3')

    print(str(datetime.now()), calculationshit.findLocation(shit))
