from flask import *
import sys
sys.path.insert(0, '..')

from functions.blockchain_functions import *
from functions.rabbitmq_functions import rabbit_check_health
# Route Flask pour obtenir santé du node
def health_function():
    #return "test"
    rabbit_health=rabbit_check_health()
    try:
        chain = load_blockchain_data()
        public_keys = load_verified_public_keys()
        merkle_root = calculate_merkle_root_from_json(chain)
        return jsonify({'blockchain_status': 'Working as expected',"rabbitmq_status": rabbit_health[0],"rabbitmq_details": rabbit_health[1],"merkle_root": str(merkle_root)}), 200
    except Exception as error:
        print("[!] Impossible de récuperer les données nécessaire")
        return jsonify({'blockchain_status': f'Error {error}',"rabbitmq_status": rabbit_health[0],"rabbitmq_details": rabbit_health[1]}), 500