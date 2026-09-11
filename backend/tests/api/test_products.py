from uuid import uuid4

from httpx import AsyncClient

from tests.conftest import ProductFactory

UNKNOWN_ID = str(uuid4())


def payload(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "sku": "CHAISE-001",
        "name": "Chaise en chêne",
        "description": "Assise en paille tressée.",
        "price_cents": 12900,
        "stock": 4,
    }
    body.update(overrides)
    return body


async def test_list_products_returns_paginated_envelope(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory()
    await product_factory()

    response = await client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_list_products_hides_inactive_by_default(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory()
    await product_factory(is_active=False)

    visible = await client.get("/products")
    everything = await client.get("/products", params={"include_inactive": True})

    assert visible.json()["total"] == 1
    assert everything.json()["total"] == 2


async def test_list_products_applies_offset(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory()
    await product_factory()

    response = await client.get("/products", params={"limit": 1, "offset": 1})

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["total"] == 2


async def test_list_products_rejects_limit_above_maximum(client: AsyncClient) -> None:
    response = await client.get("/products", params={"limit": 201})

    assert response.status_code == 422


async def test_get_product_returns_it(client: AsyncClient, product_factory: ProductFactory) -> None:
    product = await product_factory(name="Table basse", price_cents=24900)

    response = await client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Table basse"
    assert response.json()["price_cents"] == 24900


async def test_get_unknown_product_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/products/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ce produit n'existe pas."


async def test_create_product_returns_201(client: AsyncClient) -> None:
    response = await client.post("/products", json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "CHAISE-001"
    assert body["is_active"] is True
    assert body["id"]


async def test_create_product_rejects_duplicate_sku(client: AsyncClient) -> None:
    await client.post("/products", json=payload())

    response = await client.post("/products", json=payload(name="Autre chaise"))

    assert response.status_code == 409
    assert response.json()["detail"] == "Un produit porte déjà cette référence."


async def test_create_product_rejects_negative_price(client: AsyncClient) -> None:
    response = await client.post("/products", json=payload(price_cents=-1))

    assert response.status_code == 422


async def test_update_product_changes_fields(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(price_cents=1000)

    response = await client.patch(f"/products/{product.id}", json={"price_cents": 1500})

    assert response.status_code == 200
    assert response.json()["price_cents"] == 1500


async def test_update_unknown_product_returns_404(client: AsyncClient) -> None:
    response = await client.patch(f"/products/{UNKNOWN_ID}", json={"price_cents": 1500})

    assert response.status_code == 404


async def test_update_product_rejects_sku_taken_by_another(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    first = await product_factory(sku="AAA-111")
    second = await product_factory(sku="BBB-222")

    response = await client.patch(f"/products/{second.id}", json={"sku": first.sku})

    assert response.status_code == 409


async def test_delete_product_deactivates_it(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory()

    response = await client.delete(f"/products/{product.id}")

    assert response.status_code == 204
    still_there = await client.get(f"/products/{product.id}")
    assert still_there.status_code == 200
    assert still_there.json()["is_active"] is False


async def test_delete_unknown_product_returns_404(client: AsyncClient) -> None:
    response = await client.delete(f"/products/{UNKNOWN_ID}")

    assert response.status_code == 404


async def test_create_product_carries_its_image(client: AsyncClient) -> None:
    url = "https://cdn.example.com/chaise-chene.jpg"

    response = await client.post("/products", json=payload(image_url=url))

    assert response.status_code == 201
    assert response.json()["image_url"] == url


async def test_product_without_image_reads_back_as_null(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    """A product can be listed before it has been photographed."""
    product = await product_factory()

    response = await client.get(f"/products/{product.id}")

    assert response.status_code == 200
    assert response.json()["image_url"] is None


async def test_search_matches_the_name(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(name="Chaise en chêne")
    await product_factory(name="Table basse")

    response = await client.get("/products", params={"q": "chaise"})

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["name"] == "Chaise en chêne"


async def test_search_matches_the_reference(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(sku="LUM-042")
    await product_factory(sku="TAB-007")

    response = await client.get("/products", params={"q": "lum"})

    assert response.json()["total"] == 1
    assert response.json()["items"][0]["sku"] == "LUM-042"


async def test_search_without_result_returns_an_empty_page(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(name="Chaise en chêne")

    response = await client.get("/products", params={"q": "aspirateur"})

    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0}


async def test_total_counts_the_filtered_set_not_the_catalogue(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    """The classic bug: items filtered, total computed on everything."""
    await product_factory(name="Chaise en chêne")
    await product_factory(name="Table basse")
    await product_factory(name="Tabouret")

    response = await client.get("/products", params={"q": "table"})

    body = response.json()
    assert body["total"] == len(body["items"]) == 1


async def test_filter_by_category(client: AsyncClient, product_factory: ProductFactory) -> None:
    await product_factory(category="Assises")
    await product_factory(category="Assises")
    await product_factory(category="Tables")

    response = await client.get("/products", params={"category": "Assises"})

    assert response.json()["total"] == 2


async def test_sort_by_price_ascending(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(price_cents=3000)
    await product_factory(price_cents=1000)
    await product_factory(price_cents=2000)

    response = await client.get("/products", params={"sort": "price_asc"})

    prices = [item["price_cents"] for item in response.json()["items"]]
    assert prices == [1000, 2000, 3000]


async def test_sort_by_price_descending(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(price_cents=3000)
    await product_factory(price_cents=1000)

    response = await client.get("/products", params={"sort": "price_desc"})

    prices = [item["price_cents"] for item in response.json()["items"]]
    assert prices == [3000, 1000]


async def test_unknown_sort_is_rejected(client: AsyncClient) -> None:
    response = await client.get("/products", params={"sort": "cheapest"})

    assert response.status_code == 422


async def test_categories_lists_the_aisles(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(category="Tables")
    await product_factory(category="Assises")
    await product_factory(category="Assises")
    await product_factory(category=None)

    response = await client.get("/products/categories")

    assert response.status_code == 200
    assert response.json() == ["Assises", "Tables"]


async def test_categories_ignores_products_off_sale(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    await product_factory(category="Tables")
    await product_factory(category="Luminaires", is_active=False)

    response = await client.get("/products/categories")

    assert response.json() == ["Tables"]
