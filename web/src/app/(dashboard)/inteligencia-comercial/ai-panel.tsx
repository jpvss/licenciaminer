"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  Sparkles,
  RefreshCw,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Clock,
  Globe,
  BarChart3,
  ShieldAlert,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { fetchAiStatus, streamMarketSummary } from "@/lib/api";

const CACHE_KEY = "sq_briefing_cache";
const CACHE_TTL_MS = 60 * 60 * 1000; // 1 hour

interface CachedBriefing {
  text: string;
  generatedAt: string; // ISO
}

interface AiPanelProps {
  context: Record<string, unknown>;
}

function loadCache(): CachedBriefing | null {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const cached: CachedBriefing = JSON.parse(raw);
    const age = Date.now() - new Date(cached.generatedAt).getTime();
    if (age > CACHE_TTL_MS) return null;
    return cached;
  } catch {
    return null;
  }
}

function saveCache(text: string) {
  const entry: CachedBriefing = {
    text,
    generatedAt: new Date().toISOString(),
  };
  try {
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(entry));
  } catch {
    // sessionStorage full — ignore
  }
}

export function AiPanel({ context }: AiPanelProps) {
  // Initialize from cache synchronously to avoid effect-based setState
  const [available, setAvailable] = useState<boolean | null>(null);
  const [text, setText] = useState(() => loadCache()?.text ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const [generatedAt, setGeneratedAt] = useState<string | null>(
    () => loadCache()?.generatedAt ?? null
  );
  const abortRef = useRef<AbortController | null>(null);
  const hasGeneratedRef = useRef(!!loadCache());

  const generateSummary = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setText("");
    setGeneratedAt(null);

    let accumulated = "";
    streamMarketSummary(
      context,
      (chunk) => {
        accumulated += chunk;
        setText(accumulated);
      },
      controller.signal,
    )
      .then(() => {
        if (accumulated) {
          saveCache(accumulated);
          setGeneratedAt(new Date().toISOString());
        }
      })
      .catch((e) => {
        if (e.name !== "AbortError") {
          setError(e.message || "Erro ao gerar análise");
        }
      })
      .finally(() => setLoading(false));
  }, [context]);

  // Check AI availability + auto-generate once if no cache
  useEffect(() => {
    let cancelled = false;
    fetchAiStatus()
      .then((r) => {
        if (cancelled) return;
        setAvailable(r.available);
        if (r.available && !hasGeneratedRef.current && !text) {
          hasGeneratedRef.current = true;
          generateSummary();
        }
      })
      .catch(() => {
        if (!cancelled) setAvailable(false);
      });
    return () => { cancelled = true; };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Cleanup abort on unmount
  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  // Don't render if AI is not available
  if (available === false) return null;

  const handleRefresh = () => {
    try {
      sessionStorage.removeItem(CACHE_KEY);
    } catch {
      // ignore
    }
    generateSummary();
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

  return (
    <Card className="border-brand-gold/20 bg-gradient-to-br from-card to-brand-gold/[0.02]">
      <CardHeader className="flex flex-row items-center justify-between pb-2 gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-brand-gold" />
          Briefing Estratégico
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
          {text && !loading && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 gap-1 text-[10px] text-muted-foreground"
              onClick={handleRefresh}
            >
              <RefreshCw className="h-3 w-3" />
              Atualizar
            </Button>
          )}
          {text && (
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
          {/* Loading skeleton */}
          {loading && !text && (
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

          {/* Structured briefing */}
          {text && (
            <div className="relative">
              <StructuredBriefing text={text} />
              {loading && (
                <span className="inline-block w-1.5 h-3.5 bg-brand-gold animate-pulse ml-0.5 align-middle" />
              )}
            </div>
          )}

          {/* Error state */}
          {error && !text && (
            <div className="flex flex-col items-center py-4 gap-2">
              <AlertCircle className="h-5 w-5 text-muted-foreground/40" />
              <p className="text-xs text-muted-foreground text-center">
                {error}
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRefresh}
                className="gap-1.5 text-xs mt-1"
              >
                <RefreshCw className="h-3 w-3" />
                Tentar novamente
              </Button>
            </div>
          )}

          {/* Initial availability check */}
          {available === null && (
            <div className="space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-[80%]" />
            </div>
          )}
        </CardContent>
      )}
    </Card>
  );
}

/* ── Structured Section Parser ── */

interface ParsedSection {
  title: string;
  content: string;
}

function parseSections(text: string): ParsedSection[] {
  const lines = text.split("\n");
  const sections: ParsedSection[] = [];
  let currentTitle = "";
  let currentLines: string[] = [];

  for (const line of lines) {
    // Match section headers: **Title**, **Title**:, **Title** —, ## Title, ### Title
    const headerMatch =
      line.match(/^\s*\*\*(.+?)\*\*\s*[:—–-]?\s*$/) ||
      line.match(/^\s*#{2,3}\s+(.+?)\s*$/);
    if (headerMatch) {
      if (currentTitle || currentLines.length > 0) {
        sections.push({
          title: currentTitle,
          content: currentLines.join("\n").trim(),
        });
      }
      currentTitle = headerMatch[1].replace(/\*\*/g, "").trim();
      currentLines = [];
    } else {
      currentLines.push(line);
    }
  }

  if (currentTitle || currentLines.length > 0) {
    sections.push({
      title: currentTitle,
      content: currentLines.join("\n").trim(),
    });
  }

  return sections;
}

interface SectionStyle {
  border: string;
  bg: string;
  iconColor: string;
  Icon: React.ElementType;
}

const SECTION_MATCHERS: { test: (s: string) => boolean; style: SectionStyle }[] = [
  {
    test: (s) => /cenário|cenario|atual|contexto|panorama/i.test(s),
    style: {
      border: "border-l-brand-gold",
      bg: "bg-brand-gold/5",
      iconColor: "text-brand-gold",
      Icon: Globe,
    },
  },
  {
    test: (s) => /sinais|mercado|indicador|dado|número/i.test(s),
    style: {
      border: "border-l-brand-teal",
      bg: "bg-brand-teal/5",
      iconColor: "text-brand-teal",
      Icon: BarChart3,
    },
  },
  {
    test: (s) => /risco|oportunidade|alerta|atenção/i.test(s),
    style: {
      border: "border-l-brand-orange",
      bg: "bg-brand-orange/5",
      iconColor: "text-brand-orange",
      Icon: ShieldAlert,
    },
  },
];

const DEFAULT_STYLE: SectionStyle = {
  border: "border-l-brand-gold",
  bg: "bg-brand-gold/5",
  iconColor: "text-brand-gold",
  Icon: Globe,
};

function getSectionStyle(title: string): SectionStyle {
  return SECTION_MATCHERS.find((m) => m.test(title))?.style ?? DEFAULT_STYLE;
}

function StructuredBriefing({ text }: { text: string }) {
  const sections = parseSections(text);
  const titled = sections.filter((s) => s.title && s.content);

  // Fallback: no clear sections — render as a single styled block
  if (titled.length <= 1) {
    return (
      <div className="rounded-lg border-l-2 border-l-brand-gold bg-brand-gold/5 p-4">
        <div className="text-xs leading-relaxed text-muted-foreground">
          <FormattedText text={text} />
        </div>
      </div>
    );
  }

  return (
    <div className="grid gap-3 md:grid-cols-3">
      {titled.map((section, i) => {
        const style = getSectionStyle(section.title);
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

/** Renders inline markdown: **bold**, bullet points. */
function FormattedText({ text }: { text: string }) {
  const lines = text.split("\n");

  return (
    <>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <br key={i} />;

        // Bold: **text**
        const formatted = trimmed.replace(
          /\*\*(.+?)\*\*/g,
          '<strong class="font-semibold text-foreground">$1</strong>'
        );

        // Bullet points
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
