"use client";

import { useEffect, useState } from "react";
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
  Search,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { fetchFreshness } from "@/lib/api";

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
}

const NAV_SECTIONS: { label: string; color?: string; standalone?: boolean; items: NavItem[] }[] = [
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

export function SidebarNav() {
  const pathname = usePathname();
  const [freshness, setFreshness] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchFreshness()
      .then((r) => { if (!cancelled) setFreshness(r.last_updated); })
      .catch(() => {});
    return () => { cancelled = true; };
  }, []);

  return (
    <aside className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 bg-sidebar text-sidebar-foreground">
      {/* Logo */}
      <div className="flex h-16 items-center gap-3 px-6 border-b border-sidebar-border">
        <Image src="/logo2.png" alt="Summo Quartile" width={32} height={32} className="rounded-lg" />
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
                const isActive =
                  item.href === "/"
                    ? pathname === "/"
                    : pathname.startsWith(item.href);
                const disabled = item.disabled;
                return (
                  <li key={item.href}>
                    <Link
                      href={disabled ? "#" : item.href}
                      aria-disabled={disabled || undefined}
                      tabIndex={disabled ? -1 : undefined}
                      className={cn(
                        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors",
                        disabled
                          ? "pointer-events-none text-sidebar-foreground/30"
                          : isActive
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
      <div className="border-t border-sidebar-border px-5 py-3 space-y-1.5">
        <p className="text-[10px] leading-relaxed text-sidebar-foreground/40">
          Fontes públicas oficiais · Cada registro rastreável à origem
        </p>
        <div className="flex items-center gap-1.5 text-[10px] text-sidebar-foreground/25">
          {freshness && (
            <>
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-green-500" />
              <span>Dados: {freshness}</span>
              <span>&middot;</span>
            </>
          )}
          <span>v0.2.0</span>
        </div>
      </div>
    </aside>
  );
}
