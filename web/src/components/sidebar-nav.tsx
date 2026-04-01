"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Building2,
  FileSearch,
  LayoutDashboard,
  Map,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_SECTIONS = [
  {
    label: "Summo Ambiental",
    items: [
      { href: "/", label: "Visão Geral", icon: LayoutDashboard },
      { href: "/empresa", label: "Consulta Empresa", icon: Building2 },
      { href: "/decisoes", label: "Análise Decisões", icon: BarChart3 },
      { href: "/due-diligence", label: "Due Diligence", icon: ShieldCheck },
    ],
  },
  {
    label: "Direitos e Concessões",
    items: [
      { href: "/concessoes", label: "Concessões", icon: FileSearch },
      { href: "/mapa", label: "Mapa Geoespacial", icon: Map },
    ],
  },
  {
    label: "Inteligência",
    items: [
      { href: "/prospeccao", label: "Prospecção", icon: TrendingUp },
    ],
  },
];

export function SidebarNav() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 bg-sidebar text-sidebar-foreground">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-sidebar-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sidebar-primary">
          <ShieldCheck className="h-4.5 w-4.5 text-sidebar-primary-foreground" />
        </div>
        <div>
          <span className="font-heading text-sm font-bold tracking-tight text-white">
            Summo Quartile
          </span>
          <span className="block text-[10px] uppercase tracking-widest text-sidebar-foreground/50">
            Conformidade Ambiental
          </span>
        </div>
      </div>

      {/* Nav sections */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label}>
            <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-sidebar-foreground/40">
              {section.label}
            </p>
            <ul className="space-y-0.5">
              {section.items.map((item) => {
                const isActive =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname.startsWith(item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                        isActive
                          ? "bg-sidebar-accent text-sidebar-accent-foreground font-medium"
                          : "text-sidebar-foreground/70 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground"
                      )}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-sidebar-border px-6 py-3">
        <p className="text-[10px] text-sidebar-foreground/30">
          v0.1.0 &middot; Dados: MG SEMAD, IBAMA, ANM
        </p>
      </div>
    </aside>
  );
}
