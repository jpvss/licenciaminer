"use client";

import { useEffect, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import {
  Map as MapIcon,
  Loader2,
  Layers,
  Palette,
  AlertTriangle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { MultiSelect } from "@/components/multi-select";
import { StatCard } from "@/components/stat-card";
import {
  fetchGeoConcessoes,
  fetchGeoStats,
  fetchGeoFilters,
  fetchGeoLayer,
  fmtNumber,
  type GeoStats,
  type GeoFilterOptions,
} from "@/lib/api";
import { fmtBR, fmtHa } from "@/lib/format";

const MiningMap = dynamic(
  () => import("@/components/mining-map").then((m) => m.MiningMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full items-center justify-center bg-muted/30">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    ),
  }
);

type ColorBy = "categoria" | "regime" | "fase" | "cfem";

const COLOR_BY_LABELS: Record<ColorBy, string> = {
  categoria: "Categoria Mineral",
  regime: "Regime",
  fase: "Fase ANM",
  cfem: "Status CFEM",
};

export default function MapaPage() {
  const [geojson, setGeojson] = useState<GeoJSON.FeatureCollection | null>(null);
  const [stats, setStats] = useState<GeoStats | null>(null);
  const [filterOptions, setFilterOptions] = useState<GeoFilterOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [regime, setRegime] = useState<string[]>([]);
  const [categoria, setCategoria] = useState<string[]>([]);
  const [substancia, setSubstancia] = useState<string[]>([]);
  const [colorBy, setColorBy] = useState<ColorBy>("categoria");

  // Restriction layers
  const [showUCs, setShowUCs] = useState(false);
  const [showTIs, setShowTIs] = useState(false);
  const [ucsGeojson, setUcsGeojson] = useState<GeoJSON.FeatureCollection | null>(null);
  const [tisGeojson, setTisGeojson] = useState<GeoJSON.FeatureCollection | null>(null);

  // Load filter options on mount
  useEffect(() => {
    fetchGeoFilters().then(setFilterOptions).catch(() => {});
  }, []);

  // Load concessoes
  const loadConcessoes = useCallback(() => {
    setLoading(true);
    setError(null);

    const params = {
      regime: regime.length > 0 ? regime : undefined,
      categoria: categoria.length > 0 ? categoria : undefined,
      substancia: substancia.length > 0 ? substancia : undefined,
    };

    Promise.all([
      fetchGeoConcessoes(params),
      fetchGeoStats(params),
    ])
      .then(([geoData, statsData]) => {
        setGeojson(geoData.geojson);
        setStats(statsData);
        if (geoData.truncated) {
          setError(`Exibindo ${fmtBR(geoData.returned)} de ${fmtBR(geoData.total)} polígonos. Refine os filtros.`);
        }
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [regime, categoria, substancia]);

  useEffect(() => {
    loadConcessoes();
  }, [loadConcessoes]);

  // Lazy load restriction layers
  useEffect(() => {
    if (showUCs && !ucsGeojson) {
      fetchGeoLayer("ucs").then(setUcsGeojson).catch(() => {});
    }
  }, [showUCs, ucsGeojson]);

  useEffect(() => {
    if (showTIs && !tisGeojson) {
      fetchGeoLayer("tis").then(setTisGeojson).catch(() => {});
    }
  }, [showTIs, tisGeojson]);

  const colorPalettes = filterOptions?.color_palettes ?? {
    categoria: {},
    regime: {},
    fase: {},
  };

  // Legend entries for current colorBy
  const legendPalette =
    colorBy === "cfem"
      ? { Ativo: "#27AE60", Inativo: "#E74C3C" }
      : colorBy === "fase"
        ? colorPalettes.fase
        : colorBy === "regime"
          ? colorPalettes.regime
          : colorPalettes.categoria;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Mapa Geoespacial
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Concessões minerárias com sobreposição de UCs e Terras Indígenas
        </p>
      </div>

      {/* KPIs */}
      {stats ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Polígonos"
            value={fmtBR(stats.total_polygons)}
            subtitle={stats.total_polygons !== stats.total_all ? `de ${fmtBR(stats.total_all)} total` : undefined}
            icon={MapIcon}
          />
          <StatCard
            label="Enriquecidos"
            value={stats.enriched_count != null ? fmtBR(stats.enriched_count) : "—"}
            subtitle="com dados SCM"
            icon={Layers}
            accentClass="bg-brand-teal"
          />
          <StatCard
            label="Substâncias"
            value={stats.distinct_substances != null ? fmtBR(stats.distinct_substances) : "—"}
            icon={Palette}
            accentClass="bg-brand-gold"
          />
          <StatCard
            label="Área Total"
            value={stats.total_area_ha != null ? fmtHa(stats.total_area_ha) : "—"}
            icon={MapIcon}
            accentClass="bg-brand-orange"
          />
        </div>
      ) : !error ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-5">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : null}

      {/* Warning for truncation */}
      {error && (
        <Card className="border-warning/30">
          <CardContent className="flex items-center gap-2 p-3 text-sm text-warning">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </CardContent>
        </Card>
      )}

      {/* Controls + Map */}
      <div className="grid gap-4 lg:grid-cols-[260px_1fr]">
        {/* Sidebar controls */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-heading">Filtros</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Regime
                </label>
                <MultiSelect
                  options={filterOptions?.options.regimes ?? []}
                  selected={regime}
                  onChange={setRegime}
                  placeholder="Todos"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Categoria
                </label>
                <MultiSelect
                  options={filterOptions?.options.categorias ?? []}
                  selected={categoria}
                  onChange={setCategoria}
                  placeholder="Todas"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Substância
                </label>
                <MultiSelect
                  options={filterOptions?.options.substancias ?? []}
                  selected={substancia}
                  onChange={setSubstancia}
                  placeholder="Todas"
                />
              </div>

              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">
                  Colorir por
                </label>
                <Select value={colorBy} onValueChange={(v) => setColorBy(v as ColorBy)}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {(Object.keys(COLOR_BY_LABELS) as ColorBy[]).map((k) => (
                      <SelectItem key={k} value={k}>
                        {COLOR_BY_LABELS[k]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-heading">Camadas</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2">
                <Checkbox
                  id="show-ucs"
                  checked={showUCs}
                  onCheckedChange={(v) => setShowUCs(!!v)}
                />
                <label htmlFor="show-ucs" className="text-xs cursor-pointer flex items-center gap-1.5">
                  <span className="inline-block h-2.5 w-2.5 rounded-sm bg-success" />
                  Unidades de Conservação
                </label>
              </div>
              <div className="flex items-center gap-2">
                <Checkbox
                  id="show-tis"
                  checked={showTIs}
                  onCheckedChange={(v) => setShowTIs(!!v)}
                />
                <label htmlFor="show-tis" className="text-xs cursor-pointer flex items-center gap-1.5">
                  <span className="inline-block h-2.5 w-2.5 rounded-sm bg-danger" />
                  Terras Indígenas
                </label>
              </div>
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-heading">Legenda</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {Object.entries(legendPalette).map(([label, color]) => (
                  <div key={label} className="flex items-center gap-2 text-xs">
                    <span
                      className="inline-block h-3 w-3 rounded-sm shrink-0"
                      style={{ backgroundColor: color }}
                    />
                    <span className="truncate">{label}</span>
                  </div>
                ))}
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span className="inline-block h-3 w-3 rounded-sm shrink-0 bg-[#95A5A6]" />
                  <span>Outros / Sem dados</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Map */}
        <Card className="overflow-hidden">
          <div className="relative h-[600px] lg:h-[700px]">
            {loading && !geojson ? (
              <div className="flex h-full items-center justify-center bg-muted/30">
                <div className="text-center">
                  <Loader2 className="mx-auto h-8 w-8 animate-spin text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">Carregando geometrias...</p>
                </div>
              </div>
            ) : (
              <MiningMap
                geojson={geojson}
                colorBy={colorBy}
                colorPalettes={colorPalettes}
                showUCs={showUCs}
                showTIs={showTIs}
                ucsGeojson={ucsGeojson}
                tisGeojson={tisGeojson}
              />
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
