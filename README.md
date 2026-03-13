# Task Manager

Application de gestion de tâches avec authentification, gestion des rôles et tableau de bord analytique, construite en architecture microservices.

## Architecture

```
                        ┌──────────────────┐
                        │    Frontend      │
                        │  Vue 3 + Vite    │
                        │     :5173        │
                        └────────┬─────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
          ┌───────▼────────┐          ┌────────▼─────────┐
          │  Task Service  │          │ Analytics Service │
          │  Django + DRF  │          │   Django + DRF    │
          │ Auth + Tâches  │          │ Consultation (RO) │
          │    :8000       │          │     :8001         │
          └───────┬────────┘          └────────┬──────────┘
                  │                            │
                  └──────────────┬─────────────┘
                                 │
                        ┌────────▼────────┐
                        │  PostgreSQL 16  │
                        │     :5432       │
                        └─────────────────┘
```

Le projet est composé de **deux services backend distincts** :

1. **Task Service** (port 8000) -- Service principal : authentification JWT, gestion des utilisateurs et CRUD des taches
2. **Analytics Service** (port 8001) -- Service de consultation : statistiques par statut, par utilisateur, taches en retard. Lecture seule sur la base partagee

Les deux services partagent une base PostgreSQL. L'analytics-service utilise des modeles Django `managed = False` pour lire les tables sans gerer les migrations.

## Choix techniques

| Choix | Justification |
|-------|---------------|
| **2 services Django** | Separation commande/consultation (CQRS). Le task-service ecrit, l'analytics-service lit et agrege |
| **1 base PostgreSQL partagee** | Les deux services lisent les memes donnees. `managed = False` evite les conflits de migrations |
| **JWT avec permissions embarquees** | L'analytics-service verifie les droits sans appeler le task-service (stateless) |
| **simplejwt** (task-service) | Integration native DRF, gestion access + refresh tokens |
| **PyJWT** (analytics-service) | Decodage leger via middleware custom, pas besoin de DRF auth complet |
| **Vue 3 Composition API + Pinia** | Frontend reactif, store type-safe, interceptors Axios pour le refresh automatique |
| **IntegerField pour assigned_to/created_by** | References utilisateurs sans FK pour decoupler les modeles entre services |
| **seed_roles (management command)** | Roles et permissions crees au demarrage via `get_or_create`, idempotent et relancable |
| **drf-spectacular** | Documentation OpenAPI/Swagger auto-generee pour les deux services |

## Prerequis

- Docker et Docker Compose

## Demarrage rapide

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd task-manager

# 2. Copier et adapter le fichier d'environnement
cp .env.example .env

# 3. Lancer
docker compose up --build -d
```

Au demarrage, le task-service :
1. Genere les migrations (`makemigrations`)
2. Applique les migrations (`migrate`)
3. Cree les roles et permissions (`seed_roles`)
4. Cree le compte admin depuis les variables `.env` (`create_admin`)

## Lancement en production

```bash
# 1. Generer un certificat SSL auto-signe (ou utiliser Let's Encrypt)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=localhost"

# 2. Lancer avec le compose de production
docker compose -f docker-compose.prod.yml up --build -d
```

En production, Nginx sert le frontend en statique et fait reverse proxy vers les services Django (Gunicorn). Seuls les ports 80 (redirige vers 443) et 443 sont exposes.

## Acces

| Mode | Service | URL |
|------|---------|-----|
| Dev | Frontend | http://localhost:5173 |
| Dev | Task API | http://localhost:8000/api/ |
| Dev | Task API Docs | http://localhost:8000/api/docs/ |
| Dev | Analytics API | http://localhost:8001/api/analytics/ |
| Dev | Analytics API Docs | http://localhost:8001/api/analytics/docs/ |
| Prod | Tout (via Nginx) | https://localhost |

### Compte admin par defaut

Configurable dans `.env` :

| Variable | Valeur par defaut |
|----------|-------------------|
| `ADMIN_USERNAME` | admin |
| `ADMIN_PASSWORD` | admin123 |

## Flux d'authentification

```
Frontend ── POST /api/auth/login/ ──> Task Service
                                          │
                                     verifie credentials
                                     genere JWT contenant :
                                     {username, role, permissions}
                                          │
Frontend <── {access (15min), refresh (7j)} ──┘
    │
    ├── Bearer token ──> Task Service (:8000)    simplejwt decode → request.user
    │
    └── Bearer token ──> Analytics Service (:8001) middleware PyJWT decode → request.user_permissions
```

Le JWT est autosuffisant : l'analytics-service n'a jamais besoin d'appeler le task-service pour verifier un token. Le refresh est automatique cote frontend via un interceptor Axios.

## Endpoints API

### Task Service (port 8000)

Documentation interactive : http://localhost:8000/api/docs/

#### Authentification

| Methode | URL | Description | Auth |
|---------|-----|-------------|------|
| POST | `/api/auth/login/` | Login (retourne access + refresh JWT) | Non |
| POST | `/api/auth/refresh/` | Rafraichir le token JWT | Non |

#### Utilisateurs

| Methode | URL | Description | Auth |
|---------|-----|-------------|------|
| GET | `/api/users/me/` | Profil de l'utilisateur connecte | Authentifie |
| PATCH | `/api/users/me/` | Modifier son profil (email, prenom, nom) | Authentifie |
| GET | `/api/users/` | Liste des utilisateurs | Admin |
| POST | `/api/users/` | Creer un utilisateur | Admin |
| GET | `/api/users/{id}/` | Detail d'un utilisateur | Authentifie |
| PATCH | `/api/users/{id}/` | Modifier un utilisateur | Admin |
| DELETE | `/api/users/{id}/` | Supprimer un utilisateur | Admin |
| GET | `/api/roles/` | Liste des roles | Authentifie |

#### Taches

| Methode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/api/tasks/` | Liste des taches (paginee, filtrable) | task:read |
| POST | `/api/tasks/` | Creer une tache | task:create |
| GET | `/api/tasks/{id}/` | Detail d'une tache | task:read |
| PUT | `/api/tasks/{id}/` | Modifier une tache | task:update |
| PATCH | `/api/tasks/{id}/` | Modification partielle | task:update |
| DELETE | `/api/tasks/{id}/` | Supprimer une tache | task:delete |

**Filtres disponibles** : `status`, `priority`, `assigned_to`, `created_by`, `due_date_before`, `due_date_after`
**Recherche** : `?search=` sur titre et description
**Tri** : `?ordering=` sur created_at, updated_at, due_date, priority, status

### Analytics Service (port 8001)

Documentation interactive : http://localhost:8001/api/analytics/docs/

| Methode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | `/api/analytics/summary/` | Nombre de taches par statut | analytics:read |
| GET | `/api/analytics/by-user/` | Nombre de taches par utilisateur | analytics:read |
| GET | `/api/analytics/overdue/` | Taches en retard | analytics:read |

## Roles et permissions

| Role | Permissions |
|------|-------------|
| **admin** | Toutes (9 permissions) |
| **manager** | task:create, task:read, task:update, task:delete, analytics:read, user:read |
| **member** | task:create, task:read, task:update, analytics:read, user:read |
| **viewer** | task:read, analytics:read |

### Regles metier

- Un **member** ne peut modifier/supprimer que les taches qu'il a creees ou qui lui sont assignees
- Un **manager** ou **admin** peut modifier toutes les taches
- Le champ `created_by` est automatiquement rempli avec l'ID de l'utilisateur connecte
- L'utilisateur **admin** est protege : son role ne peut pas etre change, il ne peut pas etre desactive ni supprime

## Tests

```bash
# Lancer les tests du task-service
docker compose exec task-service python manage.py test

# Lancer les tests d'une app specifique
docker compose exec task-service python manage.py test users
docker compose exec task-service python manage.py test tasks
```

Les tests couvrent :
- **users** : creation d'utilisateur, login, refresh token, profil `/me`, permissions admin/member
- **tasks** : CRUD complet, controle des permissions, logique de modification par role

## Variables d'environnement

Voir [.env.example](.env.example) pour la liste complete :

| Variable | Description | Defaut |
|----------|-------------|--------|
| `JWT_SECRET_KEY` | Secret partage entre les services pour signer/verifier les JWT | - |
| `DB_NAME` | Nom de la base PostgreSQL | taskmanager_db |
| `DB_USER` | Utilisateur PostgreSQL | taskmanager_user |
| `DB_PASSWORD` | Mot de passe PostgreSQL | - |
| `ADMIN_USERNAME` | Username du compte admin cree au demarrage | admin |
| `ADMIN_PASSWORD` | Mot de passe du compte admin | - |
| `DEBUG` | Mode debug (1 = dev, 0 = prod) | 1 |
| `TASK_SERVICE_PORT` | Port du task-service | 8000 |
| `ANALYTICS_SERVICE_PORT` | Port de l'analytics-service | 8001 |
| `FRONTEND_PORT` | Port du frontend | 5173 |

## Persistance

Les donnees sont stockees dans un volume Docker (`db_data`). `docker compose down` conserve les donnees, `docker compose down -v` les supprime.

## Ameliorations possibles

- **Cache Redis** : mise en cache des analytics pour eviter les requetes d'agregation repetees
- **CI/CD** : pipeline GitHub Actions (lint, tests, build Docker)
- **Rate limiting** : protection contre les abus (django-ratelimit ou Nginx)
- **Monitoring** : Prometheus + Grafana, structured logging
- **Audit trail** : journalisation des actions sur les taches
- **Refresh token rotation** : blacklist des anciens refresh tokens
