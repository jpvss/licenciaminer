import { Construction } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

interface UnderConstructionProps {
  title: string;
  description: string;
  expectedDate: string;
}

export function UnderConstruction({ title, description, expectedDate }: UnderConstructionProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading text-2xl font-bold tracking-tight lg:text-3xl">
          {title}
        </h1>
      </div>
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-20">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted">
            <Construction className="h-8 w-8 text-muted-foreground/50" />
          </div>
          <p className="mt-6 font-heading text-lg font-semibold">Em construção</p>
          <p className="mt-2 max-w-md text-center text-sm text-muted-foreground">
            {description}
          </p>
          <p className="mt-4 rounded-full bg-muted px-4 py-1.5 text-xs font-medium text-muted-foreground">
            Previsão: {expectedDate}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
