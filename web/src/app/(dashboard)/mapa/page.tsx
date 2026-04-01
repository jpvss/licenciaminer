import { Map } from "lucide-react";

export default function MapaPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          Mapa Geoespacial
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Sobreposição de concessões com áreas protegidas, UCs e terras indígenas
        </p>
      </div>
      <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-border py-20">
        <Map className="h-12 w-12 text-muted-foreground/30" />
        <p className="mt-4 text-sm text-muted-foreground">
          Em desenvolvimento — MapLibre + vector tiles
        </p>
      </div>
    </div>
  );
}
