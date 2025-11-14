import { ItemsList } from './components/ItemsList'

interface HealthResponse {
  status: string
  database: string
  time: string
}

async function getHealth(): Promise<HealthResponse | null> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001'
    const res = await fetch(`${apiUrl}/api/health`, {
      cache: 'no-store',
    })
    if (!res.ok) return null
    return res.json()
  } catch (error) {
    console.error('Health check failed:', error)
    return null
  }
}

export default async function Home() {
  const health = await getHealth()

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <header className="mb-12">
          <h1 className="text-4xl font-bold mb-4 text-blue-600">
            🚀 Neevs Full Stack Demo
          </h1>
          <p className="text-gray-600 mb-6">
            Next.js 14 + Go (Fiber) + PostgreSQL
          </p>

          {/* Health Status */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">System Status</h2>
            {health ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                  <span className="font-medium">API:</span>
                  <span className="text-green-600">{health.status}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${
                    health.database === 'connected' ? 'bg-green-500' : 'bg-red-500'
                  }`}></span>
                  <span className="font-medium">Database:</span>
                  <span className={health.database === 'connected' ? 'text-green-600' : 'text-red-600'}>
                    {health.database}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-medium">Last Check:</span>
                  <span className="text-gray-600 text-sm">
                    {new Date(health.time).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-red-600">
                <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                <span>Unable to connect to backend API</span>
              </div>
            )}
          </div>
        </header>

        {/* Items Section */}
        <ItemsList />
      </div>
    </main>
  )
}
