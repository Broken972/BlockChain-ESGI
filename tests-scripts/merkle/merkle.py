import hashlib
import json

def hash_block(block):
    block_string = json.dumps(block, sort_keys=True)
    return hashlib.sha256(block_string.encode()).hexdigest()

class MerkleTree:
    def __init__(self, hashes):
        self.leaves = hashes
        self.levels = []
        self.build_tree()

    def build_tree(self):
        current_level = self.leaves
        while len(current_level) > 1:
            self.levels.append(current_level)
            next_level = []
            for i in range(0, len(current_level), 2):
                if i + 1 < len(current_level):
                    combined = current_level[i] + current_level[i + 1]
                else:
                    combined = current_level[i] + current_level[i]
                next_level.append(hashlib.sha256(combined.encode()).hexdigest())
            current_level = next_level
        self.levels.append(current_level)
        self.root = current_level[0]


blockchain = [
    {
        "block_hash": "39331a6a2ea1cf31a5014b2a7c9e8dfad82df0b0666e81ce04cf8173cc5aed3e",
        "previous_block_hash": "0",
        "transaction_list": ["Genesis Block"]
    },
    {
        "block_hash": "e38a354a0de0abc43e3ceee1521e68d83adef1cef3eef467c1863d718b669ff2",
        "previous_block_hash": "39331a6a2ea1cf31a5014b2a7c9e8dfad82df0b0666e81ce04cf8173cc5aed3e",
        "owner": "AcerlorMittal DSF",
        "package_id": "39829829829",
        "time": "2018-11-20|12:00:00",
        "status": "En cours",
        "produit": "Tolle",
        "current_place": "Stock Centrale (AcerlorMittal)",
        "destination": "Client",
        "packages_total_number": "100",
        "packages_total_weight": "100",
        "product_detail": [
            {
                "index": "1",
                "weight": "1",
                "origin_place": "Usine-France"
            },
            {
                "index": "2",
                "weight": "1",
                "origin_place": "Usine-Chine"
            }
        ]
    },
    {
        "block_hash": "5f5bb823ac49eb212cc36b4348785b779ee1459e8b3ff8bba8caffbed34ffe61",
        "previous_block_hash": "c2cf4d19a1f544ee889a2fda72adf5ce204d3db91863ad4557fd6f4b632ff468",
        "time": "2024-06-13|00:15:02.935",
        "status": "Valide",
        "produit": "Fer",
        "current_place": "Chalons-en-Champagne",
        "destination": "Reims",
        "packages_total_number": "2",
        "packages_total_weight": "400kg",
        "package_id": "1164985237",
        "product_detail": "ceci est un  detail",
        "product_family": "Metal",
        "product_current_owner": "autre con",
        "product_origin_country": "Africa",
        "product_origin_producer": "Jupiter"
    },
    {
        "block_hash": "73a8b4543cddf20480a4a169c6710b7c566bfb952ff644a5e5e53d79b2e4304e",
        "previous_block_hash": "5f5bb823ac49eb212cc36b4348785b779ee1459e8b3ff8bba8caffbed34ffe61",
        "time": "2024-06-13|00:20:28.550",
        "status": "Valide",
        "produit": "Fer",
        "current_place": "Chalons-en-Champagne",
        "destination": "Reims",
        "packages_total_number": "2",
        "packages_total_weight": "400kg",
        "package_id": "972972975",
        "product_detail": "ceci est un  detail",
        "product_family": "Metal",
        "product_current_owner": "Moi",
        "product_origin_country": "Africa",
        "product_origin_producer": "Jupiter"
    },
    {
        "block_hash": "d62ca946d3b60de19b03b20c24f1f2466ff66e5b5d601fbccdc87f8ea2b45bc2",
        "previous_block_hash": "73a8b4543cddf20480a4a169c6710b7c566bfb952ff644a5e5e53d79b2e4304e",
        "time": "2024-06-13|00:20:50.527",
        "status": "Valide",
        "produit": "Fer",
        "current_place": "Chalons-en-Champagne",
        "destination": "Reims",
        "packages_total_number": "2",
        "packages_total_weight": "400kg",
        "package_id": "972972976",
        "product_detail": "ceci est un  detail",
        "product_family": "Metal",
        "product_current_owner": "Moi",
        "product_origin_country": "Africa",
        "product_origin_producer": "Jupiter"
    },
    {
        "block_hash": "c35719c7c2f6c2711157c155b8d3074bf9ba3e00d49fcf0b9deb329b671bb677",
        "previous_block_hash": "d62ca946d3b60de19b03b20c24f1f2466ff66e5b5d601fbccdc87f8ea2b45bc2",
        "time": "2024-06-13|00:21:10.595",
        "status": "Valide",
        "produit": "Fer",
        "current_place": "Chalons-en-Champagne",
        "destination": "Reims",
        "packages_total_number": "2",
        "packages_total_weight": "400kg",
        "package_id": "972972978",
        "product_detail": "ceci est un  detail",
        "product_family": "Metal",
        "product_current_owner": "Moi",
        "product_origin_country": "Africa",
        "product_origin_producer": "Jupiter"
    },
    {
        "block_hash": "cea16c0886a84b24777c18ddd7db6f38be324457297cc81a4e86723827318222",
        "previous_block_hash": "c35719c7c2f6c2711157c155b8d3074bf9ba3e00d49fcf0b9deb329b671bb677",
        "time": "2024-06-13|00:39:14.227",
        "status": "Test02",
        "produit": "Test02",
        "current_place": "Test02",
        "destination": "Test02",
        "packages_total_number": "Test02",
        "packages_total_weight": "Test02",
        "package_id": "1234",
        "product_detail": "Test02",
        "product_family": "Test02",
        "product_current_owner": "autre con",
        "product_origin_country": "Test02",
        "product_origin_producer": "Test02"
    },
    {
        "block_hash": "34df5e0b1928f47568cd1413ee2ef9fbeb994139a72b081426da99f11fb52604",
        "previous_block_hash": "cea16c0886a84b24777c18ddd7db6f38be324457297cc81a4e86723827318222",
        "time": "2024-06-13|00:39:22.246",
        "status": "Test02",
        "produit": "Test02",
        "current_place": "Test02",
        "destination": "Test02",
        "packages_total_number": "Test02",
        "packages_total_weight": "Test02",
        "package_id": "1234",
        "product_detail": "Test02",
        "product_family": "Test02",
        "product_current_owner": "autre con",
        "product_origin_country": "Test02",
        "product_origin_producer": "Test02"
    },
    {
        "block_hash": "cfbd1f8038a7df8c58013a824060298aac401acd88147803836728ea830a53c6",
        "previous_block_hash": "34df5e0b1928f47568cd1413ee2ef9fbeb994139a72b081426da99f11fb52604",
        "time": "2024-06-13|00:41:00.918",
        "status": "Test03",
        "produit": "Test03",
        "current_place": "Test03",
        "destination": "Test03",
        "packages_total_number": "Test03",
        "packages_total_weight": "Test03",
        "package_id": "Test03",
        "product_detail": "Test03",
        "product_family": "Test03",
        "product_current_owner": "autre con",
        "product_origin_country": "Test03",
        "product_origin_producer": "Test03"
    }
]

# Compute the hash of each block
block_hashes = [hash_block(block) for block in blockchain]

# Build the Merkle tree and get the root
merkle_tree = MerkleTree(block_hashes)
merkle_root = merkle_tree.root

print("Merkle Root:", merkle_root)
