import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorBoundary } from './components/ErrorBoundary'

console.log("Main.tsx starting execution");
const rootElement = document.getElementById('root');
console.log("Root element found:", rootElement);

if (!rootElement) {
    console.error("FATAL: Root element missing!");
} else {
    createRoot(rootElement).render(
        <StrictMode>
            <ErrorBoundary>
                <App />
            </ErrorBoundary>
        </StrictMode>,
    )
}
