"use client";

import { useState } from "react";
import { Building2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmpresaDossier } from "./dossier";

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
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Consulta Empresa
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Dossiê ambiental completo por CNPJ — decisões, infrações, CFEM e risco
        </p>
      </div>

      {/* Search */}
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

      {/* Dossier */}
      {activeCnpj && <EmpresaDossier cnpj={activeCnpj} />}

      {!activeCnpj && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20">
          <Building2 className="h-12 w-12 text-muted-foreground/30" />
          <p className="mt-4 text-sm text-muted-foreground">
            Insira um CNPJ para visualizar o dossiê completo
          </p>
          <p className="mt-1 text-xs text-muted-foreground/60">
            Exemplo: 00.000.000/0001-00
          </p>
        </div>
      )}
    </div>
  );
}
