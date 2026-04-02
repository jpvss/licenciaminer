"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Globe,
  DollarSign,
  Coins,
  MapPin,
} from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KpiStrip } from "./kpi-strip";
import { MercadoTab } from "./tab-mercado";
import { ProducaoTab } from "./tab-producao";
import { TerritorioTab } from "./tab-territorio";
import { AiPanel } from "./ai-panel";
import { RegulatoryPulse } from "./regulatory-pulse";
import { PRESETS_BY_TAB } from "./chart-helpers";

const TAB_ICONS = {
  mercado: DollarSign,
  producao: Coins,
  territorio: MapPin,
} as const;

const TAB_LABELS = {
  mercado: "Mercado",
  producao: "Produção & Receita",
  territorio: "Território",
} as const;

type TabKey = keyof typeof TAB_LABELS;
const TAB_KEYS: TabKey[] = ["mercado", "producao", "territorio"];

export default function InteligenciaComercialPage() {
  return (
    <Suspense>
      <InteligenciaContent />
    </Suspense>
  );
}

function InteligenciaContent() {
  const params = useSearchParams();

  // URL state
  const [activeTab, setActiveTab] = useState<TabKey>(
    (params.get("tab") as TabKey) || "mercado"
  );
  const [activeMetric, setActiveMetric] = useState<string>(
    params.get("metric") || PRESETS_BY_TAB.mercado[0].id
  );

  // When switching tabs, reset metric to first preset of that tab
  function handleTabChange(tab: string) {
    const t = tab as TabKey;
    setActiveTab(t);
    const firstPreset = PRESETS_BY_TAB[t]?.[0]?.id;
    if (firstPreset) setActiveMetric(firstPreset);
  }

  // Sync to URL
  useEffect(() => {
    const qs = new URLSearchParams();
    if (activeTab !== "mercado") qs.set("tab", activeTab);
    const defaultMetric = PRESETS_BY_TAB[activeTab]?.[0]?.id;
    if (activeMetric !== defaultMetric) qs.set("metric", activeMetric);
    const q = qs.toString();
    window.history.replaceState(null, "", `${window.location.pathname}${q ? `?${q}` : ""}`);
  }, [activeTab, activeMetric]);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-gold">
          <Globe className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
            Inteligência Comercial
          </h1>
          <p className="text-xs text-muted-foreground">
            Visão integrada do setor mineral — Mercado, Produção, Território
          </p>
        </div>
      </div>

      {/* KPI Strip */}
      <KpiStrip />

      {/* AI Briefing — full-width, above tabs */}
      <AiPanel />

      {/* Regulatory Pulse — signal badges */}
      <RegulatoryPulse />

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange} className="space-y-4">
        <TabsList className="flex flex-wrap h-auto gap-1">
          {TAB_KEYS.map((key) => {
            const Icon = TAB_ICONS[key];
            return (
              <TabsTrigger key={key} value={key} className="gap-1.5 text-xs">
                <Icon className="h-3.5 w-3.5" />
                {TAB_LABELS[key]}
              </TabsTrigger>
            );
          })}
        </TabsList>

        <TabsContent value="mercado" className="mt-0">
          <MercadoTab
            activeMetric={activeMetric}
            onMetricChange={setActiveMetric}
          />
        </TabsContent>
        <TabsContent value="producao" className="mt-0">
          <ProducaoTab
            activeMetric={activeMetric}
            onMetricChange={setActiveMetric}
          />
        </TabsContent>
        <TabsContent value="territorio" className="mt-0">
          <TerritorioTab
            activeMetric={activeMetric}
            onMetricChange={setActiveMetric}
          />
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <p className="text-[10px] text-muted-foreground/50 text-center">
        Fontes: BCB PTAX, ANM (CFEM, RAL, SIGMINE), Comex Stat / MDIC, IBAMA, SEMAD/MG, COPAM, Investing.com, LME
      </p>
    </div>
  );
}
