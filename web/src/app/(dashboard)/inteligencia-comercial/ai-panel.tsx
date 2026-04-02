"use client";

import { useState, useEffect } from "react";
import {
  Sparkles,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  Clock,
  Globe,
  BarChart3,
  ShieldAlert,
  Loader2,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  fetchBriefing,
  refreshBriefing,
  type BriefingSection,
} from "@/lib/api";

export function AiPanel() {
  const [sections, setSections] = useState<BriefingSection[]>([]);
  const [generatedAt, setGeneratedAt] = useState<string | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "generating">(
    "loading"
  );
  const [collapsed, setCollapsed] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    let cancelled = false;
    let retryTimer: ReturnType<typeof setTimeout>;

    function load() {
      fetchBriefing()
        .then((res) => {
          if (cancelled) return;
          if (res.status === "ready" && res.sections.length > 0) {
            setSections(res.sections);
            setGeneratedAt(res.generated_at);
            setStatus("ready");
          } else {
            // Still generating on server — poll again in 5s
            setStatus("generating");
            retryTimer = setTimeout(load, 5000);
          }
        })
        .catch(() => {
          if (!cancelled) setStatus("ready"); // fail silently
        });
    }

    load();
    return () => {
      cancelled = true;
      clearTimeout(retryTimer);
    };
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    refreshBriefing()
      .then(() => {
        // Poll for the new briefing after a short delay
        setTimeout(() => {
          fetchBriefing().then((res) => {
            if (res.status === "ready" && res.sections.length > 0) {
              setSections(res.sections);
              setGeneratedAt(res.generated_at);
            }
            setRefreshing(false);
          });
        }, 8000); // give the LLM time to generate
      })
      .catch(() => setRefreshing(false));
  };

  const formattedTimestamp = generatedAt
    ? new Date(generatedAt).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : null;

  const hasSections = sections.length > 0;
  const isLoading = status === "loading" || status === "generating";

  return (
    <Card className="border-brand-gold/20 bg-gradient-to-br from-card to-brand-gold/[0.02]">
      <CardHeader className="flex flex-row items-center justify-between pb-2 gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-brand-gold" />
          Briefing Estratégico
          {status === "generating" && !hasSections && (
            <Loader2 className="h-3 w-3 animate-spin text-muted-foreground ml-1" />
          )}
        </CardTitle>
        <div className="flex items-center gap-2">
          {formattedTimestamp && (
            <Badge
              variant="secondary"
              className="text-[10px] font-normal text-muted-foreground gap-1"
            >
              <Clock className="h-2.5 w-2.5" />
              {formattedTimestamp}
            </Badge>
          )}
          {hasSections && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1 text-[10px] text-muted-foreground"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw
                className={cn("h-3 w-3", refreshing && "animate-spin")}
              />
              Atualizar
            </Button>
          )}
          {hasSections && (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-muted-foreground"
              onClick={() => setCollapsed(!collapsed)}
            >
              {collapsed ? (
                <ChevronDown className="h-3.5 w-3.5" />
              ) : (
                <ChevronUp className="h-3.5 w-3.5" />
              )}
            </Button>
          )}
        </div>
      </CardHeader>

      {!collapsed && (
        <CardContent>
          {isLoading && !hasSections && (
            <div className="grid gap-4 md:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-full" />
                  <Skeleton className="h-3 w-[90%]" />
                  <Skeleton className="h-3 w-[75%]" />
                  <Skeleton className="h-3 w-full" />
                </div>
              ))}
            </div>
          )}

          {hasSections && <SectionGrid sections={sections} />}
        </CardContent>
      )}
    </Card>
  );
}

/* ── Section Rendering ── */

interface SectionStyle {
  border: string;
  bg: string;
  iconColor: string;
  Icon: React.ElementType;
}

const SECTION_STYLES: Record<string, SectionStyle> = {
  "Cenário Atual": {
    border: "border-l-brand-gold",
    bg: "bg-brand-gold/5",
    iconColor: "text-brand-gold",
    Icon: Globe,
  },
  "Sinais de Mercado": {
    border: "border-l-brand-teal",
    bg: "bg-brand-teal/5",
    iconColor: "text-brand-teal",
    Icon: BarChart3,
  },
  "Riscos e Oportunidades": {
    border: "border-l-brand-orange",
    bg: "bg-brand-orange/5",
    iconColor: "text-brand-orange",
    Icon: ShieldAlert,
  },
};

const DEFAULT_STYLE: SectionStyle = {
  border: "border-l-brand-gold",
  bg: "bg-brand-gold/5",
  iconColor: "text-brand-gold",
  Icon: Globe,
};

function SectionGrid({ sections }: { sections: BriefingSection[] }) {
  const titled = sections.filter((s) => s.title && s.content);

  if (titled.length === 0) {
    const content = sections[0]?.content ?? "";
    return (
      <div className="rounded-lg border-l-2 border-l-brand-gold bg-brand-gold/5 p-4">
        <div className="text-xs leading-relaxed text-muted-foreground">
          <FormattedText text={content} />
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-3">
      {titled.map((section, i) => {
        const style = SECTION_STYLES[section.title] ?? DEFAULT_STYLE;
        const { Icon } = style;
        return (
          <div
            key={i}
            className={cn(
              "rounded-lg border-l-2 p-4 space-y-2",
              style.border,
              style.bg
            )}
          >
            <div className="flex items-center gap-1.5">
              <Icon className={cn("h-3.5 w-3.5 shrink-0", style.iconColor)} />
              <h3 className="text-xs font-semibold text-foreground">
                {section.title}
              </h3>
            </div>
            <div className="text-[11px] leading-relaxed text-muted-foreground">
              <FormattedText text={section.content} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function FormattedText({ text }: { text: string }) {
  const lines = text.split("\n");

  return (
    <>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <br key={i} />;

        const formatted = trimmed.replace(
          /\*\*(.+?)\*\*/g,
          '<strong class="font-semibold text-foreground">$1</strong>'
        );

        if (trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
          return (
            <div key={i} className="flex gap-1.5 pl-1 py-0.5">
              <span className="text-brand-gold shrink-0 mt-px">•</span>
              <span
                dangerouslySetInnerHTML={{ __html: formatted.slice(2) }}
              />
            </div>
          );
        }

        return (
          <p
            key={i}
            className="py-0.5"
            dangerouslySetInnerHTML={{ __html: formatted }}
          />
        );
      })}
    </>
  );
}
