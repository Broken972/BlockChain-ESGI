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

##


