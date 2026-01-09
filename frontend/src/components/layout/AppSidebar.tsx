
import {
    Briefcase,
    Banknote,
    HardHat,
    Menu,
    ChevronRight,
    ChevronDown,
    LayoutDashboard
} from "lucide-react";
import { cn } from "@/lib/utils";

type Page = 'pricing' | 'items' | 'dashboard' | 'prices-check' | 'obras-control' | 'dashboard-obras';

interface AppSidebarProps {
    currentPage: Page;
    onNavigate: (page: Page) => void;
}

export function AppSidebar({ currentPage, onNavigate }: AppSidebarProps) {
    // Simplified State - Expand all for now or simple local state if needed
    // For MVP fix, just list links.

    const MenuItem = ({
        active,
        icon: Icon,
        label,
        onClick
    }: {
        active: boolean;
        icon: any;
        label: string;
        onClick: () => void;
    }) => (
        <button
            onClick={onClick}
            className={cn(
                "flex items-center w-full px-3 py-2 text-sm font-medium transition-colors rounded-md",
                active
                    ? "bg-primary/10 text-primary hover:bg-primary/20"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
        >
            <Icon className="h-4 w-4 mr-2" />
            {label}
        </button>
    );

    return (
        <aside className="hidden md:flex w-64 flex-col border-r bg-card text-card-foreground h-screen fixed left-0 top-0 z-30 shadow-sm overflow-y-auto">
            <div className="p-6">
                <h2 className="text-lg font-bold tracking-tight">Alubrasa PGI</h2>
            </div>
            <nav className="flex-1 px-4 space-y-4">
                <div>
                    <h3 className="mb-2 px-2 text-xs font-semibold uppercase text-muted-foreground">
                        Comercial
                    </h3>
                    <div className="space-y-1">
                        <MenuItem
                            active={currentPage === 'pricing'}
                            icon={LayoutDashboard}
                            label="Precificação"
                            onClick={() => onNavigate('pricing')}
                        />
                        <MenuItem
                            active={currentPage === 'prices-check'}
                            icon={Banknote}
                            label="Consulta de Preço"
                            onClick={() => onNavigate('prices-check')}
                        />
                    </div>
                </div>

                <div>
                    <h3 className="mb-2 px-2 text-xs font-semibold uppercase text-muted-foreground">
                        Financeiro
                    </h3>
                    <div className="space-y-1">
                        <MenuItem
                            active={currentPage === 'items'}
                            icon={LayoutDashboard}
                            label="Informações NF (Itens)"
                            onClick={() => onNavigate('items')}
                        />
                    </div>
                </div>

                <div>
                    <h3 className="mb-2 px-2 text-xs font-semibold uppercase text-muted-foreground">
                        Administração
                    </h3>
                    <div className="space-y-1">
                        <MenuItem
                            active={currentPage === 'dashboard-obras'}
                            icon={LayoutDashboard}
                            label="Dashboard de Obras"
                            onClick={() => onNavigate('dashboard-obras')}
                        />
                        <MenuItem
                            active={currentPage === 'obras-control'}
                            icon={HardHat}
                            label="Controle de Obras"
                            onClick={() => onNavigate('obras-control')}
                        />
                    </div>
                </div>
            </nav>
        </aside>
    );
}
