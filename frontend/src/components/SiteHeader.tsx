import { Link } from 'react-router'

import { useCart } from '../features/cart/api'

/** Shared by every screen: the shop's name, the way back, and the cart. */
export default function SiteHeader() {
  const { data: cart } = useCart()
  const count =
    cart?.items.reduce((total, item) => total + item.quantity, 0) ?? 0

  return (
    <header className="border-b border-plate">
      <div className="mx-auto flex max-w-5xl items-baseline justify-between px-6 py-5">
        <Link to="/" className="font-display text-lg leading-none">
          Le Bon Coin
        </Link>

        <Link to="/panier" className="text-sm text-accent">
          Panier
          {count > 0 ? (
            <span className="ml-2 bg-accent px-2 py-0.5 text-paper">
              {count}
            </span>
          ) : null}
        </Link>
      </div>
    </header>
  )
}
