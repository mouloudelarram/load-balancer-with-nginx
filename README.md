# Mini-Projet Docker Compose : Déploiement d’une architecture Web, Base de données et Reverse Proxy

## 1. Objectif

Ce projet a pour objectif de concevoir et déployer une application multi-services en utilisant Docker Compose. L’architecture repose sur trois composants principaux :

* Un service web implémenté en Python (Flask), exposant une API REST
* Une base de données PostgreSQL assurant le stockage persistant des données
* Un serveur Nginx jouant le rôle de reverse proxy et répartiteur de charge

L’ensemble des services est interconnecté via un réseau Docker commun, permettant leur communication interne.

---

## 2. Architecture du système

L’architecture globale du système est organisée comme suit :

* Le client envoie des requêtes HTTP vers le serveur Nginx
* Nginx redirige ces requêtes vers l’un des conteneurs du service web
* Le service web traite les requêtes et interagit avec la base de données PostgreSQL

Tous les services sont connectés au réseau Docker nommé `appnet`.

---

## 3. Technologies utilisées

* Docker et Docker Compose
* Python (Flask) pour le service web
* PostgreSQL pour la base de données
* Nginx pour le reverse proxy

---

## 4. Prérequis

Avant de déployer le projet, les outils suivants doivent être installés :

* Docker
* Docker Compose (plugin Docker)

Vérification :

```bash
docker --version
docker compose version
```

---

## 5. Déploiement de l’application

Se placer dans le répertoire du projet puis exécuter la commande suivante :

```bash
docker compose up -d --build
```

Cette commande permet de construire les images si nécessaire et de lancer les conteneurs en arrière-plan.

---

## 6. Accès au service

Une fois les conteneurs démarrés, l’application est accessible à l’adresse suivante :

```
http://localhost:8080
```

Nginx constitue le point d’entrée unique de l’application.

---

## 7. Vérification du fonctionnement

### 7.1 Vérification de la disponibilité du service

```bash
curl http://localhost:8080/health
```

---

### 7.2 Insertion de données

```bash
curl -X POST http://localhost:8080/items \
-H "Content-Type: application/json" \
-d '{"content":"test"}'
```

---

### 7.3 Consultation des données

```bash
curl http://localhost:8080/items
```

---

### 7.4 Vérification du routage des requêtes

```bash
curl http://localhost:8080/
```

La réponse contient un champ `instance` correspondant au nom du conteneur ayant traité la requête. Cela permet de vérifier la répartition des requêtes entre les différentes instances du service web.

---

## 8. Passage à l’échelle

Le service web peut être répliqué afin de simuler une montée en charge :

```bash
docker compose up -d --scale web=3
```

Il est ensuite possible de vérifier la distribution des requêtes en effectuant plusieurs appels successifs :

```bash
for i in $(seq 1 10); do curl -s http://localhost:8080/; done
```

---

## 9. Persistance des données

La base de données PostgreSQL utilise un volume Docker nommé `db_data`. Ce volume permet de conserver les données même après l’arrêt des conteneurs.

Arrêt sans suppression des données :

```bash
docker compose down
```

Redémarrage :

```bash
docker compose up -d
```

Suppression complète (y compris les données) :

```bash
docker compose down -v
```

---

## 10. Communication entre services

* Le service web accède à la base de données via le nom d’hôte `db`
* Nginx redirige les requêtes vers le service web via `web:8000`
* Tous les services partagent le réseau `appnet`, ce qui permet la résolution DNS interne

---

## 11. Limites du projet

Ce prototype présente certaines limitations :

* Absence de mécanisme d’authentification
* Absence de gestion avancée des migrations de base de données
* Load balancing basique reposant sur la résolution DNS de Docker
* Absence d’outils de supervision et de journalisation avancés

---

## 12. Arrêt de l’application

Pour arrêter les conteneurs :

```bash
docker compose down
```

---

## 13. Création de l’archive

Pour générer l’archive à soumettre :

```bash
tar -czf mini-prototype.tar.gz README.md docker-compose.yml web nginx
```

---

## 14. Conclusion

Ce projet met en œuvre les concepts fondamentaux de la conteneurisation et de l’orchestration avec Docker Compose. Il illustre :

* La séparation des services (web, base de données, proxy)
* La communication inter-conteneurs
* La persistance des données via les volumes
* La mise en place d’un reverse proxy
* La scalabilité horizontale d’un service

---