from flask import request
import sys
sys.path.insert(0, '..')

from functions import *

# Route Flask pour obtenir la liste des clés publiques
def keys_list():
    data=request
    return load_verified_public_keys()