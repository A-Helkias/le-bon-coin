# Règles de développement Backend

Ces règles sont obligatoires pour tout développement backend.

Elles définissent les contraintes à respecter lors de la création, modification ou maintenance du code backend.

---

# 1. Découpage en couches

Le backend doit respecter une séparation stricte des responsabilités entre les différentes couches.

Pour chaque entité métier, les différentes couches doivent utiliser **le même nom d'entité**.

Par exemple, pour l'entité `Product` :

```text
models/product.py
schemas/product.py
repositories/product.py
services/product.py
api/products.py
```

La correspondance est la suivante :

```text
Product
   │
   ├── models/product.py
   ├── schemas/product.py
   ├── repositories/product.py
   ├── services/product.py
   └── api/products.py
```

Cette convention doit être conservée pour les nouvelles entités.

### Acceptable

Pour une entité `Order` :

```text
models/order.py
schemas/order.py
repositories/order.py
services/order.py
api/orders.py
```

Pour une entité `User` :

```text
models/user.py
schemas/user.py
repositories/user.py
services/user.py
api/users.py
```

### Interdit

Utiliser des noms différents selon les couches :

```text
models/product.py
schemas/item.py
repositories/product_repository.py
services/catalog_service.py
api/catalog.py
```

lorsque ces fichiers représentent tous la même entité `Product`.

### Principe à retenir

> Une entité métier porte le même nom à travers les différentes couches du backend.

---

# 2. Requêtes SQLAlchemy uniquement dans les repositories

Toute requête SQLAlchemy doit être effectuée **exclusivement dans un repository**.

Aucune requête SQLAlchemy ne doit apparaître dans :

* un service ;
* une route ;
* un schéma Pydantic ;
* un modèle utilisé comme couche métier ;
* ou toute autre couche qui n'est pas le repository.

Le repository est la couche responsable de l'accès aux données.

### Acceptable

```python
# repositories/product.py

result = await db.execute(
    select(Product).where(Product.id == product_id)
)
```

### Interdit

```python
# services/product.py

result = await db.execute(
    select(Product).where(Product.id == product_id)
)
```

### Interdit

```python
# api/products.py

result = await db.execute(
    select(Product).where(Product.id == product_id)
)
```

Même si la requête est techniquement correcte, elle viole la séparation des couches.

### Principe à retenir

> Toute interaction SQLAlchemy avec la base de données passe par un repository.

---

# 3. FastAPI interdit dans les services

Les services contiennent la logique métier.

Ils ne doivent pas dépendre de FastAPI.

Il est donc interdit d'utiliser :

```python
import fastapi
```

dans un service.

Il est également interdit d'utiliser :

```python
HTTPException
```

dans un service.

Les services ne doivent pas connaître les mécanismes HTTP.

### Interdit

```python
from fastapi import HTTPException

async def get_product(...):
    ...
    raise HTTPException(
        status_code=404,
        detail="Produit introuvable"
    )
```

### Acceptable

Le service lève une exception métier :

```python
raise NotFoundError(...)
```

Cette exception sera ensuite traduite en réponse HTTP par le mécanisme global prévu à cet effet.

### Principe à retenir

> Un service connaît la logique métier, pas HTTP ni FastAPI.

---

# 4. Gestion du commit et du flush

Le repository ne doit jamais effectuer de `commit()`.

Il est interdit de faire :

```python
await db.commit()
```

dans un repository.

Le repository peut effectuer un :

```python
await db.flush()
```

lorsque cela est nécessaire au fonctionnement de la logique de persistance.

Le `commit` appartient à la **dépendance de session**.

### Acceptable

```python
# repository

db.add(product)
await db.flush()
```

### Interdit

```python
# repository

db.add(product)
await db.commit()
```

### Principe à retenir

> Le repository persiste et flush les changements nécessaires ; le commit est géré par la dépendance de session.

---

# 5. Les routes ne retournent jamais directement un modèle SQLAlchemy

Une route API ne doit jamais retourner directement une instance de modèle SQLAlchemy.

Les données exposées par l'API doivent toujours être représentées par un **schéma Pydantic**.

### Interdit

```python
@router.get("/{product_id}")
async def get_product(...) -> Product:
    return product
```

si `Product` est le modèle SQLAlchemy.

### Acceptable

```python
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(...) -> ProductResponse:
    ...
```

Le modèle SQLAlchemy reste interne à la couche de persistance.

Le schéma Pydantic constitue le contrat exposé par l'API.

### Principe à retenir

> Un modèle SQLAlchemy ne sort jamais directement d'une route. Une route expose toujours un schéma Pydantic.

---

# 6. Asynchrone de bout en bout

Le backend doit être entièrement asynchrone.

Il ne doit pas introduire de driver ou de mécanisme synchrone dans une chaîne qui doit être `async`.

Cela implique notamment :

* `async def` ;
* `AsyncSession` ;
* client HTTP asynchrone ;
* tests utilisant `httpx.AsyncClient`.

### Acceptable

```python
async def get_product(...):
    ...
```

avec :

```python
AsyncSession
```

et :

```python
httpx.AsyncClient
```

pour les tests HTTP.

### Interdit

Introduire un driver de base de données synchrone ou une session SQLAlchemy synchrone dans le backend.

### Interdit

```python
def get_product(...):
    ...
```

lorsque cette fonction effectue une opération d'I/O qui doit être asynchrone.

### Interdit

Utiliser un client HTTP synchrone dans les tests lorsque le test doit exercer l'API asynchrone.

### Principe à retenir

> La chaîne backend est asynchrone de bout en bout : API → service → repository → base de données, ainsi que les clients HTTP utilisés dans les tests.

---

# 7. Montants monétaires en centimes

Les montants financiers doivent être représentés par des **entiers exprimés en centimes**.

Le champ doit utiliser une représentation de type :

```python
price_cents: int
```

Les montants monétaires ne doivent jamais être représentés par un `float`.

### Acceptable

```python
price_cents: int
```

Exemple :

```text
1999 → 19,99 €
```

### Interdit

```python
price: float
```

### Interdit

```python
price = 19.99
```

pour représenter directement un montant financier.

### Pourquoi

Les nombres flottants ne constituent pas une représentation fiable pour les calculs monétaires.

### Principe à retenir

> Tout montant financier est stocké et manipulé en entier, exprimé en centimes. Aucun `float` pour l'argent.

---

# 8. Identifiants exposés sous forme de UUID

Les identifiants exposés par l'API doivent être des **UUID**.

Les identifiants ne doivent pas être des entiers auto-incrémentés exposés publiquement.

### Acceptable

```python
id: UUID
```

### Interdit

```python
id: int
```

lorsque cet entier constitue l'identifiant exposé de la ressource.

### Interdit

Exposer directement un identifiant de base de données auto-incrémenté sous forme :

```text
/products/42
```

si l'identifiant public attendu est un UUID.

### Principe à retenir

> Les identifiants exposés par l'API sont des UUID et non des entiers auto-incrémentés.

---

# 9. Horodatages en UTC

Les horodatages doivent être enregistrés en **UTC**.

Les champs concernés doivent utiliser un défaut généré côté serveur avec :

```python
server_default=func.now()
```

### Acceptable

```python
created_at = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
)
```

### Interdit

Créer manuellement la date dans le code applicatif lorsque le champ doit utiliser l'horodatage serveur.

### Interdit

Utiliser l'heure locale de la machine comme source de vérité pour les horodatages persistés.

### Principe à retenir

> Les horodatages persistés sont en UTC et leur valeur par défaut est générée par le serveur de base de données.

---

# 10. Pagination obligatoire des routes de liste

Toute route qui retourne une liste doit être paginée.

Une route de liste doit accepter :

```text
limit
offset
```

avec les contraintes suivantes :

```text
limit par défaut : 50
limit maximum   : 200
offset           : paramètre de pagination
```

La réponse doit utiliser la structure :

```json
{
  "items": [],
  "total": 0
}
```

### Acceptable

```text
GET /products?limit=50&offset=0
```

Réponse :

```json
{
  "items": [
    ...
  ],
  "total": 143
}
```

### Acceptable

```text
GET /products?limit=100&offset=50
```

### Interdit

```text
GET /products
```

qui retourne l'intégralité des produits sans pagination.

### Interdit

Autoriser :

```text
limit=1000
```

si la limite maximale définie est `200`.

### Interdit

Retourner directement :

```json
[
  {...},
  {...}
]
```

pour une route de liste lorsque le contrat attendu est :

```json
{
  "items": [...],
  "total": 0
}
```

### Principe à retenir

> Toute route de liste est paginée et retourne toujours `items` et `total`.

---

# 11. Exceptions métier

Les services doivent signaler les erreurs métier en utilisant les exceptions métier définies dans :

```text
app/core/exceptions.py
```

Les exceptions métier disponibles comprennent notamment :

```text
NotFoundError
AlreadyExistsError
BusinessRuleError
InsufficientStockError
```

Le service doit lever l'exception métier correspondant à la situation rencontrée.

### Acceptable

```python
raise NotFoundError(...)
```

lorsqu'une ressource attendue n'existe pas.

### Acceptable

```python
raise AlreadyExistsError(...)
```

lorsqu'une règle d'unicité métier est violée.

### Acceptable

```python
raise InsufficientStockError(...)
```

lorsqu'une opération ne peut pas être effectuée en raison d'un stock insuffisant.

### Interdit

Convertir directement l'erreur métier en `HTTPException` dans le service.

### Interdit

```python
raise HTTPException(status_code=404)
```

dans un service.

### Principe à retenir

> Les services expriment les erreurs en termes métier, jamais en termes HTTP.

---

# 12. Traduction globale des exceptions en codes HTTP

Les exceptions métier sont traduites en codes HTTP par un **gestionnaire global** déclaré dans :

```text
app/main.py
```

Le gestionnaire global constitue le point de traduction entre :

```text
Exception métier
        ↓
Code HTTP
```

### Acceptable

```text
Service
  ↓
NotFoundError
  ↓
gestionnaire global
  ↓
HTTP 404
```

### Interdit

Faire cette traduction directement dans une route :

```python
try:
    ...
except NotFoundError:
    raise HTTPException(status_code=404)
```

lorsque le gestionnaire global est précisément chargé de cette responsabilité.

### Principe à retenir

> La conversion des exceptions métier en réponses HTTP est centralisée dans le gestionnaire global.

---

# 13. Les routeurs ne lèvent jamais `HTTPException`

Un routeur API ne doit jamais lever directement une `HTTPException`.

Il doit appeler les services et laisser les exceptions métier remonter jusqu'au gestionnaire global.

### Interdit

```python
@router.get("/{product_id}")
async def get_product(...):
    product = ...

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Produit introuvable",
        )
```

### Acceptable

```text
Route
 ↓
Service
 ↓
NotFoundError
 ↓
Gestionnaire global
 ↓
404
```

### Principe à retenir

> Les routes orchestrent les appels API ; elles ne traduisent pas elles-mêmes les erreurs métier en codes HTTP.

---

# 14. Tests des routes

Chaque route doit disposer :

* d'un test du **cas nominal** ;
* d'au moins un test d'un **cas d'erreur pertinent**.

Les cas d'erreur peuvent notamment correspondre à :

```text
404
409
422
```

selon le comportement attendu de la route.

### Cas nominal

Le test doit vérifier que la route fonctionne avec une requête valide et retourne le résultat attendu.

### Cas d'erreur

Le test doit vérifier que la route produit correctement l'erreur attendue lorsqu'une situation d'échec prévue se produit.

### Acceptable

Pour une route de récupération d'un produit :

```text
GET /products/{id}

Cas nominal → 200
Produit inexistant → 404
```

### Acceptable

Pour une création :

```text
POST /products

Cas nominal → 201
Donnée invalide → 422
Ressource déjà existante → 409
```

### Interdit

Créer une route sans test du cas nominal.

### Interdit

Créer une route sans aucun test d'erreur lorsque la route possède des situations d'erreur prévues.

### Principe à retenir

> Toute route doit être testée dans son fonctionnement nominal et dans au moins un scénario d'erreur pertinent.

---

# 15. Tests sur une vraie base PostgreSQL

Les tests backend doivent utiliser une **véritable base PostgreSQL jetable**.

SQLite ne doit pas être utilisé pour remplacer PostgreSQL dans les tests.

L'objectif est que les contraintes testées soient les mêmes que celles réellement utilisées par le backend.

### Acceptable

```text
Test API
   ↓
Application réelle
   ↓
Repository réel
   ↓
PostgreSQL de test jetable
```

### Interdit

```text
Test API
   ↓
SQLite
```

pour simuler PostgreSQL.

### Pourquoi

Une base SQLite peut avoir un comportement différent de PostgreSQL concernant notamment :

* les types ;
* les contraintes ;
* les index ;
* les comportements SQL ;
* les transactions.

Le test doit donc utiliser le même moteur de base de données que celui attendu par l'application.

### Principe à retenir

> Les tests doivent exercer les contraintes réelles de PostgreSQL, pas une approximation fournie par SQLite.

---

# 16. Pas de mock du repository dans les tests d'API

Les tests d'API ne doivent pas mocker les repositories.

L'objectif est de tester la chaîne complète :

```text
HTTP
 ↓
Route
 ↓
Service
 ↓
Repository
 ↓
PostgreSQL
```

### Acceptable

Une requête HTTP de test traverse réellement :

```text
API → service → repository → PostgreSQL
```

### Interdit

Remplacer le repository par un mock :

```python
mock_repository = ...
```

puis vérifier uniquement le comportement de la route avec ce mock.

### Pourquoi

Un test d'API doit vérifier que les différentes couches fonctionnent réellement ensemble.

### Principe à retenir

> Les tests d'API testent la chaîne complète et ne remplacent pas le repository par un mock.

---

# 17. Aucun contournement des tests ou du typage

Il est interdit de faire passer artificiellement une implémentation ou une suite de tests en contournant les contraintes du projet.

Sont notamment interdits :

```text
skip
# type: ignore
```

ainsi que tout assouplissement de la configuration destiné à masquer une erreur.

### Interdit

```python
@pytest.mark.skip
```

utilisé pour éviter un test qui échoue.

### Interdit

```python
# type: ignore
```

utilisé pour masquer une erreur de typage introduite par l'implémentation.

### Interdit

Modifier la configuration du projet pour désactiver une vérification uniquement afin de faire passer le code.

### Acceptable

Corriger réellement :

* le code ;
* le typage ;
* le test ;
* ou l'implémentation concernée.

### Principe à retenir

> Une erreur doit être corrigée, pas masquée.

---

# 18. Génération de code

Les modifications doivent rester **minimales et justifiées par la logique métier**.

Il ne faut pas générer du code uniquement parce qu'il est possible de le générer.

La génération automatique ou mécanique de grandes quantités de code sans nécessité fonctionnelle constitue un **anti-pattern**.

### Acceptable

Ajouter uniquement les fichiers, fonctions ou modifications nécessaires à l'implémentation de la logique métier demandée.

### Interdit

Générer automatiquement de nombreuses abstractions, classes ou fichiers qui ne répondent à aucun besoin réel.

### Interdit

Créer du code uniquement pour remplir une structure ou produire artificiellement davantage de code.

### Principe à retenir

> Chaque modification doit être justifiée par le besoin métier ou technique réel. Le code généré sans nécessité est interdit.

---

# Synthèse des règles obligatoires

Le backend doit respecter les principes suivants :

1. **Une entité possède un fichier par couche et conserve le même nom d'entité entre les couches.**
2. **Toute requête SQLAlchemy appartient exclusivement à un repository.**
3. **Un service ne doit pas importer FastAPI.**
4. **Un service ne doit jamais lever `HTTPException`.**
5. **Un repository ne doit jamais effectuer `db.commit()`.**
6. **Le repository utilise `flush()` lorsque nécessaire ; le commit appartient à la dépendance de session.**
7. **Une route ne retourne jamais directement un modèle SQLAlchemy.**
8. **Une route expose toujours un schéma Pydantic.**
9. **Le backend est asynchrone de bout en bout.**
10. **Les montants sont des entiers en centimes et jamais des `float`.**
11. **Les identifiants exposés sont des UUID.**
12. **Les horodatages sont en UTC avec une valeur par défaut générée par le serveur.**
13. **Toute route de liste est paginée avec `limit` et `offset`.**
14. **`limit` vaut 50 par défaut et ne peut pas dépasser 200.**
15. **Les réponses paginées utilisent `{"items": [...], "total": int}`.**
16. **Les services lèvent des exceptions métier définies dans `app/core/exceptions.py`.**
17. **Les exceptions métier sont traduites en codes HTTP par le gestionnaire global de `app/main.py`.**
18. **Les routeurs ne lèvent jamais directement `HTTPException`.**
19. **Chaque route possède au minimum un test nominal et un test d'erreur pertinent.**
20. **Les tests utilisent une vraie base PostgreSQL jetable.**
21. **SQLite n'est pas utilisé pour remplacer PostgreSQL dans les tests.**
22. **Les tests d'API ne mockent pas les repositories.**
23. **Les tests doivent exercer la chaîne complète de l'API jusqu'à la base de données.**
24. **Les tests, le typage et la configuration ne doivent jamais être contournés avec `skip`, `# type: ignore` ou un assouplissement artificiel de la configuration.**
25. **Les modifications doivent rester minimales et être justifiées par la logique métier.**
26. **La génération de code sans nécessité réelle est considérée comme un anti-pattern.**
