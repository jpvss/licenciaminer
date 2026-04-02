"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  Construction,
  Database,
  Factory,
  FileSearch,
  Globe,
  LayoutDashboard,
  Map,
  Menu,
  Search,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

interface MobileNavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
}

const MOBILE_NAV_SECTIONS: { label: string; items: MobileNavItem[] }[] = [
  {
    label: "Summo Ambiental",
    items: [
      { href: "/", label: "Painel Principal", icon: LayoutDashboard },
      { href: "/explorar", label: "Explorar Dados", icon: Database },
      { href: "/empresa", label: "Consulta Empresa", icon: Building2 },
      { href: "/decisoes", label: "Análise Decisões", icon: BarChart3 },
      { href: "/due-diligence", label: "Due Diligence", icon: ShieldCheck },
    ],
  },
  {
    label: "Direitos e Concessões",
    items: [
      { href: "/concessoes", label: "Base de Concessões", icon: FileSearch },
      { href: "/mapa", label: "Mapa Geoespacial", icon: Map },
      { href: "/prospeccao", label: "Prospecção", icon: TrendingUp },
    ],
  },
  {
    label: "Mineral Intelligence",
    items: [
      { href: "/inteligencia-comercial", label: "Inteligência Comercial", icon: Globe },
      { href: "/monitoramento", label: "Monitoramento", icon: Search, disabled: true },
    ],
  },
  {
    label: "SQ Solutions",
    items: [
      { href: "/mineradora-modelo", label: "Mineradora Modelo", icon: Factory },
    ],
  },
  {
    label: "Gestão Interna",
    items: [
      { href: "/gestao-interna", label: "Gestão Interna", icon: Construction, disabled: true },
    ],
  },
];

export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-4 lg:px-8">
      {/* Mobile menu */}
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="lg:hidden">
            <Menu className="h-5 w-5" />
            <span className="sr-only">Menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-72 bg-sidebar p-0">
          <SheetTitle className="sr-only">Navegação</SheetTitle>
          <div className="flex h-16 items-center gap-3 px-6 border-b border-sidebar-border">
            <ShieldCheck className="h-5 w-5 text-brand-orange" />
            <span className="font-heading text-sm font-bold text-white">
              Summo Quartile
            </span>
          </div>
          <nav className="px-3 py-4 space-y-4">
            {MOBILE_NAV_SECTIONS.map((section) => (
              <div key={section.label}>
                <p className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-sidebar-foreground/40">
                  {section.label}
                </p>
                {section.items.map((item) => {
                  if (item.disabled) {
                    return (
                      <span
                        key={item.href}
                        className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-sidebar-foreground/30 cursor-not-allowed"
                      >
                        <item.icon className="h-4 w-4" />
                        {item.label}
                      </span>
                    );
                  }
                  const isActive =
                    item.href === "/"
                      ? pathname === "/"
                      : pathname.startsWith(item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setOpen(false)}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors",
                        isActive
                          ? "bg-sidebar-accent text-white font-medium"
                          : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-white"
                      )}
                    >
                      <item.icon className="h-4 w-4" />
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            ))}
          </nav>
        </SheetContent>
      </Sheet>

      {/* Breadcrumb / page context */}
      <div className="flex-1" />

      {/* Right actions placeholder */}
      <div className="flex items-center gap-2">
        <span className="hidden sm:inline text-xs text-muted-foreground font-tabular">
          MG &middot; SEMAD + IBAMA + ANM
        </span>
      </div>
    </header>
  );
}
