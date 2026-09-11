"""Fill a local database with a catalogue large enough to exercise the shop.

Development tool, run on demand:

    uv run python -m scripts.seed

Idempotent — a SKU already present is left alone rather than duplicated — and it
refuses to run against anything but a local database. A seeding script that
overwrites production is a classic accident; the guard below is the cheap
insurance against it.
"""

import asyncio
import sys
from typing import Any

from app.core.config import settings
from app.core.database import SessionLocal
from app.repositories import product as product_repo
from app.schemas.product import ProductCreate

LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1", "db")

PHOTO = "https://images.unsplash.com/photo-{id}?w=900&q=80"

CATALOGUE: list[dict[str, Any]] = [
    # --- Assises -------------------------------------------------------------
    {
        "sku": "ASS-001",
        "name": "Chaise en chêne massif",
        "category": "Assises",
        "description": "Assise en paille tressée à la main, piètement assemblé à tenon-mortaise.",
        "image_url": PHOTO.format(id="1503602642458-232111445657"),
        "price_cents": 14900,
        "stock": 12,
    },
    {
        "sku": "ASS-002",
        "name": "Tabouret de bar en frêne",
        "category": "Assises",
        "description": "Hauteur d'assise 75 cm, repose-pieds en acier brossé.",
        "image_url": PHOTO.format(id="1503602642458-232111445657"),
        "price_cents": 8900,
        "stock": 3,
    },
    {
        "sku": "ASS-003",
        "name": "Fauteuil lounge en cuir",
        "category": "Assises",
        "description": "Cuir pleine fleur patiné, structure en noyer, coussins garnis de plume.",
        "image_url": PHOTO.format(id="1567538096630-e0c55bd6374c"),
        "price_cents": 129000,
        "stock": 2,
    },
    {
        "sku": "ASS-004",
        "name": "Banc d'entrée en pin",
        "category": "Assises",
        "description": "Deux places, casier de rangement sous l'assise.",
        "image_url": None,
        "price_cents": 11900,
        "stock": 0,
    },
    {
        "sku": "ASS-005",
        "name": "Canapé trois places en lin",
        "category": "Assises",
        "description": "Housse déhoussable et lavable, coloris sable.",
        "image_url": PHOTO.format(id="1555041469-a586c61ea9bc"),
        "price_cents": 189000,
        "stock": 1,
    },
    # --- Tables --------------------------------------------------------------
    {
        "sku": "TAB-001",
        "name": "Table basse en noyer",
        "category": "Tables",
        "description": "Plateau d'une seule pièce, bord vivant conservé et huilé.",
        "image_url": PHOTO.format(id="1533090161767-e6ffed986c88"),
        "price_cents": 48900,
        "stock": 4,
    },
    {
        "sku": "TAB-002",
        "name": "Table de salle à manger, six couverts",
        "category": "Tables",
        "description": "Chêne huilé, 180 x 90 cm, allonge centrale de 50 cm.",
        "image_url": PHOTO.format(id="1617806118233-18e1de247200"),
        "price_cents": 89000,
        "stock": 2,
    },
    {
        "sku": "TAB-003",
        "name": "Bureau plat en hêtre",
        "category": "Tables",
        "description": "Deux tiroirs à glissières bois, passe-câbles intégré.",
        "image_url": PHOTO.format(id="1518455027359-f3f8164ba6bd"),
        "price_cents": 42900,
        "stock": 6,
    },
    {
        "sku": "TAB-004",
        "name": "Console d'entrée étroite",
        "category": "Tables",
        "description": "Profondeur 28 cm, pensée pour un couloir.",
        "image_url": None,
        "price_cents": 24900,
        "stock": 7,
    },
    {
        "sku": "TAB-005",
        "name": "Guéridon en marbre",
        "category": "Tables",
        "description": "Plateau Carrare, piètement laiton brossé.",
        "image_url": PHOTO.format(id="1540574163026-643ea20ade25"),
        "price_cents": 34900,
        "stock": 5,
    },
    # --- Rangements ----------------------------------------------------------
    {
        "sku": "RAN-001",
        "name": "Étagère modulaire en frêne",
        "category": "Rangements",
        "description": "Quatre modules empilables, montage sans outil.",
        "image_url": PHOTO.format(id="1594620302200-9a762244a156"),
        "price_cents": 22900,
        "stock": 14,
    },
    {
        "sku": "RAN-002",
        "name": "Bibliothèque murale, six niveaux",
        "category": "Rangements",
        "description": "Fixation invisible, charge admissible 40 kg par tablette.",
        "image_url": PHOTO.format(id="1507473885765-e6ed057f782c"),
        "price_cents": 67900,
        "stock": 3,
    },
    {
        "sku": "RAN-003",
        "name": "Commode quatre tiroirs",
        "category": "Rangements",
        "description": "Façades en chêne, coulisses à fermeture douce.",
        "image_url": PHOTO.format(id="1595428774223-ef52624120d2"),
        "price_cents": 54900,
        "stock": 4,
    },
    {
        "sku": "RAN-004",
        "name": "Vaisselier vitré",
        "category": "Rangements",
        "description": "Verre trempé, éclairage intérieur en option.",
        "image_url": None,
        "price_cents": 78900,
        "stock": 0,
    },
    {
        "sku": "RAN-005",
        "name": "Casier à vin, douze bouteilles",
        "category": "Rangements",
        "description": "Pin massif non traité, empilable.",
        "image_url": PHOTO.format(id="1510812431401-41d2bd2722f3"),
        "price_cents": 7900,
        "stock": 21,
    },
    # --- Luminaires ----------------------------------------------------------
    {
        "sku": "LUM-001",
        "name": "Lampe d'atelier articulée",
        "category": "Luminaires",
        "description": "Bras acier, abat-jour émaillé. Restaurée, câblage neuf.",
        "image_url": PHOTO.format(id="1507473885765-e6ed057f782c"),
        "price_cents": 8900,
        "stock": 0,
    },
    {
        "sku": "LUM-002",
        "name": "Suspension en rotin tressé",
        "category": "Luminaires",
        "description": "Diamètre 45 cm, douille E27, câble textile de 2 m.",
        "image_url": PHOTO.format(id="1513506003901-1e6a229e2d15"),
        "price_cents": 12900,
        "stock": 9,
    },
    {
        "sku": "LUM-003",
        "name": "Lampadaire trépied en noyer",
        "category": "Luminaires",
        "description": "Hauteur réglable de 140 à 175 cm, variateur au pied.",
        "image_url": PHOTO.format(id="1573225342350-16731dd9bf3d"),
        "price_cents": 19900,
        "stock": 6,
    },
    {
        "sku": "LUM-004",
        "name": "Applique murale en laiton",
        "category": "Luminaires",
        "description": "Orientable, finition laiton non verni qui se patine.",
        "image_url": PHOTO.format(id="1524634126442-357e0eac3c14"),
        "price_cents": 6900,
        "stock": 18,
    },
    {
        "sku": "LUM-005",
        "name": "Lampe de chevet en céramique",
        "category": "Luminaires",
        "description": "Émail craquelé, chaque pièce est unique.",
        "image_url": PHOTO.format(id="1507473885765-e6ed057f782c"),
        "price_cents": 5900,
        "stock": 2,
    },
    # --- Textiles ------------------------------------------------------------
    {
        "sku": "TEX-001",
        "name": "Tapis en laine tuftée",
        "category": "Textiles",
        "description": "200 x 300 cm, laine de Nouvelle-Zélande, motif géométrique.",
        "image_url": PHOTO.format(id="1600166898405-da9535204843"),
        "price_cents": 89000,
        "stock": 3,
    },
    {
        "sku": "TEX-002",
        "name": "Plaid en mohair",
        "category": "Textiles",
        "description": "130 x 180 cm, tissé en Écosse.",
        "image_url": PHOTO.format(id="1580301762395-83179d1e7d05"),
        "price_cents": 14900,
        "stock": 11,
    },
    {
        "sku": "TEX-003",
        "name": "Coussin en velours côtelé",
        "category": "Textiles",
        "description": "45 x 45 cm, garnissage plumes, housse zippée.",
        "image_url": PHOTO.format(id="1584100936595-c0654b55a2e2"),
        "price_cents": 3900,
        "stock": 34,
    },
    {
        "sku": "TEX-004",
        "name": "Rideaux occultants en lin lavé",
        "category": "Textiles",
        "description": "Paire, 140 x 260 cm, œillets métal.",
        "image_url": None,
        "price_cents": 11900,
        "stock": 8,
    },
    # --- Objets --------------------------------------------------------------
    {
        "sku": "OBJ-001",
        "name": "Miroir rond en chêne",
        "category": "Objets",
        "description": "Diamètre 70 cm, verre biseauté.",
        "image_url": PHOTO.format(id="1618220179428-22790b461013"),
        "price_cents": 16900,
        "stock": 7,
    },
    {
        "sku": "OBJ-002",
        "name": "Vase en grès émaillé",
        "category": "Objets",
        "description": "Tourné à la main, hauteur 28 cm.",
        "image_url": PHOTO.format(id="1578500494198-246f612d3b3d"),
        "price_cents": 4900,
        "stock": 16,
    },
    {
        "sku": "OBJ-003",
        "name": "Horloge murale en bois",
        "category": "Objets",
        "description": "Diamètre 32 cm, mouvement silencieux.",
        "image_url": PHOTO.format(id="1563861826100-9cb868fdbe1c"),
        "price_cents": 5900,
        "stock": 12,
    },
    {
        "sku": "OBJ-004",
        "name": "Corbeille en osier",
        "category": "Objets",
        "description": "Osier brut, deux poignées, hauteur 40 cm.",
        "image_url": PHOTO.format(id="1595341888016-a392ef81b7de"),
        "price_cents": 3900,
        "stock": 23,
    },
    {
        "sku": "OBJ-005",
        "name": "Porte-revues en cuir",
        "category": "Objets",
        "description": "Cuir végétal, coutures apparentes.",
        "image_url": PHOTO.format(id="1550226891-ef816aed4a98"),
        "price_cents": 8900,
        "stock": 1,
    },
]


def _refuse_if_not_local() -> None:
    url = settings.database_url
    if not any(f"@{host}" in url or f"@{host}:" in url for host in LOCAL_HOSTS):
        print(f"Refus : DATABASE_URL ne pointe pas sur une base locale.\n  {url}", file=sys.stderr)
        raise SystemExit(1)


async def seed() -> None:
    _refuse_if_not_local()

    created = 0
    skipped = 0
    async with SessionLocal() as session:
        for entry in CATALOGUE:
            existing = await product_repo.get_by_sku(session, entry["sku"])
            if existing is not None:
                skipped += 1
                continue
            await product_repo.create(session, ProductCreate(**entry))
            created += 1
        await session.commit()

        total = await product_repo.count(session)
        categories = await product_repo.list_categories(session)

    print(f"{created} article(s) créé(s), {skipped} déjà présent(s).")
    print(f"Catalogue : {total} articles actifs, rayons : {', '.join(categories)}.")


if __name__ == "__main__":
    asyncio.run(seed())
