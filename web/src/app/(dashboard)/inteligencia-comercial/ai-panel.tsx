"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import { Sparkles, RefreshCw, ChevronDown, ChevronUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { fetchAiStatus, streamMarketSummary } from "@/lib/api";

interface AiPanelProps {
  context: Record<string, unknown>;
}

export function AiPanel({ context }: AiPanelProps) {
  const [available, setAvailable] = useState<boolean | null>(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const cacheRef = useRef<Map<string, string>>(new Map());

  // Check AI availability on mount
  useEffect(() => {
    fetchAiStatus()
      .then((r) => setAvailable(r.available))
      .catch(() => setAvailable(false));
  }, []);

  const generateSummary = useCallback(() => {
    // Check cache
    const cacheKey = JSON.stringify(context);
    const cached = cacheRef.current.get(cacheKey);
    if (cached) {
      setText(cached);
      return;
    }

    // Abort previous stream
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
      .then(() => {
        cacheRef.current.set(cacheKey, accumulated);
      })
      .catch((e) => {
        if (e.name !== "AbortError") {
          setError(e.message || "Erro ao gerar análise");
        }
      })
      .finally(() => setLoading(false));
  }, [context]);

  // Cleanup abort on unmount
  useEffect(() => {
    return () => {
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  // Don't render if AI is not available
  if (available === false) return null;

  // Loading initial status check
  if (available === null) {
    return (
      <Card>
        <CardContent className="p-4">
          <Skeleton className="h-32 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-fit">
      <CardHeader className="flex flex-row items-center justify-between pb-2 gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-1.5">
          <Sparkles className="h-3.5 w-3.5 text-brand-gold" />
          Análise AI
        </CardTitle>
        <div className="flex items-center gap-1">
          {text && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 lg:hidden"
              onClick={() => setCollapsed((v) => !v)}
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
      <CardContent className={cn(collapsed && "hidden lg:block")}>
        {!text && !loading && !error && (
          <div className="text-center py-6">
            <Sparkles className="mx-auto h-8 w-8 text-muted-foreground/20 mb-3" />
            <p className="text-xs text-muted-foreground mb-3">
              Gere um resumo executivo baseado nos dados visíveis.
            </p>
            <Button
              size="sm"
              onClick={generateSummary}
              className="gap-1.5"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Gerar Análise
            </Button>
          </div>
        )}

        {loading && (
          <div className="space-y-2">
            {text ? (
              <div className="prose prose-sm max-w-none text-xs leading-relaxed whitespace-pre-wrap">
                {text}
                <span className="inline-block w-1.5 h-3.5 bg-brand-gold animate-pulse ml-0.5" />
              </div>
            ) : (
              <>
                <Skeleton className="h-3 w-full" />
                <Skeleton className="h-3 w-[80%]" />
                <Skeleton className="h-3 w-[90%]" />
                <Skeleton className="h-3 w-[60%]" />
              </>
            )}
          </div>
        )}

        {text && !loading && (
          <div className="space-y-3">
            <div className="prose prose-sm max-w-none text-xs leading-relaxed whitespace-pre-wrap">
              {text}
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="gap-1.5 text-xs h-7"
              onClick={generateSummary}
            >
              <RefreshCw className="h-3 w-3" />
              Regenerar
            </Button>
          </div>
        )}

        {error && (
          <div className="text-center py-4">
            <p className="text-xs text-danger mb-2">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={generateSummary}
              className="gap-1.5 text-xs"
            >
              <RefreshCw className="h-3 w-3" />
              Tentar novamente
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
