"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Sparkles, RefreshCw, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { fetchAiStatus, streamMarketSummary } from "@/lib/api";

interface AiPanelProps {
  context: Record<string, unknown>;
}

export function AiPanel({ context }: AiPanelProps) {
  const [available, setAvailable] = useState<boolean | null>(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const hasGeneratedRef = useRef(false);

  // Check AI availability on mount
  useEffect(() => {
    fetchAiStatus()
      .then((r) => setAvailable(r.available))
      .catch(() => setAvailable(false));
  }, []);

  const generateSummary = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setError(null);
    setText("");

    let accumulated = "";
    streamMarketSummary(
      context,
      (chunk) => {
        accumulated += chunk;
        setText(accumulated);
      },
      controller.signal,
    )
      .catch((e) => {
        if (e.name !== "AbortError") {
          setError(e.message || "Erro ao gerar análise");
        }
      })
      .finally(() => setLoading(false));
  }, [context]);

  // Auto-generate on mount once available
  useEffect(() => {
    if (available && !hasGeneratedRef.current) {
      hasGeneratedRef.current = true;
      generateSummary();
    }
  }, [available, generateSummary]);

  // Cleanup abort on unmount
  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  // Don't render if AI is not available
  if (available === false) return null;

  return (
    <Card className="h-fit">
      <CardHeader className="flex flex-row items-center justify-between pb-2 gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-brand-gold" />
          Briefing Estratégico
        </CardTitle>
        {text && !loading && (
          <Button
            variant="ghost"
            size="sm"
            className="h-7 gap-1 text-[10px] text-muted-foreground"
            onClick={generateSummary}
          >
            <RefreshCw className="h-3 w-3" />
            Atualizar
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {/* Loading skeleton */}
        {loading && !text && (
          <div className="space-y-2.5">
            <Skeleton className="h-3 w-[90%]" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-[75%]" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-[85%]" />
            <Skeleton className="h-3 w-[60%]" />
            <div className="pt-2" />
            <Skeleton className="h-3 w-[40%]" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-[80%]" />
          </div>
        )}

        {/* Streaming text */}
        {text && (
          <div className="prose prose-sm max-w-none text-xs leading-relaxed">
            <FormattedBriefing text={text} />
            {loading && (
              <span className="inline-block w-1.5 h-3.5 bg-brand-gold animate-pulse ml-0.5 align-middle" />
            )}
          </div>
        )}

        {/* Error state */}
        {error && !text && (
          <div className="flex flex-col items-center py-4 gap-2">
            <AlertCircle className="h-5 w-5 text-muted-foreground/40" />
            <p className="text-xs text-muted-foreground text-center">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={generateSummary}
              className="gap-1.5 text-xs mt-1"
            >
              <RefreshCw className="h-3 w-3" />
              Tentar novamente
            </Button>
          </div>
        )}

        {/* Initial check loading */}
        {available === null && (
          <div className="space-y-2">
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-[80%]" />
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/** Renders markdown-like bold (**text**) and bullet points from the LLM response. */
function FormattedBriefing({ text }: { text: string }) {
  const lines = text.split("\n");

  return (
    <>
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <br key={i} />;

        // Bold headers: **Text**
        const formatted = trimmed.replace(
          /\*\*(.+?)\*\*/g,
          '<strong class="font-semibold text-foreground">$1</strong>'
        );

        // Bullet points
        if (trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
          return (
            <div key={i} className="flex gap-1.5 pl-1 py-0.5">
              <span className="text-brand-gold shrink-0 mt-px">•</span>
              <span dangerouslySetInnerHTML={{ __html: formatted.slice(2) }} />
            </div>
          );
        }

        return (
          <p key={i} className="py-0.5" dangerouslySetInnerHTML={{ __html: formatted }} />
        );
      })}
    </>
  );
}
