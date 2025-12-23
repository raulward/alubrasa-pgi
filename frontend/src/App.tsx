
import { useState } from 'react';
import PricingPage from './features/pricing/PricingPage';
import ItemsPage from './features/items/ItemsPageSafe';
import ObrasPage from './features/obras/ObrasPageSafe';
import { AppSidebar } from './components/layout/AppSidebar';
// Icons mostly used in Sidebar but imported here to ensure they work
import { LayoutDashboard, Banknote, HardHat } from 'lucide-react';

function App() {
    const [page, setPage] = useState<'pricing' | 'items' | 'dashboard' | 'prices-check' | 'obras-control'>('pricing');

    return (
        <div className="min-h-screen bg-background font-sans flex text-foreground">
            {/* Sidebar Component */}
            <AppSidebar currentPage={page} onNavigate={setPage} />

            {/* Main Content Area */}
            <main className="flex-1 md:ml-64 transition-all duration-300">
                {/* Gradient Background */}
                <div className="fixed inset-0 -z-10 h-full w-full bg-background bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]">
                    <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary/20 opacity-20 blur-[100px]"></div>
                </div>

                <div className="container mx-auto p-4 md:p-8 pt-16 md:pt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {page === 'pricing' && <PricingPage />}
                    {page === 'obras-control' && <ObrasPage />}

                    {/* Inline Items Page Placeholder */}
                    {page === 'items' && <ItemsPage />}

                    {page === 'dashboard' && (
                        <div className="flex h-[80vh] items-center justify-center text-muted-foreground flex-col gap-4">
                            <div className="h-20 w-20 rounded-full bg-slate-100 flex items-center justify-center">
                                <LayoutDashboard className="h-10 w-10 text-slate-300" />
                            </div>
                            <p>Dashboard em construção...</p>
                        </div>
                    )}
                    {page === 'prices-check' && (
                        <div className="flex h-[80vh] items-center justify-center text-muted-foreground flex-col gap-4">
                            <div className="h-20 w-20 rounded-full bg-slate-100 flex items-center justify-center">
                                <Banknote className="h-10 w-10 text-slate-300" />
                            </div>
                            <p>Módulo de Consulta de Preço (Em breve)</p>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}

export default App;
