import sys
sys.path.insert(0, '..')

from functions import *
from functions.blockchain_functions import *
# Route Flask pour obtenir la liste des clés publiques
async def keys_list():
    return load_verified_public_keys()