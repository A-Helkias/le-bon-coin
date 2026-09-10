import { Route, Routes } from 'react-router'

import CatalogPage from './pages/CatalogPage'
import ProductPage from './pages/ProductPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<CatalogPage />} />
      <Route path="/produits/:productId" element={<ProductPage />} />
    </Routes>
  )
}
