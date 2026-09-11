import { Route, Routes } from 'react-router'

import SiteHeader from './components/SiteHeader'
import CartPage from './pages/CartPage'
import CatalogPage from './pages/CatalogPage'
import CheckoutPage from './pages/CheckoutPage'
import OrderConfirmationPage from './pages/OrderConfirmationPage'
import ProductPage from './pages/ProductPage'

export default function App() {
  return (
    <>
      <SiteHeader />
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/produits/:productId" element={<ProductPage />} />
        <Route path="/panier" element={<CartPage />} />
        <Route path="/commande" element={<CheckoutPage />} />
        <Route path="/commande/:orderId" element={<OrderConfirmationPage />} />
      </Routes>
    </>
  )
}
