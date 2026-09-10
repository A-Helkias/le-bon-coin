---
name: frontend-design
description: Direction artistique pour toute interface du Bon Coin — nouvel écran React, refonte visuelle, page vitrine, maquette. Aide à choisir une palette, une typographie et une mise en page qui ne ressemblent pas à un template généré. À utiliser dès qu'il faut décider de l'apparence d'un écran (catalogue, fiche produit, panier, tunnel de commande, back-office), pas seulement de son câblage à l'API. Couvre aussi la structure du dossier de feature, les hooks TanStack Query et les tests de l'écran.
license: Complete terms in LICENSE.txt
source: anthropics/claude-plugins-official — plugins/frontend-design/skills/frontend-design
modifications: description traduite et adaptée au projet ; section « Contraintes Le Bon Coin » ajoutée en fin de fichier
---

# Frontend Design

Approach this as the design lead at a design studio known for giving every client a distinct visual identity that is not mistaken for anyone else's. This client has already rejected proposals that felt cliché or templated, and is paying for a distinctive point of view: make deliberate, opinionated choices about palette, typography, and layout that are specific to this brief, and take aesthetic risk if justified.

## Ground your designs in the subject matter

If the brief does not identify what the product or subject matter is, identify it yourself before designing, and confirm with the client. You can come up with one concrete subject, the design's audience, and the design's primary job, as a proposal. If there's any information in your memory about the client's preferences or context about what they're building, use that as a hint. The subject's industry, subject matter, materials, and vernacular are where distinctive visual choices come from — a design for a toy for girls aged 8–11 will be very aesthetically different from a dashboard for financial analysts. Build with the brief's real content and subject matter throughout.

## Design principles

For web designs, the hero is the first thing viewers will see. Open with the most characteristic thing in the subject's world, in the form that is most appropriate: a headline, an image, an animation, a live demo, an interactive moment, or other treatments. Be deliberate with your choice: a big number with a small label, supporting stats, and a gradient accent is the default treatment, so only use it if that's truly the best option.

Typography carries the personality of the page. You don't need a different typeface for display or headline text and body content: use one family or two, and if two, make them clearly distinct.

Choose your typefaces deliberately, not the default families you would reach for on any other project, and set a clear type scale following the default guidance of The Elements of Typographic Style with intentional weights, widths, and spacing. When type is used as a headline or visual element, use the type treatment itself as an active part of the design, not a neutral delivery vehicle for the content.

Default to line lengths of less than 80 characters. Serif typefaces can have slightly longer line lengths; give serif body text slightly more line-height than a sans-serif.

Avoid these default typographic treatments; they are the commonest tells of a generated page:
- Accenting just a single word or phrase in a headline, like putting one word in italic/bold or a different color.
- Using all caps for labels.
- Adding unnecessary typographic labels above content.

Visual structure is information. Structural devices like outlines, borders, numbering, eyebrows, dividers, labels, etc., encode useful information about the content rather than decorate it. Many generic designs use numbered markers (01 / 02 / 03), but that's only appropriate if the content actually is a sequence — like a stepped process or a timeline. Before adding numbered markers, check the content really is a sequence.

Use non-user-triggered motion sparingly and deliberately, only to draw attention. A single orchestrated moment — one page-load sequence or one reveal — lands better than scattered effects; fade-and-slide-up entrances on each section and hover transitions on every card are the generic default and read as AI-generated. Motion that answers a person's action (opening, expanding, confirming) is welcome when it shows what changed.

Consider written content carefully. Often a design brief may not contain real content, and it's up to you to come up with copy and placeholder content. Copy can make a design feel as templated as the design itself. See the below section on writing for more guidance.

## Process: plan, review against the brief, build, critique

For calibration, AI-generated design right now clusters around some traits:
1. a warm cream background (near #F4F1EA) with a high-contrast serif display and a terracotta or warm-clay accent (often near #D97757 — Anthropic's own Claude-interaction accent, so on a user's brief it reads as a tell);
2. a near-black background with a single bright acid-green or vermilion accent;
3. a broadsheet-style layout with hairline rules, zero border-radius, and dense newspaper-like columns;
4. the SaaS-card kit: content chopped into identical rounded cards, one border-radius on everything regardless of hierarchy, the same soft grey shadow (rgba(0,0,0,.1)) under each, and gradient washes as decoration;
5. template chrome that appears whatever the subject: a tracked-out ALL-CAPS eyebrow label above every heading; meta strings joined with middle dots ('A · B · C'); labels built as 'WORD — fragment' with a spaced em dash; tinted near-black (#0B0B0B, #111) standing in for black; a monospace face for small data labels; a '→' appended to link and button text.

All traits are legitimate for some briefs, but they are defaults rather than choices, and they appear regardless of subject. Where the brief pins down a visual direction, follow it exactly — the brief's own words always win, including when it asks for one of these looks. Where it leaves an axis free, don't spend that freedom on one of these defaults. As with a hired human designer, there's often a careful balance between doing what you're good at and taking each project as a chance to experiment and learn.

Work in two passes. First, brainstorm a short design plan based on the client's design brief: create a compact token system with color, type, layout, and principles.
- Color: describe the core base palette as 4–6 named hex values.
- Type: the typefaces and their roles.
- Layout: a layout concept, using one-sentence prose descriptions and ASCII wireframes to ideate and compare. Include alignment guidance; should the content be left aligned, center aligned, justified?
- Principles: the high-level guidance for what makes this page unique.

Then review that plan against the brief before building: if any part of it reads like the generic default you would produce for any similar page (work through a similar prompt to see if you arrive somewhere similar) rather than a choice made for this specific brief — revise that part, say what you changed and why. Only after you've confirmed the relative uniqueness of your design plan should you start to write the code, following the revised plan.

When writing the code, be careful of structuring your CSS selector specificities. It's easy to generate CSS classes that cancel each other out (especially with a type-based selector like .section and an element-based selector like .cta). This can happen often with padding/margin between sections.

## Restraint and self-critique

Spend your boldness in one place. Let one element be the memorable thing, keep everything around it quiet and disciplined, and cut any decoration that does not serve the brief. Build to a quality floor without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, visually accessible, harmonious color palettes. Critique your own work as you build, taking screenshots to review if your environment supports it — a picture is worth 1000 tokens. Consider Chanel's advice: before leaving the house, take a look in the mirror and remove one accessory. Human creatives have memory and always try to do something new, so if you have a space to quickly jot down notes about what you've tried, it can help you in future passes.

## More on writing in design

Words appear in a design for one reason: to make it easier to understand and use. They are design content, not decoration. Bring the same intentionality and minimalism to copywriting that you would bring to spacing and color. Before writing anything, ask what the design needs to say, and how it can best be said to help the person navigate the experience.

Write from the end user's perspective. Name things by what users will understand in simple language, not by how the system is built. A user manages notifications, not webhook config. Describe what something is or does in plain terms rather than selling it. Being specific and legible to new users is always better than being clever.

Use active voice as default. A CTA says exactly what happens when it is used: "Save changes," not "Submit." An action keeps the same name through the whole flow, so the button that says "Publish" produces a toast that says "Published." The vocabulary of an interface is the signposting for someone navigating the product. Cohesion and consistency are how people learn their way around.

Treat failure and emptiness as moments for direction, not mood. Explain what went wrong and how to fix it, in the interface's voice rather than a person's. Errors don't apologize, and they are never vague about what happened. An empty screen is an invitation to act.

Keep the tone conversational: plain verbs, sentence case, no filler, with tone matched to the brand and the audience. Let each written element do exactly one job.


---

## Contraintes Le Bon Coin

*Section ajoutée au skill d'origine. Elle ne remplace rien de ce qui précède : elle borne le terrain de jeu.*

Ce qui suit prime sur toute proposition esthétique. Une direction artistique qui viole une de ces contraintes est à revoir, pas à négocier.

### Ce que la direction artistique ne décide pas

- **Les libellés sont en français**, les identifiants en anglais — voir `.claude/rules/naming-and-language.md`. La copie proposée par ce skill est du texte affiché : elle est donc en français, y compris les CTA, les états vides et les messages d'erreur.
- **Aucun emoji**, ni dans l'interface, ni dans le code, ni dans les tests. Un pictogramme se fait en SVG avec un `aria-label`, pas avec un caractère emoji.
- **Aucune donnée métier inventée.** Les maquettes et les écrans affichent ce que renvoie le backend. Pas de produit fictif, pas de prix de remplissage, pas de `?? 19.99`. Si le contenu réel manque pour juger d'une mise en page, dis-le et demande le contrat d'API — l'agent `api-explorer` le cartographie.
- **Les prix arrivent en centimes** et passent par `formatPrice` de `src/lib/format.ts`. Une maquette qui écrit un prix en dur écrit un prix formaté par cette fonction.

### Ce que la direction artistique doit couvrir

Le skill parle de « quality floor ». Ici, il est explicite. Tout écran branché sur l'API se dessine dans ses **quatre états** : chargement, erreur, vide, nominal. L'état vide et l'état d'erreur se conçoivent, ils ne se subissent pas — ce sont des écrans à part entière, avec une direction et une action, pas une liste vide silencieuse.

Accessibilité, non négociable : chaque image produit a un `alt`, chaque champ de formulaire un `label` associé, chaque bouton un intitulé explicite, le focus clavier reste visible, `prefers-reduced-motion` est respecté.

### Le cadre technique

- **Tailwind v4** est le moteur de style du projet. Les tokens du plan de design (couleurs, échelle typographique, rythme d'espacement) se déclarent dans le bloc `@theme` de `src/index.css`, pas en CSS parallèle ni en styles inline dispersés. Il n'y a pas de `tailwind.config.ts` : la configuration est CSS-first. La mise en garde du skill sur les spécificités CSS qui s'annulent se traduit ici en : une seule source pour un espacement donné.
- **Les typographies** se chargent en local (`src/assets/fonts`), pas depuis un CDN tiers. Deux familles au maximum, conformément au skill.
- **Un composant ne monte dans `src/components/` qu'au deuxième usage réel.** Un système visuel n'est pas une excuse pour créer une bibliothèque de composants génériques par anticipation — voir `.claude/rules/frontend.md`.
- **Les fichiers sont en PascalCase** : `ProductCard.tsx`, `CartSummary.tsx`.

### L'ordre de travail

1. Le plan de design d'abord — palette, typographies, mise en page, principes — soumis et validé avant la moindre ligne de code, comme l'exige `.claude/rules/workflow.md` pour toute tâche qui touche plus de deux fichiers.
2. La structure ensuite — dossier de feature, hooks TanStack Query, invalidation des clés — selon `.claude/rules/frontend.md`. Ce skill couvre les deux : l'apparence **et** le câblage.
3. `/check front` au vert, et un test par écran couvrant le cas nominal, l'état d'erreur et l'interaction principale.
