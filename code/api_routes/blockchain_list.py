from flask import request,jsonify
import sys
sys.path.insert(0, '..')

from functions import *

# Route Flask pour obtenir la liste des blocs de la blockchain
def blockchain_list():
    data=request
    chain = load_blockchain_data()
    return jsonify(chain)