import { Button } from '@sprint-radar/ui'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-5xl font-bold text-gray-900 dark:text-gray-50 mb-6">
          Sprint Radar
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-8">
          High-performance agile analytics and forecasting platform
        </p>
        <div className="flex gap-4 justify-center">
          <Button variant="default" size="lg">
            View Reports
          </Button>
          <Button variant="outline" size="lg">
            Documentation
          </Button>
        </div>
      </div>
    </main>
  )
}