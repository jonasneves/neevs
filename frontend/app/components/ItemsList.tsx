import { ItemsClient } from './ItemsClient'

interface Item {
  id: number
  title: string
  description: string
  created_at: string
  updated_at: string
}

async function getItems(): Promise<Item[]> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'
    const res = await fetch(`${apiUrl}/api/items`, {
      cache: 'no-store',
    })
    if (!res.ok) return []
    return res.json()
  } catch (error) {
    console.error('Failed to fetch items:', error)
    return []
  }
}

export async function ItemsList() {
  const initialItems = await getItems()

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Items</h2>
      </div>
      <ItemsClient initialItems={initialItems} />
    </div>
  )
}
