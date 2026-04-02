"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  Database,
  Factory,
  FileSearch,
  Globe,
  Home,
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

const MOBILE_NAV_SECTIONS: { label: string; color?: string; standalone?: boolean; items: MobileNavItem[] }[] = [
  {
    label: "",
    standalone: true,
    items: [
      { href: "/", label: "Início", icon: Home },
    ],
  },
  {
    label: "Análise & Pesquisa",
    color: "text-brand-orange",
    items: [
      { href: "/empresa", label: "Consulta Empresa", icon: Building2 },
      { href: "/explorar", label: "Explorador", icon: Database },
      { href: "/decisoes", label: "Análise de Decisões", icon: BarChart3 },
    ],
  },
  {
    label: "Direitos Minerários",
    color: "text-brand-teal",
    items: [
      { href: "/mapa", label: "Mapa Interativo", icon: Map },
      { href: "/concessoes", label: "Concessões", icon: FileSearch },
      { href: "/prospeccao", label: "Prospecção Mineral", icon: TrendingUp },
    ],
  },
  {
    label: "Mercado & Inteligência",
    color: "text-brand-gold",
    items: [
      { href: "/inteligencia-comercial", label: "Inteligência Comercial", icon: Globe },
      { href: "/monitoramento", label: "Monitoramento", icon: Search, disabled: true },
    ],
  },
  {
    label: "Conformidade",
    color: "text-brand-orange",
    items: [
      { href: "/due-diligence", label: "Due Diligence", icon: ShieldCheck },
    ],
  },
  {
    label: "Simulação",
    color: "text-sidebar-foreground/40",
    items: [
      { href: "/mineradora-modelo", label: "Mineradora Modelo", icon: Factory },
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
            <Image src="/logo2.png" alt="Summo Quartile" width={20} height={20} className="rounded" />
            <span className="font-heading text-sm font-bold text-white">
              Summo Quartile
            </span>
          </div>
          <nav className="px-3 py-4 space-y-6">
            {MOBILE_NAV_SECTIONS.map((section) => (
              <div key={section.label || "home"}>
                {!section.standalone && (
                  <p className={cn(
                    "px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest",
                    section.color ?? "text-sidebar-foreground/40"
                  )}>
                    {section.label}
                  </p>
                )}
                <ul className="space-y-0.5">
                  {section.items.map((item) => {
                    if (item.disabled) {
                      return (
                        <li key={item.href}>
                          <span className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-sidebar-foreground/30 cursor-not-allowed">
                            <item.icon className="h-4 w-4" />
                            {item.label}
                          </span>
                        </li>
                      );
                    }
                    const isActive =
                      item.href === "/"
                        ? pathname === "/"
                        : pathname.startsWith(item.href);
                    return (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          onClick={() => setOpen(false)}
                          className={cn(
                            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                            isActive
                              ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                              : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                          )}
                        >
                          <item.icon className="h-4 w-4" />
                          {item.label}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
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
