from uuid import uuid4

from httpx import AsyncClient

from tests.conftest import ProductFactory

UNKNOWN_ID = str(uuid4())

CUSTOMER = {
    "customer_email": "camille@example.com",
    "customer_name": "Camille Martin",
    "shipping_address": "12 rue des Lilas",
    "shipping_postal_code": "75011",
    "shipping_city": "Paris",
    "shipping_country": "FR",
}


async def cart_with(client: AsyncClient, product_id: str, quantity: int) -> str:
    cart_id = str((await client.post("/carts")).json()["id"])
    response = await client.post(
        f"/carts/{cart_id}/items",
        json={"product_id": product_id, "quantity": quantity},
    )
    assert response.status_code == 201
    return cart_id


async def order_from(client: AsyncClient, cart_id: str) -> dict[str, object]:
    response = await client.post("/orders", json={"cart_id": cart_id, **CUSTOMER})
    assert response.status_code == 201, response.text
    body: dict[str, object] = response.json()
    return body


async def test_create_order_freezes_the_lines(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(price_cents=2500, stock=10)
    cart_id = await cart_with(client, str(product.id), 2)

    body = await order_from(client, cart_id)

    assert body["status"] == "pending"
    assert body["total_cents"] == 5000
    items = body["items"]
    assert isinstance(items, list)
    assert items[0]["product_sku"] == product.sku
    assert items[0]["unit_price_cents"] == 2500
    assert items[0]["line_total_cents"] == 5000


async def test_create_order_consumes_the_cart(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    cart_id = await cart_with(client, str(product.id), 1)

    await order_from(client, cart_id)

    assert (await client.get(f"/carts/{cart_id}")).status_code == 404


async def test_create_order_decrements_stock(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    cart_id = await cart_with(client, str(product.id), 4)

    await order_from(client, cart_id)

    remaining = await client.get(f"/products/{product.id}")
    assert remaining.json()["stock"] == 6


async def test_order_keeps_its_price_after_the_product_is_repriced(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    """An order is a historical record: re-pricing the catalogue must not touch it."""
    product = await product_factory(price_cents=1000, stock=10)
    cart_id = await cart_with(client, str(product.id), 2)
    order = await order_from(client, cart_id)

    await client.patch(f"/products/{product.id}", json={"price_cents": 9999})

    reread = await client.get(f"/orders/{order['id']}")
    assert reread.json()["total_cents"] == 2000
    assert reread.json()["items"][0]["unit_price_cents"] == 1000


async def test_create_order_from_unknown_cart_returns_404(client: AsyncClient) -> None:
    response = await client.post("/orders", json={"cart_id": UNKNOWN_ID, **CUSTOMER})

    assert response.status_code == 404
    assert response.json()["detail"] == "Ce panier n'existe pas."


async def test_create_order_from_empty_cart_returns_422(client: AsyncClient) -> None:
    cart_id = str((await client.post("/carts")).json()["id"])

    response = await client.post("/orders", json={"cart_id": cart_id, **CUSTOMER})

    assert response.status_code == 422
    assert response.json()["detail"] == "Votre panier est vide."


async def test_create_order_beyond_stock_returns_409(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    """Stock can fall between filling the cart and checking out."""
    product = await product_factory(stock=10)
    cart_id = await cart_with(client, str(product.id), 5)
    await client.patch(f"/products/{product.id}", json={"stock": 2})

    response = await client.post("/orders", json={"cart_id": cart_id, **CUSTOMER})

    assert response.status_code == 409


async def test_create_order_with_deactivated_product_returns_422(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    cart_id = await cart_with(client, str(product.id), 1)
    await client.delete(f"/products/{product.id}")

    response = await client.post("/orders", json={"cart_id": cart_id, **CUSTOMER})

    assert response.status_code == 422


async def test_create_order_rejects_malformed_email(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    cart_id = await cart_with(client, str(product.id), 1)

    response = await client.post(
        "/orders",
        json={"cart_id": cart_id, **CUSTOMER, "customer_email": "pas-un-email"},
    )

    assert response.status_code == 422


async def test_list_orders_returns_paginated_envelope(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    await order_from(client, await cart_with(client, str(product.id), 1))

    response = await client.get("/orders")

    assert response.status_code == 200
    assert response.json()["total"] == 1


async def test_list_orders_filters_by_status(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    await order_from(client, await cart_with(client, str(product.id), 1))

    pending = await client.get("/orders", params={"status": "pending"})
    shipped = await client.get("/orders", params={"status": "shipped"})

    assert pending.json()["total"] == 1
    assert shipped.json()["total"] == 0


async def test_list_orders_rejects_limit_above_maximum(client: AsyncClient) -> None:
    response = await client.get("/orders", params={"limit": 201})

    assert response.status_code == 422


async def test_get_order_returns_it(client: AsyncClient, product_factory: ProductFactory) -> None:
    product = await product_factory(stock=10)
    order = await order_from(client, await cart_with(client, str(product.id), 1))

    response = await client.get(f"/orders/{order['id']}")

    assert response.status_code == 200
    assert response.json()["customer_name"] == "Camille Martin"


async def test_get_unknown_order_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/orders/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Cette commande n'existe pas."


async def test_pending_order_can_be_paid(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    order = await order_from(client, await cart_with(client, str(product.id), 1))

    response = await client.patch(f"/orders/{order['id']}", json={"status": "paid"})

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


async def test_pending_order_cannot_ship_directly(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    order = await order_from(client, await cart_with(client, str(product.id), 1))

    response = await client.patch(f"/orders/{order['id']}", json={"status": "shipped"})

    assert response.status_code == 422


async def test_cancelled_order_is_terminal(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    order = await order_from(client, await cart_with(client, str(product.id), 1))
    await client.patch(f"/orders/{order['id']}", json={"status": "cancelled"})

    response = await client.patch(f"/orders/{order['id']}", json={"status": "paid"})

    assert response.status_code == 422


async def test_cancelling_an_order_returns_the_stock(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    order = await order_from(client, await cart_with(client, str(product.id), 3))
    assert (await client.get(f"/products/{product.id}")).json()["stock"] == 7

    await client.patch(f"/orders/{order['id']}", json={"status": "cancelled"})

    assert (await client.get(f"/products/{product.id}")).json()["stock"] == 10


async def test_update_unknown_order_returns_404(client: AsyncClient) -> None:
    response = await client.patch(f"/orders/{UNKNOWN_ID}", json={"status": "paid"})

    assert response.status_code == 404


async def test_update_order_rejects_unknown_status(
    client: AsyncClient, product_factory: ProductFactory
) -> None:
    product = await product_factory(stock=10)
    order = await order_from(client, await cart_with(client, str(product.id), 1))

    response = await client.patch(f"/orders/{order['id']}", json={"status": "refunded"})

    assert response.status_code == 422
