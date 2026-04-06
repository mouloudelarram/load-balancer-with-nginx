# Mini-prototype Docker Compose (web + DB + Nginx)

Objectif : déployer une application composée de 3 services sur un même réseau Docker :
- **web** : API Python (Flask) qui lit/écrit dans PostgreSQL
- **db** : PostgreSQL avec **volume** persistant
- **nginx** : reverse proxy HTTP (load balancer) vers les containers `web`

## Prérequis (Ubuntu)
- Docker + plugin Compose
  - Vérifier : `docker --version` et `docker compose version`

## Démarrage (déploiement)
Dans le dossier du projet :
```bash
docker compose up -d --build
```

Accès :
- Nginx écoute sur `http://localhost:8080`

## Test rapide (communication web <-> db + passage nginx)
1) Vérifier la santé :
```bash
curl -s http://localhost:8080/health && echo
```

2) Créer des données (simulées) en base via l’API :
```bash
curl -s -X POST http://localhost:8080/items \
  -H 'Content-Type: application/json' \
  -d '{"content":"hello from compose"}' && echo
```

3) Lister les données :
```bash
curl -s http://localhost:8080/items && echo
```

4) Observer quel container web répond (utile pour le load balancing) :
```bash
curl -s http://localhost:8080/ && echo
```
La réponse inclut `instance` (hostname du container).

## Passage à l’échelle (manuel)
Exemple avec 3 réplicas du service web :
```bash
docker compose up -d --build --scale web=3
```

Puis lancer plusieurs requêtes et constater que `instance` varie :
```bash
for i in $(seq 1 10); do curl -s http://localhost:8080/ | jq -r .instance; done
```
(Si `jq` n’est pas installé : retirez `| jq -r .instance`.)

## Persistance DB (volume)
Le service `db` utilise le volume nommé `db_data`. Les données survivent à :
```bash
docker compose down
docker compose up -d
```

Pour supprimer aussi les données :
```bash
docker compose down -v
```

## Architecture
- Réseau : `appnet` (commun aux 3 services)
- Reverse proxy : Nginx sur port hôte `8080` -> proxy vers `web:8000`
- DB : PostgreSQL accessible depuis `web` via hostname `db`

## Limites / remarques
- Le “load balancing” se fait via Nginx + résolution DNS Docker : en mode `--scale`, Docker DNS renvoie plusieurs IP pour `web` et Nginx choisit une cible au fil des requêtes.
- Ce mini-prototype est volontairement simple (pas d’auth, pas de migrations avancées).

## Arrêt
```bash
docker compose down
```

## Création de l’archive à uploader
Depuis le dossier du projet :
```bash
tar -czf mini-prototype.tar.gz README.md docker-compose.yml web nginx
```

