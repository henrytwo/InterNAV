import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from datetime import datetime
import uuid

COLLECTION_NAME = 'map'


def generate_id(p):
    return ''.join([str(x).replace('.', '|') for x in p])


def set_nodes(nodes):
    firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .document('nodes') \
        .set(nodes)


def add_node_data(name, data):
    """
    :param name: dis is da node name
    :param data: dis is da dict with da {macaddress: db and other stuff}
    :return:
    """

    firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .document('nodes') \
        .update({
        str(name): {
            'aps': data
        }
    })


def get_nodes():
    return firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .document('nodes') \
        .get().to_dict()

    """
    ok dis return this shit
    
    {
        "index shit of the node": {
            "location": [x, y],
            "aps" : {
                "<mac>" : db,
                ....
            }
        }, ...
    }
    
    """


def get_edges():
    data = firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .document('edges')\
        .get().to_dict()

    good_data = []

    if data:
        for i in data:
            good_data.append(data[i])

    return good_data

def set_edge(edges):
    for e in edges:
        firebase_admin.firestore.client(app=None) \
            .collection(COLLECTION_NAME) \
            .document('edges')\
            .update({generate_id(e): e})
