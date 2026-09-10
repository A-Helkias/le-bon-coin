---
name: api-entity
description: Recette complète pour créer ou modifier une entité métier du backend Le Bon Coin (produit, panier, commande, utilisateur) à travers les cinq couches — modèle SQLAlchemy, schéma Pydantic, repository, service, routeur FastAPI — plus les migrations et les tests. À utiliser dès qu'il faut ajouter une table, exposer une nouvelle ressource REST, ou faire évoluer un champ existant côté backend.
---

# Créer une entité backend

Une entité traverse cinq couches. Elles se créent **dans cet ordre**, et chacune est complète avant de passer à la suivante. Ne saute pas de couche, même pour une entité triviale : c'est ce qui garde le code prévisible.

## 1. Modèle — `app/models/<entite>.py`

```python
class Product(Base):
    __tablename__ = "products"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sku: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    price_cents: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

Toujours : UUID en clé primaire, `price_cents` entier, `created_at` en `server_default`. Déclare le modèle dans `app/models/__init__.py`, sinon Alembic ne le verra pas.

## 2. Schémas — `app/schemas/<entite>.py`

Trois schémas distincts, jamais un seul :

| Schéma | Rôle |
|---|---|
| `ProductCreate` | entrée de création — pas d'`id`, pas de `created_at` |
| `ProductUpdate` | entrée de mise à jour — tous les champs optionnels |
| `ProductRead` | sortie — `model_config = ConfigDict(from_attributes=True)` |

## 3. Repository — `app/repositories/<entite>.py`

Seule couche autorisée à importer SQLAlchemy. Fonctions `async`, prenant une `AsyncSession` en premier argument. Elle retourne des modèles ou `None` — **jamais** de `HTTPException`.

## 4. Service — `app/services/<entite>.py`

Porte la logique métier et les règles d'invariant (stock disponible, SKU unique, panier non vide avant commande). Elle lève des exceptions métier définies dans `app/core/exceptions.py`, jamais des exceptions HTTP.

## 5. Routeur — `app/api/<entites>.py`

Fin, sans logique. Il déclare `response_model`, injecte la session, appelle le service, traduit les exceptions métier en codes HTTP. Enregistre-le dans `app/api/__init__.py`.

## 6. Migration

Utilise la commande `/migrate <description>` — elle génère, fait relire et applique. Ne rédige pas la migration à la main.

## 7. Tests — `tests/api/test_<entites>.py`

Pour chaque route : le cas nominal, **plus** au moins un cas d'erreur. Les tests tournent sur une vraie base Postgres jetable via la fixture `db_session`, et appellent l'API avec `httpx.AsyncClient` — pas de mock du repository.

## Vérification finale

Lance `/check back`. L'entité n'est pas terminée tant que format, lint, mypy et pytest ne sont pas tous verts.

## Détail des conventions

Les signatures exactes, les exceptions métier disponibles et les fixtures de test sont dans `references/conventions.md`. Consulte ce fichier avant d'écrire le repository et les tests.
