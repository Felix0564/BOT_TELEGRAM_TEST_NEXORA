
Nexora Restaurant Bot est un chatbot Telegram qui permet aux clients de consulter le menu, passer des commandes et indiquer une adresse de livraison ou un retrait sur place. Le bot notifie également l’administrateur du restaurant lorsqu’une commande est passée.


## Fonctionnalités

Affichage du menu avec les plats et leurs prix

Commande guidée en plusieurs étapes :

Choix de l’article

Saisie de la quantité

Saisie de l’adresse ou retrait sur place

Confirmation de la commande

Gestion des commandes côté backend avec sauvegarde dans un fichier JSON

Notification automatique de l’administrateur pour chaque nouvelle commande

Commandes annulables à tout moment via /cancel

Gestion des erreurs et messages informatifs pour l’utilisateur


## Technologies utilisées

Python 3.10+

python-telegram-bot : pour l’intégration Telegram

JSON: pour le stockage local des commandes

dotenv: pour la gestion des variables d’environnement

Logging: Python pour le suivi et la détection des erreurs

## Création d'un environnement virtuel ou activer:
python -m venv env
source venv/bin/activate      Linux / macOS
env\Scripts\activate 


## Installation des dépendances :
pip install -r requirements.txt

## Lancer le bot :

python bot.py

Il sera actif et répondra aux commandes /start, /menu, /order, /help

## Utilisation

/start – Accueil et instructions

/menu – Affichage du menu du restaurant

/order – Démarrer une commande guidée

/cancel – Annuler la commande en cours

/help – Aide et informations sur les commandes


## Gestion des commandes côté backend

Les commandes sont sauvegardées dans un fichier orders.json.

Chaque commande contient :

ID unique

ID et nom de l’utilisateur

Article commandé

Quantité

Total

### NB:
   
   Une fois que le serveur est lancé.
   Il faut utiliser ce nom: @TestNexoraRestaurantBot sur Telegram pour l'interaction.
$$