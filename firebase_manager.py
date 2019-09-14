import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth
from datetime import datetime
import uuid

def get_nodes():
    thing = firebase_admin.firestore.client(app=None) \
        .collection('map') \
        .document('nodes') \
        .get().to_dict()

    """
    ok dis return this shit
    
    {
        "index shit of the node": [
            x, y
        }, ...
    }
    
    """

def get_edges():
    edges = firebase_admin.firestore.client(app=None) \
        .collection('map') \
        .document('edges') \
        .get().to_dict()

    clean_edges = []

    for e in edges:
        clean_edges.append(edges[e])

    return clean_edges

def add_node(name, x, y):
    firebase_admin.firestore.client(app=None) \
        .collection('map') \
        .document('nodes') \
        .update({name: [x, y]})

def add_edge(node1, node2):
    firebase_admin.firestore.client(app=None) \
        .collection('map') \
        .document('edges') \
        .update({str(uuid.uuid4()): [node1, node2]})

def add_node_data(name, data):

    """
    :param name: dis is da node name
    :param data: dis is da dict with da {macaddress: db and other stuff}
    :return:
    """

    firebase_admin.firestore.client(app=None) \
        .collection('signals') \
        .document(str(name)) \
        .set(data)

def get_node_data():
    node_data = firebase_admin.firestore.client(app=None) \
        .collection('signals') \
        .get()

    clean_node_data = {}

    for i in node_data:
        clean_node_data[i.id] = i.to_dict()

    return clean_node_data