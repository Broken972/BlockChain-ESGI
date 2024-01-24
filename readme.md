# Projet Blockchain ESGI

Bienvenue sur le projet Blockchain ESGI. Ce projet vise à créer une blockchain simple et un système de contrats intelligents pour la traçabilité des produits.

## Démarrage

Pour commencer à utiliser ce projet, suivez les étapes ci-dessous :

1. Clonez le dépôt sur votre machine locale.
2. Assurez-vous que Python est installé sur votre système.
3. Installez les dépendances nécessaires en exécutant `pip install -r requirements.txt`.
4. Générez vos clés publiques et privées en utilisant le script fourni dans `functions.py`.
5. Lancez le serveur Flask en exécutant `python blockchain.py <port>` où `<port>` est le port sur lequel vous souhaitez que le serveur s'exécute.

## Fonctionnalités

- `blockchain.py` : Contient le code pour créer et gérer une blockchain.
- `functions.py` : Contient des fonctions utiles pour charger les clés, initialiser les en-têtes de requête, et plus encore.
- `verified_public_keys.json` : Un fichier JSON contenant les clés publiques vérifiées des participants au réseau.

## Contrats Intelligents

Le dossier `smart-contract` contient un exemple de contrat intelligent pour la traçabilité des produits. Vous pouvez déployer ce contrat sur une blockchain Ethereum pour suivre la propriété et l'emplacement des produits.

## Defaut configuration BLOC

    {
    "block_hash": "e38a354a0de0abc43e3ceee1521e68d83adef1cef3eef467c1863d718b669ff2",
    "previous_block_hash": "39331a6a2ea1cf31a5014b2a7c9e8dfad82df0b0666e81ce04cf8173cc5aed3e",
    "owner": "AcerlorMittal DSF",
    "time": "2018-11-20|12:00:00",
    "status": "En cours",
    "produit": "Tolle",
    "current_place": "Stock Centrale (AcerlorMittal)",
    "destination": "Client",
    "packages_total_number": "100",
    "paclages_total_weight": "100",
    "product_detail": [
      {"index": "1", "weight": "1", "origin_place":"Usine-France"},
      {"index": "2", "weight": "1","origin_place": "Usine-Chine"}
    ]
  },
  


