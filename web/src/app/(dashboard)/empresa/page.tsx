"use client";

import { useState } from "react";
import { Building2, Search, FolderSearch } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { EmpresaDossier } from "./dossier";
import { ViabilidadeTab } from "./viabilidade-tab";

export default function EmpresaPage() {
  const [cnpj, setCnpj] = useState("");
  const [activeCnpj, setActiveCnpj] = useState<string | null>(null);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    const cleaned = cnpj.replace(/\D/g, "");
    if (cleaned.length >= 11) {
      setActiveCnpj(cleaned);
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Consulta de Inteligência
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Dossiê ambiental por empresa ou análise de viabilidade por projeto
        </p>
      </div>

      <Tabs defaultValue="empresa" className="space-y-6">
        <TabsList>
          <TabsTrigger value="empresa" className="gap-2">
            <Building2 className="h-3.5 w-3.5" />
            Por Empresa (CNPJ)
          </TabsTrigger>
          <TabsTrigger value="projeto" className="gap-2">
            <FolderSearch className="h-3.5 w-3.5" />
            Por Projeto
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Por Empresa */}
        <TabsContent value="empresa" className="space-y-6">
          <form onSubmit={handleSearch} className="flex gap-3 max-w-lg">
            <div className="relative flex-1">
              <Building2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Digite o CNPJ (somente números)"
                value={cnpj}
                onChange={(e) => setCnpj(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit" className="bg-brand-orange hover:bg-brand-orange/90">
              <Search className="mr-2 h-4 w-4" />
              Consultar
            </Button>
          </form>

          {activeCnpj && <EmpresaDossier cnpj={activeCnpj} />}

          {!activeCnpj && (
            <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-16">
              <Building2 className="h-12 w-12 text-muted-foreground/30" />
              <p className="mt-4 text-sm text-muted-foreground">
                Insira um CNPJ para visualizar o dossiê completo
              </p>
              <p className="mt-1 text-xs text-muted-foreground/60">
                O dossiê inclui decisões SEMAD, infrações IBAMA, títulos ANM e pagamentos CFEM.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {[
                  { cnpj: "08902291000115", label: "CSN Mineração" },
                  { cnpj: "16628281000323", label: "Samarco" },
                  { cnpj: "19095249000156", label: "Caldense" },
                ].map(({ cnpj: example, label }) => (
                  <button
                    key={example}
                    onClick={() => { setCnpj(example); setActiveCnpj(example); }}
                    className="rounded-md border px-3 py-1.5 text-xs transition-colors hover:bg-muted"
                  >
                    <span className="font-mono">{example.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5")}</span>
                    <span className="ml-1.5 text-muted-foreground">{label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </TabsContent>

        {/* Tab 2: Por Projeto */}
        <TabsContent value="projeto">
          <ViabilidadeTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
