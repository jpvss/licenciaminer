"use client";

import {
  BarChart3,
  Workflow,
  Brain,
  GaugeCircle,
  Map,
} from "lucide-react";

const SECTIONS = [
  { id: "kpis", label: "KPIs", icon: BarChart3 },
  { id: "atividades", label: "Atividades", icon: Workflow },
  { id: "ia", label: "Casos de IA", icon: Brain },
  { id: "maturidade", label: "Maturidade", icon: GaugeCircle },
  { id: "roadmap", label: "Roadmap", icon: Map },
] as const;

export type SectionId = (typeof SECTIONS)[number]["id"];

interface ModuleSectionNavProps {
  activeSection: SectionId;
  onSectionChange: (section: SectionId) => void;
}

export function ModuleSectionNav({
  activeSection,
  onSectionChange,
}: ModuleSectionNavProps) {
  return (
    <div className="sticky top-0 z-10 -mx-1 flex gap-1 overflow-x-auto bg-background/95 px-1 py-2 backdrop-blur-sm">
      {SECTIONS.map(({ id, label, icon: Icon }) => (
        <button
          key={id}
          onClick={() => onSectionChange(id)}
          className={`flex shrink-0 items-center gap-1.5 rounded-md px-3 py-1.5 text-[11px] font-medium transition-colors ${
            activeSection === id
              ? "bg-foreground text-background"
              : "text-muted-foreground hover:bg-muted hover:text-foreground"
          }`}
        >
          <Icon className="h-3.5 w-3.5" />
          {label}
        </button>
      ))}
    </div>
  );
}
