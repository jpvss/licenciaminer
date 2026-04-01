"use client";

import { FileText, ExternalLink } from "lucide-react";

interface DocumentLinksProps {
  /** Raw string from SEMAD: "name|url;name|url" or "name|url\nname|url" */
  raw: string;
}

interface DocLink {
  name: string;
  url: string;
}

function parseDocLinks(raw: string): DocLink[] {
  if (!raw || raw === "\u2014") return [];

  // SEMAD uses "name|url" pairs separated by ";" or newlines
  const entries = raw.split(/[;\n]/).filter(Boolean);
  const links: DocLink[] = [];

  for (const entry of entries) {
    const trimmed = entry.trim();
    if (!trimmed) continue;

    const pipeIdx = trimmed.indexOf("|");
    if (pipeIdx > 0) {
      const name = trimmed.slice(0, pipeIdx).trim();
      const url = trimmed.slice(pipeIdx + 1).trim();
      if (url.startsWith("http")) {
        links.push({ name, url });
      }
    } else if (trimmed.startsWith("http")) {
      // Just a URL with no name
      links.push({ name: "Documento", url: trimmed });
    }
  }

  return links;
}

export function DocumentLinks({ raw }: DocumentLinksProps) {
  const links = parseDocLinks(raw);

  if (links.length === 0) {
    return (
      <p className="text-xs text-muted-foreground italic">
        Nenhum documento dispon\u00edvel
      </p>
    );
  }

  return (
    <ul className="space-y-1.5">
      {links.map((link, i) => (
        <li key={i}>
          <a
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-md border px-3 py-2 text-xs transition-colors hover:bg-muted/50"
          >
            <FileText className="h-3.5 w-3.5 shrink-0 text-brand-teal" />
            <span className="flex-1 truncate">{link.name}</span>
            <ExternalLink className="h-3 w-3 shrink-0 text-muted-foreground" />
          </a>
        </li>
      ))}
    </ul>
  );
}
