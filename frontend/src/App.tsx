import './App.css'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  return (
    <main className="app">
      <h1>SmartLearn.AI</h1>
      <p>React + TypeScript frontend is initialized.</p>
      <p>
        Backend API URL: <code>{apiBaseUrl}</code>
      </p>
    </main>
  )
}

export default App
