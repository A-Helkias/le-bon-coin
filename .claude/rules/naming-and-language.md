# Règle — nommage et langue

Cette règle prime sur toutes les autres. Elle s'applique à chaque fichier créé, sans exception.

## 1. Anglais pour le code, français pour l'interface

**Tout ce qu'une machine lit est en anglais. Tout ce qu'un humain lit à l'écran est en français.**

### 1.1 En anglais, toujours

| Catégorie | Exemples |
|---|---|
| Noms de fichiers et de dossiers | `product_service.py`, `CartPage.tsx`, `docker-compose.yml` |
| Variables, fonctions, classes, méthodes | `get_product_by_sku`, `CartItem`, `useProducts` |
| Tables, colonnes, index, contraintes | `products`, `price_cents`, `ix_products_sku` |
| Chemins d'API et paramètres | `GET /products/{product_id}?limit=50` |
| Branches Git | `feat/product-catalog`, `fix/cart-total` |
| Noms des commands, skills, agents et hooks | `/check`, `api-entity`, `code-reviewer`, `db-guard.sh` |
| Commentaires de code et docstrings | `# Prices are stored in cents to avoid float rounding.` |
| Messages de log techniques | `logger.info("Order %s confirmed", order_id)` |
| Noms de tests | `test_create_product_rejects_duplicate_sku` |
| Type et scope d'un message de commit | `feat(api)`, `fix(cart)`, `chore(tooling)` |

### 1.2 En français

| Catégorie | Exemples |
|---|---|
| Texte affiché à l'utilisateur | « Ajouter au panier », « Votre panier est vide » |
| Messages d'erreur remontés à l'interface | « Ce produit n'est plus disponible. » |
| Description d'un message de commit | `feat(api):` « ajoute le endpoint de détail produit » |
| Documentation destinée à l'équipe | `README.md`, `docs/` |
| Contenu des fichiers `.claude/` (prose) | ces règles, les skills, les commands |

## Le piège à éviter

Ne mélange jamais les deux dans un même identifiant. `getPanier`, `commande_service.py`, `class Commande` sont des erreurs : le nom est en français alors qu'il est lu par la machine.

De même, un message d'erreur métier a deux faces — le **code** de l'exception est en anglais, le **libellé** rendu à l'utilisateur est en français :

```python
raise InsufficientStockError("Ce produit n'est plus disponible en quantité suffisante.")
```

## Pourquoi

Le code est lu par des outils, des bibliothèques et, potentiellement, des développeurs qui ne parlent pas français. Un identifiant en français casse la cohérence avec l'écosystème (`FastAPI`, `SQLAlchemy`, `React` sont anglophones) et rend le projet inintelligible hors de l'équipe. L'interface, elle, s'adresse à des clients francophones.



