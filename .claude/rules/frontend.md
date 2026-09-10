# Règles de développement Frontend

Ces règles sont obligatoires pour tout développement frontend.

Elles définissent les contraintes à respecter lors de la création, modification ou maintenance du code frontend.

---

## 1. Approche par composants

Le développement frontend doit suivre une **approche par composants**.

Lorsqu'une même interface, fonctionnalité ou logique de présentation est utilisée par plusieurs écrans, elle doit pouvoir être représentée par un composant réutilisable afin d'éviter la duplication de code et de faciliter la maintenance.

Cependant, **aucun composant ne doit être mutualisé par anticipation**.

Un composant ne doit être extrait vers un emplacement partagé qu'à partir de son **deuxième usage réel**.

Le premier usage doit rester local à l'écran ou à la fonctionnalité concernée.

### Acceptable

Un composant est d'abord créé pour un seul écran :

```text
ProductCard
```

Il reste local à cet écran.

Plus tard, un second écran nécessite réellement le même composant.

Le composant peut alors être mutualisé.

### Acceptable

Deux écrans utilisent réellement le même composant :

```text
Catalogue → ProductCard
Favoris   → ProductCard
```

La mutualisation est alors justifiée par un besoin réel.

### Interdit

Créer immédiatement un composant partagé en prévision d'un éventuel futur usage :

```text
GenericProductCard
```

alors qu'un seul écran l'utilise.

### Interdit

Créer plusieurs composants génériques uniquement parce qu'ils pourraient éventuellement être réutilisés plus tard.

**Principe à retenir :**

> On mutualise à partir du deuxième usage réel, jamais sur la base d'une réutilisation hypothétique.

---

## 2. Interdiction des emojis dans le code et les tests

Les emojis sont interdits dans le code frontend et dans les tests.

Cette interdiction concerne notamment :

* les composants ;
* les pages ;
* les fonctions ;
* les commentaires ;
* les chaînes de caractères ;
* les messages affichés par l'interface ;
* les données utilisées dans le code frontend ;
* les tests ;
* les assertions et leurs données de test.

Exemples d'emojis interdits :

```text
❤️
🥰
😍
😘
😎
🤩
🫶
🫰
🫱
🫲
🫳
🫴
```

La règle s'applique également aux emojis qui ne figureraient pas dans cette liste.

### Raisons

Les emojis ne doivent pas être utilisés comme substituts à une information textuelle, car ils :

* ne sont pas des contenus textuels sémantiques ;
* ne sont pas nécessairement accessibles aux lecteurs d'écran ;
* ne sont pas directement traduisibles ;
* peuvent avoir une interprétation différente selon les utilisateurs ou les cultures.

### Interdit

```tsx
<p>Commande confirmée ❤️</p>
```

### Acceptable

```tsx
<p>Commande confirmée.</p>
```

### Interdit

```ts
expect(screen.getByText("Commande confirmée ❤️")).toBeInTheDocument();
```

### Acceptable

```ts
expect(screen.getByText("Commande confirmée.")).toBeInTheDocument();
```

**Principe à retenir :**

> Toute information communiquée par le frontend doit pouvoir être comprise sans dépendre d'un emoji.

---

## 3. Aucune donnée métier mockée ou inventée dans le frontend

Le frontend ne doit **jamais inventer, créer ou maintenir lui-même des données métier**.

Les données métier affichées par le frontend doivent provenir du backend.

Cela concerne notamment :

* les produits ;
* les utilisateurs ;
* les commandes ;
* les prix ;
* les stocks ;
* les statuts ;
* les catégories ;
* les informations commerciales ;
* et, plus généralement, toute donnée ayant une signification métier.

Le frontend doit afficher les données que lui fournit le backend. Il ne doit pas créer de valeurs fictives pour compléter, remplacer ou simuler silencieusement des données métier réelles.

### Interdit

```ts
const products = [
  {
    id: 1,
    name: "Produit exemple",
    price: 19.99,
  },
];
```

si cette donnée représente une donnée métier censée provenir du backend.

### Interdit

```ts
const stock = product.stock ?? 10;
```

si `10` est une valeur métier inventée par le frontend.

### Interdit

```ts
const price = product.price ?? 29.99;
```

si `29.99` est utilisé pour masquer l'absence du prix fourni par le backend.

### Acceptable

Le frontend reçoit les données du backend et les affiche :

```ts
const products = response.products;
```

### Données de test

Cette interdiction **ne concerne pas les données simulées nécessaires aux tests**.

Les tests peuvent utiliser des données fictives afin de simuler les réponses du backend.

Ces données de test servent uniquement à reproduire un scénario de test et ne constituent pas une source de données métier du frontend.

### Acceptable

Un test simule une réponse API contenant :

```ts
{
  id: 1,
  name: "Produit de test",
  price: 19.99
}
```

à l'aide du mécanisme de simulation réseau utilisé par les tests.

### Principe à retenir

> Le frontend ne doit jamais être la source de vérité des données métier. Les données métier viennent du backend. Les données fictives sont autorisées uniquement lorsqu'elles sont nécessaires à la simulation des tests.

---

## 4. Qualité et responsabilité des données reçues du backend

Le frontend doit **afficher les données métier fournies par le backend**.

Il ne doit pas modifier arbitrairement leur contenu, inventer des valeurs de remplacement ou corriger silencieusement les données métier reçues.

La responsabilité du frontend est de présenter correctement les données qui lui sont fournies.

Si une donnée métier fournie par le backend est incorrecte, incomplète ou incohérente, le frontend ne doit pas inventer une valeur pour la remplacer.

### Interdit

Le backend fournit :

```json
{
  "price": null
}
```

et le frontend décide arbitrairement d'afficher :

```text
19,99 €
```

### Interdit

Le backend fournit un stock de `0` et le frontend remplace cette valeur par `10` parce qu'il considère que cela rend l'interface plus cohérente.

### Acceptable

Le frontend respecte la donnée fournie par le backend et l'affiche conformément à son contrat.

### Principe à retenir

> Le frontend présente les données du backend ; il ne les réinvente pas et ne doit pas masquer silencieusement leur qualité.

---

## 5. Convention de nommage des fichiers

Les fichiers frontend doivent utiliser le **PascalCase** pour leur nom.

### Acceptable

```text
ProductCard.tsx
ProductList.tsx
CheckoutPage.tsx
OrderSummary.tsx
UserProfile.tsx
```

### Interdit

```text
productCard.tsx
product-card.tsx
product_card.tsx
checkout-page.tsx
order-summary.tsx
```

### Exception technique

Lorsqu'un fichier est soumis à une convention technique qui impose un nom entièrement en minuscules, cette convention est autorisée.

Exemple :

```text
index.ts
```

Cette exception concerne uniquement les fichiers dont le nom doit techniquement respecter cette convention.

Elle ne constitue pas une autorisation générale d'utiliser le camelCase, le kebab-case ou le snake_case pour les fichiers frontend.

**Principe à retenir :**

> PascalCase par défaut pour les fichiers frontend ; les noms techniquement imposés en minuscules constituent une exception autorisée.

---

## 6. Langue des libellés et messages

Tous les textes produits par l'interface frontend doivent être en **français**.

Cela concerne notamment :

* les libellés ;
* les boutons ;
* les titres ;
* les messages d'information ;
* les messages d'erreur ;
* les messages de confirmation ;
* les messages de validation ;
* les états vides ;
* les indications affichées à l'utilisateur.

### Acceptable

```text
Ajouter au panier
Valider la commande
Modifier l'adresse
Une erreur est survenue.
Aucun produit disponible.
Commande confirmée.
```

### Interdit

```text
Add to cart
Checkout
Save changes
Something went wrong.
No products found.
Order confirmed.
```

lorsque ces textes sont générés directement par le frontend.

### Données provenant du backend

Cette règle ne signifie pas que le frontend doit modifier les données reçues du backend.

Si le backend fournit le nom d'un produit, d'une marque, d'une entreprise ou toute autre donnée métier, le frontend doit afficher cette donnée telle qu'elle est fournie.

Le frontend ne doit pas traduire ou réécrire arbitrairement les données métier reçues du backend.

### Principe à retenir

> Les textes d'interface produits par le frontend sont en français. Les données métier provenant du backend sont affichées telles qu'elles sont fournies.

---

## 7. Formats de date

Les dates affichées par le frontend doivent utiliser un **format français**.

Les formats de date destinés à l'utilisateur doivent être cohérents avec les conventions françaises.

### Acceptable

```text
10 septembre 2026
```

### Interdit

```text
September 10, 2026
```

lorsque le frontend produit lui-même ce format pour l'utilisateur.

Le format interne utilisé pour communiquer avec le backend n'est pas concerné par cette règle.

La règle concerne le **format présenté à l'utilisateur**.

---

## 8. Accessibilité des images

Chaque image représentant un contenu ayant une signification pour l'utilisateur doit posséder un attribut `alt` approprié.

L'attribut `alt` doit décrire l'information véhiculée par l'image.

### Acceptable

```tsx
<img
  src={product.imageUrl}
  alt={`Photo du produit ${product.name}`}
/>
```

### Interdit

```tsx
<img src={product.imageUrl} />
```

### Image décorative

Lorsqu'une image est purement décorative et ne transmet aucune information utile, son `alt` peut être vide :

```tsx
<img src="/decoration.svg" alt="" />
```

**Principe à retenir :**

> Une image informative doit avoir un texte alternatif ; une image purement décorative ne doit pas transmettre une information inutile au lecteur d'écran.

---

## 9. Accessibilité des champs de formulaire

Chaque champ de formulaire doit avoir un `label` associé.

Le label doit être techniquement relié au champ correspondant.

### Acceptable

```tsx
<label htmlFor="email">
  Adresse e-mail
</label>

<input
  id="email"
  name="email"
  type="email"
/>
```

### Interdit

```tsx
<input
  name="email"
  placeholder="Adresse e-mail"
/>
```

Le `placeholder` ne remplace pas le `label`.

### Principe à retenir

> Tout champ de formulaire doit être identifiable par un label associé.

---

## 10. Accessibilité et intitulé des boutons

Chaque bouton doit posséder un intitulé explicite permettant de comprendre son action.

L'utilisateur doit pouvoir identifier la fonction du bouton sans devoir interpréter uniquement une icône ou son contexte visuel.

### Acceptable

```tsx
<button type="submit">
  Valider la commande
</button>
```

### Interdit

```tsx
<button type="submit">
  ...
</button>
```

lorsque `...` ne fournit aucune information accessible sur l'action.

### Interdit

Utiliser uniquement une icône comme représentation de l'action sans fournir de nom accessible explicite.

### Principe à retenir

> Chaque bouton doit exposer une action explicitement identifiable.

---

## 11. Tests des écrans

**Tout écran frontend doit disposer d'au moins un test.**

Un même écran peut naturellement nécessiter plusieurs tests. La règle signifie qu'aucun écran ne doit être dépourvu de couverture de test.

Les tests doivent être réalisés avec :

* **Vitest** ;
* **Testing Library**.

Le réseau doit être simulé avec **MSW**.

Les hooks frontend ne doivent pas être mockés pour contourner leur fonctionnement réel.

### Couverture minimale

Pour chaque écran, les tests doivent couvrir au minimum :

1. **le cas nominal** ;
2. **l'état d'erreur** ;
3. **l'interaction principale de l'écran**.

### Cas nominal

Vérifier que l'écran fonctionne correctement lorsque les données attendues sont reçues.

### Acceptable

```text
L'écran reçoit une réponse valide
→ les données sont affichées correctement.
```

### État d'erreur

Vérifier que l'écran se comporte correctement lorsque la requête échoue.

### Acceptable

```text
L'API retourne une erreur
→ l'écran affiche le message d'erreur attendu.
```

### Interaction principale

Vérifier l'action principale réalisée par l'utilisateur sur l'écran.

### Acceptable

```text
L'utilisateur clique sur "Ajouter au panier"
→ le comportement attendu est déclenché.
```

---

## 12. Simulation réseau dans les tests

La simulation du réseau doit être réalisée avec **MSW**.

Les tests doivent conserver les mécanismes frontend réels et simuler uniquement la communication avec le backend.

### Acceptable

```text
Écran réel
→ logique frontend réelle
→ hook réel
→ appel API
→ MSW
→ réponse simulée
```

### Interdit

Remplacer directement le hook testé par un mock afin de contrôler artificiellement les données reçues par le composant.

### Interdit

```ts
vi.mock("./useProducts");
```

lorsque ce mock sert à éviter de tester le fonctionnement réel du hook et de la communication frontend avec l'API.

### Principe à retenir

> On simule le réseau, pas le comportement des hooks que l'on cherche à tester.

---

## 13. Vérification du fonctionnement global après l'ajout d'un écran ou d'une feature

Après l'ajout d'un nouvel écran ou d'une nouvelle feature frontend, il faut s'assurer que **l'application existante continue de fonctionner correctement**.

L'ajout d'un nouvel écran ou d'une nouvelle feature ne doit pas introduire de régression dans les fonctionnalités existantes.

La vérification doit porter sur le fonctionnement de l'application dans son ensemble, et pas uniquement sur le nouvel élément ajouté.

### Acceptable

Après l'ajout d'un nouvel écran :

```text
Nouvel écran → fonctionne
Écrans existants → fonctionnent toujours
Fonctionnalités existantes → fonctionnent toujours
Tests existants → restent valides
```

### Interdit

Considérer la feature comme terminée simplement parce que le nouvel écran fonctionne, alors qu'elle a cassé un écran ou une fonctionnalité existante.

### Principe à retenir

> Toute nouvelle feature doit s'intégrer à l'application existante sans régression.

---

# Synthèse des règles obligatoires

Le frontend doit donc respecter les principes suivants :

1. **Développer par composants et favoriser la réutilisation réelle.**
2. **Ne mutualiser un composant qu'à partir de son deuxième usage réel.**
3. **N'utiliser aucun emoji dans le code ou les tests.**
4. **Ne jamais inventer de données métier dans le frontend.**
5. **Autoriser les données fictives uniquement lorsqu'elles sont nécessaires aux tests.**
6. **Afficher les données métier fournies par le backend sans les réinventer.**
7. **Utiliser le PascalCase pour les noms de fichiers frontend, sauf conventions techniques imposant les minuscules.**
8. **Utiliser le français pour tous les textes produits par l'interface frontend.**
9. **Afficher les dates dans un format français.**
10. **Fournir un `alt` pour chaque image informative.**
11. **Associer un `label` à chaque champ de formulaire.**
12. **Donner un intitulé explicite à chaque bouton.**
13. **Fournir au minimum un test pour chaque écran.**
14. **Couvrir au minimum le cas nominal, l'erreur et l'interaction principale de chaque écran.**
15. **Utiliser Vitest et Testing Library pour les tests.**
16. **Simuler le réseau avec MSW et non les hooks eux-mêmes.**
17. **Vérifier que l'ajout d'un écran ou d'une feature ne provoque aucune régression dans l'application existante.**
