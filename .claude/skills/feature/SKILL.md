---
name: feature
description: Kompletter Feature-Workflow für doc-dialog. Spec (feature-analyst) → Freigabe → Branch → Backend (backend-dev) → Frontend (frontend-dev) → Review (reviewer) → Fix-Schleife → Abschluss mit Commit-Vorschlag. Aufruf mit einer Feature-Idee oder dem Pfad zu einer freigegebenen Spec.
argument-hint: <Feature-Idee oder Pfad zu docs/features/<slug>.md>
disable-model-invocation: true
---

# /feature

Eingabe: `$ARGUMENTS`

Du bist der **Orchestrator**. Die Arbeit erledigen die Subagents `feature-analyst`, `backend-dev`, `frontend-dev` und `reviewer`. Du selbst schreibst keinen Produktivcode und änderst auch keine Spec-Inhalte. Ausnahmen: Status-Zeilen in der Spec, Häkchen bei Tasks und git-Befehle.

**Wichtig:**
- Subagents können keine weiteren Subagents starten. Jeder Schritt läuft über dich.
- Jeder Subagent startet **ohne** Gesprächskontext. Übergib ihm in jedem Auftrag Spec-Pfad, konkrete Aufgabe, Branch und relevante Rahmenbedingungen. Formulierungen wie „wie besprochen“ helfen ihm nicht.
- Gib dem Nutzer nach jedem Schritt eine Statuszeile (z. B. „Schritt 3/7 Backend: fertig, 9 Tests grün“).

## Schritt 0 – Eingabe einordnen

- Ist `$ARGUMENTS` ein Pfad zu einer existierenden Datei unter `docs/features/`, lies sie.
  - Ist `Status: approved`, weiter mit **Schritt 2**.
  - Ist `Status: draft`, weiter mit **Schritt 1** (Spec überarbeiten bzw. zur Freigabe vorlegen).
  - Ist `Status: done`, frag nach, ob wirklich neu umgesetzt werden soll.
- Sonst ist `$ARGUMENTS` eine Idee, weiter mit **Schritt 1**.
- Vorab prüfen: `git status --short` muss leer sein, sonst den Nutzer fragen, wie mit den lokalen Änderungen umgegangen werden soll.

## Schritt 1 – Spec (feature-analyst)

Starte `feature-analyst` mit diesem Auftrag (Platzhalter ersetzen):

> Feature-Idee: <Idee wörtlich vom Nutzer, ergänzt um alles, was der Nutzer dazu gesagt hat>
> Bestehende Spec (falls vorhanden): <Pfad>
> Bisherige Antworten des Nutzers auf Rückfragen: <keine | Liste>
> Erstelle bzw. überarbeite die Spec unter docs/features/<slug>.md nach deiner Vorlage, oder liefere zuerst RÜCKFRAGEN.

- Antwortet er mit `RÜCKFRAGEN`, leite die Fragen an den Nutzer weiter (AskUserQuestion oder als Liste). Danach startest du `feature-analyst` **neu**, mit Idee und Antworten im Auftrag. Höchstens 2 Rückfragerunden, danach soll er offene Punkte unter „Offene Fragen“ festhalten.
- **CHECKPOINT – Freigabe:** Lege dem Nutzer die Spec vor: Pfad, Ziel, Akzeptanzkriterien, API-Vertrag, Tasks und offene Fragen kompakt zusammengefasst. Frag ausdrücklich nach Freigabe.
  - Bei Änderungswünschen startest du `feature-analyst` erneut mit Spec-Pfad und Änderungswünschen, dann erneut vorlegen.
  - Erst nach ausdrücklicher Freigabe setzt du in der Spec `Status: draft` → `Status: approved`.
  - **Ohne Freigabe geht es nicht weiter.**

## Schritt 2 – Branch

```bash
git checkout main && git pull --ff-only   # schlägt pull fehl (offline): mit lokalem main weitermachen und Hinweis geben
git checkout -b feature/<slug>
```

Existiert der Branch schon, frag den Nutzer, ob darauf weitergearbeitet werden soll. Während des Workflows wird **nicht committet**. Alle Änderungen bleiben bis Schritt 7 im Arbeitsbaum, der Reviewer liest uncommittete und ungetrackte Dateien mit.

## Schritt 3 – Backend (backend-dev)

Gibt es keine Backend-Tasks, überspringen und vermerken. Sonst `backend-dev` starten:

> Spec: docs/features/<slug>.md (Status approved)
> Branch: feature/<slug> (bereits ausgecheckt, nicht wechseln, nicht committen)
> Aufgabe: Setze die Backend-Tasks <BE-1, BE-2, …> um. Halte dich exakt an den API-Vertrag der Spec.
> Akzeptanzkriterien mit Backend-Anteil: <AK-Liste>
> Rahmen: nur backend/ ändern; für jedes dieser AKs einen pytest-Test; pytest, ruff check und ruff format --check müssen grün sein; bei Vertragsproblemen stoppen und VERTRAGSPROBLEM melden.

- Meldet er `VERTRAGSPROBLEM`, stoppst du den Workflow und legst das Problem dem Nutzer vor. Mögliche Wege: Spec anpassen (über `feature-analyst`, danach erneut freigeben) oder anders lösen.
- Prüfe seine Zusammenfassung: Sind alle Tests grün? Ist jeder BE-Task erledigt? Hake erledigte Tasks in der Spec ab (`- [x]`).

## Schritt 4 – Frontend (frontend-dev)

Gibt es keine Frontend-Tasks, überspringen und vermerken. Standardmäßig startet dieser Schritt **nach** Schritt 3. Parallel zu Schritt 3 (beide Agents in derselben Nachricht starten) nur dann, wenn der API-Vertrag vollständig feststeht: alle Felder, Typen und Fehlerfälle definiert, keine offenen Fragen zur API. Bei Zweifel immer sequenziell.

> Spec: docs/features/<slug>.md (Status approved)
> Branch: feature/<slug> (bereits ausgecheckt, nicht wechseln, nicht committen)
> Aufgabe: Setze die Frontend-Tasks <FE-1, …> um. Halte dich exakt an den API-Vertrag der Spec.
> Stand Backend: <umgesetzt in backend/app.py, Zusammenfassung von backend-dev mit Hinweisen | noch nicht umgesetzt (paralleler Modus), nur gegen die Spec arbeiten>
> Akzeptanzkriterien mit Frontend-Anteil: <AK-Liste>
> Rahmen: nur frontend/ ändern; frontend/src/types/api.ts nachziehen; API nur über src/api/client.ts; kein Router, kein Pinia, keine UI-Bibliothek; Komponententests für jedes dieser AKs; test:unit, lint, type-check und build müssen grün sein; bei Vertragsproblemen stoppen und VERTRAGSPROBLEM melden.

Umgang mit `VERTRAGSPROBLEM` und Abhaken wie in Schritt 3.

## Schritt 5 – Review (reviewer)

> Spec: docs/features/<slug>.md
> Branch: feature/<slug>, Basis: main
> Aufgabe: Reviewe den Diff main...HEAD inklusive uncommitteter Änderungen gegen die Spec nach deiner Checkliste. Führe die lesenden Checks aus. Liefere Findings als blocker / should-fix / nit mit Datei:Zeile, Zuständigkeit (backend/frontend) und Vorschlag.
> Runde: <1 | 2 | 3>

## Schritt 6 – Fix-Schleife (höchstens 2 Runden)

- Gibt es keine blocker und keine should-fix, weiter mit Schritt 7.
- Sonst sortierst du die blocker- und should-fix-Findings nach Zuständigkeit und startest `backend-dev` bzw. `frontend-dev` erneut. Sind beide Bereiche betroffen und unabhängig, können beide parallel laufen.
  > Spec: docs/features/<slug>.md · Branch: feature/<slug> (nicht wechseln, nicht committen)
  > Aufgabe: Behebe diese Review-Findings: <Findings wörtlich mit ID, Datei:Zeile, Vorschlag>
  > Rahmen: wie zuvor (nur eigener Bereich, Tests und Checks grün, VERTRAGSPROBLEM bei Vertragskonflikt).
  > Ist ein Finding deiner Meinung nach falsch, setze es nicht um und begründe das.
- Danach wieder **Schritt 5**.
- Gibt es nach **2 Fix-Runden** (also beim 3. Review) noch blocker oder should-fix, stoppst du und legst dem Nutzer die offenen Findings vor, zusammen mit der Begründung der Dev-Agents, falls sie welche abgelehnt haben. Der Nutzer entscheidet, wie es weitergeht.
- nits setzt du nicht automatisch um, sondern listest sie im Abschluss.

## Schritt 7 – Abschluss

1. Spec auf `Status: done` setzen, alle erledigten Tasks abhaken.
2. Zusammenfassung an den Nutzer:
   - Feature und Branch
   - geänderte Dateien (`git diff main...HEAD --stat`)
   - Akzeptanzkriterien mit Tests (aus dem letzten Review)
   - Ergebnis der Checks
   - offene nits und Punkte, Hinweis auf `uv run python ingest.py --reset`, falls nötig
3. Commit-Vorschlag: `git status --short` und eine Commit-Nachricht zeigen (Titel, Stichpunkte pro Bereich, Verweis auf die Spec). Committen erst nach Freigabe.
4. **Nicht pushen, keinen PR anlegen, nicht mergen**, ohne dass der Nutzer das ausdrücklich freigibt. Nach Freigabe: `git push -u origin feature/<slug>` und `gh pr create --base main` mit Zusammenfassung und Link zur Spec im Body.
