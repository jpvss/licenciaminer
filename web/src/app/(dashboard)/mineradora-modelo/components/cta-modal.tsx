"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CheckCircle2, Loader2 } from "lucide-react";

interface CTAModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  moduloInteresse?: string;
}

export function CTAModal({ open, onOpenChange, moduloInteresse }: CTAModalProps) {
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitting(true);
    // Simulate submission (replace with real API call)
    setTimeout(() => {
      setSubmitting(false);
      setSubmitted(true);
    }, 1000);
  }

  function handleClose(open: boolean) {
    if (!open) {
      setSubmitted(false);
      setSubmitting(false);
    }
    onOpenChange(open);
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        {submitted ? (
          <div className="flex flex-col items-center gap-4 py-6 text-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-success/10">
              <CheckCircle2 className="h-6 w-6 text-success" />
            </div>
            <div>
              <h3 className="font-heading text-lg font-semibold">
                Solicitação enviada!
              </h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Entraremos em contato em até 24h para agendar seu diagnóstico.
              </p>
            </div>
            <Button variant="outline" onClick={() => handleClose(false)}>
              Fechar
            </Button>
          </div>
        ) : (
          <>
            <DialogHeader>
              <DialogTitle className="font-heading">
                Solicitar Diagnóstico de IA
              </DialogTitle>
              <DialogDescription>
                Preencha seus dados para receber uma avaliação personalizada de como IA pode transformar sua operação.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-3">
              <div>
                <label className="text-xs font-medium" htmlFor="cta-nome">
                  Nome
                </label>
                <Input
                  id="cta-nome"
                  name="nome"
                  required
                  placeholder="Seu nome completo"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium" htmlFor="cta-empresa">
                  Empresa
                </label>
                <Input
                  id="cta-empresa"
                  name="empresa"
                  required
                  placeholder="Nome da mineradora"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium" htmlFor="cta-email">
                  E-mail
                </label>
                <Input
                  id="cta-email"
                  name="email"
                  type="email"
                  required
                  placeholder="seu@email.com"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium" htmlFor="cta-cargo">
                  Cargo
                </label>
                <Input
                  id="cta-cargo"
                  name="cargo"
                  placeholder="ex: Gerente de Operações"
                  className="mt-1"
                />
              </div>
              {moduloInteresse && (
                <input type="hidden" name="modulo" value={moduloInteresse} />
              )}
              {moduloInteresse && (
                <p className="text-[11px] text-muted-foreground">
                  Módulo de interesse: <span className="font-medium">{moduloInteresse}</span>
                </p>
              )}
              <Button
                type="submit"
                className="w-full"
                disabled={submitting}
              >
                {submitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  "Solicitar Diagnóstico Gratuito"
                )}
              </Button>
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
