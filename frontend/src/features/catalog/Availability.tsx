type Props = {
  stock: number
  /** Detail pages state the exact count; catalogue bands stay terse. */
  verbose?: boolean
}

/** Stock is a number, so say something useful with it rather than hide it. */
export default function Availability({ stock, verbose = false }: Props) {
  if (stock === 0) {
    return <span className="text-sm text-accent">Épuisé</span>
  }

  if (stock <= 3) {
    return (
      <span className="text-sm text-accent">
        {stock === 1 ? 'Dernière pièce' : `Plus que ${stock} pièces`}
      </span>
    )
  }

  return (
    <span className="text-sm text-mute">
      {verbose ? `En stock, ${stock} pièces` : 'En stock'}
    </span>
  )
}
