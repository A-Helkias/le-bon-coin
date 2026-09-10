from uuid import uuid4

from httpx import AsyncClient

from tests.conftest import ProductFactory

UNKNOWN_ID = str(uuid4())


async def create_cart(client: AsyncClient) -> str:
    response = await client.post("/carts")
    assert response.status_code == 201
    return str(response.json()["id"])


async def test_create_cart_returns_an_empty_cart(client: AsyncClient) -> None:
    response = await client.post("/carts")

    assert response.status_code == 201
    body = response.json()
    assert body["items"] == []
    assert body["total_cents"] == 0
    assert body["user_id"] is None


async def test_get_cart_returns_it(client: AsyncClient) -> None:
    cart_id = await create_cart(client)

    response = await client.get(f"/carts/{cart_id}")

    assert response.status_code == 200
    assert response.json()["id"] == cart_id


async def test_get_unknown_cart_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/carts/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ce panier n'existe pas."


async def test_delete_cart_returns_204(client: AsyncClient) -> None:
    cart_id = await create_cart(client)

    response = await client.delete(f"/carts/{cart_id}")

    assert response.status_code == 204
    assert (await client.get(f"/carts/{cart_id}")).status_code == 404


async def test_delete_unknown_cart_returns_404(client: AsyncClient) -> None:
    response = await client.delete(f"/carts/{UNKNOWN_ID}")

    assert response.status_code == 404


async def test_add_item_prices_the_line(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(price_cents=1250, stock=10)
    cart_id = await create_cart(client)

    response = await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 3},
    )

    assert response.status_code == 201
    body = response.json()
    assert len(body["items"]) == 1
    line = body["items"][0]
    assert line["quantity"] == 3
    assert line["unit_price_cents"] == 1250
    assert line["line_total_cents"] == 3750
    assert body["total_cents"] == 3750


async def test_adding_the_same_product_twice_merges_the_line(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    """The unique constraint on (cart_id, product_id) must not surface as a 409."""
    product = await product_factory(stock=10)
    cart_id = await create_cart(client)
    body = {"product_id": str(product.id), "quantity": 2}

    await client.post(f"/carts/{cart_id}/items", json=body)
    response = await client.post(f"/carts/{cart_id}/items", json=body)

    assert response.status_code == 201
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 4


async def test_add_item_to_unknown_cart_returns_404(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory()

    response = await client.post(
        f"/carts/{UNKNOWN_ID}/items",
        json={"product_id": str(product.id), "quantity": 1},
    )

    assert response.status_code == 404


async def test_add_unknown_product_returns_404(client: AsyncClient) -> None:
    cart_id = await create_cart(client)

    response = await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": UNKNOWN_ID, "quantity": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Ce produit n'existe pas."


async def test_add_item_beyond_stock_returns_409(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=2)
    cart_id = await create_cart(client)

    response = await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 3},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Ce produit n'est plus disponible en quantité suffisante."


async def test_merged_quantity_is_checked_against_stock(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    """Each add fits in stock on its own; their sum does not."""
    product = await product_factory(stock=3)
    cart_id = await create_cart(client)
    body = {"product_id": str(product.id), "quantity": 2}

    await client.post(f"/carts/{cart_id}/items", json=body)
    response = await client.post(f"/carts/{cart_id}/items", json=body)

    assert response.status_code == 409


async def test_add_inactive_product_returns_422(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(is_active=False)
    cart_id = await create_cart(client)

    response = await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 1},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Ce produit n'est plus disponible à la vente."


async def test_add_item_rejects_zero_quantity(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory()
    cart_id = await create_cart(client)

    response = await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 0},
    )

    assert response.status_code == 422


async def test_set_item_quantity_replaces_it(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    cart_id = await create_cart(client)
    await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 3},
    )

    response = await client.patch(f"/carts/{cart_id}/items/{product.id}", json={"quantity": 5})

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 5


async def test_set_quantity_for_product_not_in_cart_returns_404(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory()
    cart_id = await create_cart(client)

    response = await client.patch(f"/carts/{cart_id}/items/{product.id}", json={"quantity": 2})

    assert response.status_code == 404
    assert response.json()["detail"] == "Ce produit n'est pas dans le panier."


async def test_set_quantity_beyond_stock_returns_409(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=4)
    cart_id = await create_cart(client)
    await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 1},
    )

    response = await client.patch(f"/carts/{cart_id}/items/{product.id}", json={"quantity": 9})

    assert response.status_code == 409


async def test_remove_item_returns_204(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory()
    cart_id = await create_cart(client)
    await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": str(product.id), "quantity": 1},
    )

    response = await client.delete(f"/carts/{cart_id}/items/{product.id}")

    assert response.status_code == 204
    cart = await client.get(f"/carts/{cart_id}")
    assert cart.json()["items"] == []
    assert cart.json()["total_cents"] == 0


async def test_remove_item_not_in_cart_returns_404(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory()
    cart_id = await create_cart(client)

    response = await client.delete(f"/carts/{cart_id}/items/{product.id}")

    assert response.status_code == 404
