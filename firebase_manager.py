import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from datetime import datetime
import uuid

COLLECTION_NAME = 'map1'


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
    edges = firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .document('edges') \
        .get().to_dict()

    clean_edges = []

    for e in edges:
        clean_edges.append(edges[e])

    return clean_edges


def add_edge(node1, node2):
    firebase_admin.firestore.client(app=None) \
        .collection(COLLECTION_NAME) \
        .document('edges') \
        .update({str(uuid.uuid4()): [node1, node2]})
