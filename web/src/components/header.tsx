"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  Database,
  FileSearch,
  LayoutDashboard,
  Map,
  Menu,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

const MOBILE_NAV = [
  { href: "/", label: "Painel Principal", icon: LayoutDashboard },
  { href: "/explorar", label: "Explorar Dados", icon: Database },
  { href: "/empresa", label: "Consulta Empresa", icon: Building2 },
  { href: "/decisoes", label: "An\u00e1lise Decis\u00f5es", icon: BarChart3 },
  { href: "/due-diligence", label: "Due Diligence", icon: ShieldCheck },
  { href: "/concessoes", label: "Base de Concess\u00f5es", icon: FileSearch },
  { href: "/mapa", label: "Mapa Geoespacial", icon: Map },
  { href: "/prospeccao", label: "Prospec\u00e7\u00e3o", icon: TrendingUp },
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
          <nav className="px-3 py-4 space-y-1">
            {MOBILE_NAV.map((item) => {
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
