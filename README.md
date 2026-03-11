# Task Manager - Géofoncier

Application de gestion de tâches avec gestion des utilisateurs et des permissions, construite en architecture microservices.

## Architecture

```
                        +------------------+
                        |    Frontend      |
                        |  Vue 3 (Vite)    |
                        |   :5173          |
                        +--------+---------+
                                 |
                  +--------------+--------------+
                  |                             |
          +-------v--------+          +--------v--------+
          |  Task Service   |          | Analytics Service|
          |  Django + DRF   |          |  Django + DRF   |
          | Auth + Tâches   |          | Consultation    |
          |    :8000        |          |    :8001        |
          +-------+--------+          +--------+--------+
                  |                             |
                  +--------------+--------------+
                                 |
                        +--------v--------+
                        |   PostgreSQL 16  |
                        |     :5432        |
                        +-----------------+
```

**Deux services backend distincts :**
1. **Task Service (port 8000)** — Service principal : authentification (JWT), gestion des utilisateurs, CRUD des tâches
2. **Analytics Service (port 8001)** — Service de consultation/analyse : statistiques par statut, par utilisateur, tâches en retard

**Flux d'authentification :**
1. Le frontend s'authentifie via le task-service (JWT avec simplejwt)
2. Le token JWT contient le username, le rôle et les permissions de l'utilisateur
3. L'analytics-service décode le JWT localement (secret partagé) pour vérifier les droits
4. Aucun appel inter-service n'est nécessaire pour les opérations courantes

## Choix techniques

| Choix | Justification |
|-------|---------------|
| **2 services Django séparés** | Séparation commande (task-service) / consultation (analytics-service), pattern CQRS |
| **1 base PostgreSQL partagée** | Les deux services lisent les mêmes données ; l'analytics-service utilise `managed = False` pour ne pas gérer les migrations |
| **JWT avec permissions dans le payload** | L'analytics-service vérifie les droits sans appeler le task-service. Trade-off : tokens courts (15 min) |
| **simplejwt (task-service)** | Gestion complète des tokens (access + refresh) intégrée à DRF |
| **PyJWT (analytics-service)** | Décodage léger du JWT via middleware custom, pas besoin de DRF auth complet |
| **Django + DRF** | Framework mature, ORM puissant, DRF idéal pour les APIs REST |
| **Vue 3 + Composition API** | Framework réactif moderne, Composition API pour une meilleure réutilisabilité |
| **Pinia** | State management officiel Vue 3, plus simple que Vuex |
| **IntegerField pour assigned_to/created_by** | Références cross-service sans FK (conséquence de l'architecture microservices) |
| **Logique métier dans services.py** | Séparation des concerns : vues légères, logique testable isolément |

## Installation et lancement

### Prérequis
- Docker et Docker Compose

### Démarrage

```bash
# 1. Cloner le projet
git clone <url-du-repo>
cd task-manager

# 2. Copier et adapter le fichier d'environnement
cp .env.example .env
# Éditer le .env avec vos propres valeurs (passwords, secret key, etc.)

# 3. Lancer en mode développement
docker compose up --build -d
```

### Lancement en production

```bash
# 1. Générer le certificat SSL (auto-signé pour test, Let's Encrypt pour la prod)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=localhost"

# 2. Lancer en mode production
docker-compose -f docker compose.prod.yml up --build -d
```

En production, Nginx sert le frontend en statique et fait reverse proxy vers les services Django (Gunicorn). Seuls les ports 80 (redirige vers HTTPS) et 443 sont exposés.

### Accès

| Mode | Service | URL |
|------|---------|-----|
| Dev | Frontend | http://localhost:5173 |
| Dev | Task API | http://localhost:8000/api/ |
| Dev | Analytics API | http://localhost:8001/api/ |
| Prod | Tout (via Nginx) | https://localhost |

### Compte admin par défaut

Les identifiants sont définis dans `.env` (voir `.env.example`) :

| Variable | Valeur par défaut |
|----------|-------------------|
| `ADMIN_USERNAME` | admin |
| `ADMIN_PASSWORD` | admin123 |

## Endpoints API

### Task Service (port 8000)

#### Authentification

| Méthode | URL | Description | Auth |
|---------|-----|-------------|------|
| POST | /api/auth/login/ | Login (retourne access + refresh JWT) | Non |
| POST | /api/auth/refresh/ | Refresh du token JWT | Non |

#### Utilisateurs

| Méthode | URL | Description | Auth |
|---------|-----|-------------|------|
| GET | /api/users/me/ | Profil utilisateur connecté | Oui |
| GET | /api/users/ | Liste des utilisateurs | Admin |
| POST | /api/users/ | Créer un utilisateur | Admin |
| GET | /api/users/{id}/ | Détail utilisateur | Oui |
| PATCH | /api/users/{id}/ | Modification utilisateur | Admin |
| DELETE | /api/users/{id}/ | Suppression utilisateur | Admin |
| GET | /api/roles/ | Liste des rôles | Oui |

#### Tâches

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | /api/tasks/ | Liste des tâches (filtrable) | task:read |
| POST | /api/tasks/ | Créer une tâche | task:create |
| GET | /api/tasks/{id}/ | Détail d'une tâche | task:read |
| PUT | /api/tasks/{id}/ | Modifier une tâche | task:update |
| PATCH | /api/tasks/{id}/ | Modification partielle | task:update |
| DELETE | /api/tasks/{id}/ | Supprimer une tâche | task:delete |

**Filtres disponibles** : `status`, `priority`, `assigned_to`, `created_by`, `due_date_before`, `due_date_after`

### Analytics Service (port 8001)

| Méthode | URL | Description | Permission |
|---------|-----|-------------|------------|
| GET | /api/analytics/summary/ | Tâches par statut | analytics:read |
| GET | /api/analytics/by-user/ | Tâches par utilisateur | analytics:read |
| GET | /api/analytics/overdue/ | Tâches en retard | analytics:read |

## Rôles et permissions

| Rôle | Permissions |
|------|-------------|
| admin | user:create, user:read, user:update, user:delete, task:create, task:read, task:update, task:delete, analytics:read |
| manager | task:create, task:read, task:update, task:delete, analytics:read |
| member | task:create, task:read, task:update |
| viewer | task:read, analytics:read |

### Règles métier
- Un **member** ne peut modifier/supprimer que les tâches qu'il a créées ou qui lui sont assignées
- Un **manager** ou **admin** peut modifier toutes les tâches
- Le champ `created_by` est automatiquement rempli avec l'ID de l'utilisateur connecté
- L'utilisateur **admin** est protégé : son rôle ne peut pas être changé, il ne peut pas être désactivé ni supprimé

## Tests

```bash
# Task service
docker-compose exec task-service python manage.py test

# Analytics service
docker-compose exec analytics-service python manage.py test
```

## Améliorations possibles

- **API Gateway** (Nginx/Traefik) : point d'entrée unique, TLS termination, rate limiting
- **Cache Redis** : mise en cache des analytics, sessions
- **CI/CD** : pipeline GitHub Actions avec lint, tests, build Docker, deploy
- **Rate limiting** : protection contre les abus (django-ratelimit ou API Gateway)
- **Monitoring** : Prometheus + Grafana, structured logging (JSON)
- **Audit trail** : journalisation des actions utilisateur sur les tâches
- **Refresh token rotation** : blacklist des anciens refresh tokens pour plus de sécurité
