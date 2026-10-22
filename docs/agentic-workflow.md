# Agentic Workflow

Diese Anleitung beschreibt, wie doc-dialog mit Claude Code agentisch weiterentwickelt wird: welche Skills und Subagents es gibt, wie ein Feature von der Idee bis zum Pull Request läuft und wo du eingreifen musst.

## Überblick

```
/feature <Idee>
   │
   ├─ 1. Spec ──────── feature-analyst ──► docs/features/<slug>.md
   │                   ⏸ Freigabe durch dich
   ├─ 2. Branch ────── feature/<slug> von main
   ├─ 3. Backend ───── backend-dev   (nur backend/)
   ├─ 4. Frontend ──── frontend-dev  (nur frontend/)
   ├─ 5. Review ────── reviewer      (read-only)
   ├─ 6. Fix-Schleife  Dev-Agents beheben blocker/should-fix, max. 2 Runden
   └─ 7. Abschluss ─── Spec „done“, Commit-Vorschlag
                       ⏸ Commit / Push / PR nur nach deiner Freigabe
```

Der Hauptagent, also die Claude-Code-Session, in der du `/feature` aufrufst, orchestriert. Die Subagents erledigen die eigentliche Arbeit. Sie können keine weiteren Subagents starten und kennen den bisherigen Gesprächsverlauf nicht. Alles, was sie brauchen, steht in der Spec und im Auftrag, den der Hauptagent ihnen übergibt.

## Voraussetzungen

Einmalig einrichten, damit Tests, Linter und der Format-Hook funktionieren:

```bash
# Backend
cd backend
uv sync

# Frontend
cd ../frontend
npm install
```

Außerdem brauchst du `jq` für die Hook-Skripte und für PRs die GitHub CLI `gh`.

Nach Änderungen unter `.claude/` musst du Claude Code neu starten, damit Agents, Skills und Hooks neu geladen werden.

## Skills

Skills rufst du in Claude Code als Slash-Befehl auf.

### `/feature` – Feature komplett umsetzen

```
/feature Nutzer sollen Dokumente direkt im Browser hochladen können
/feature docs/features/upload-documents.md
```

- **Mit einer Idee** startet der Workflow bei der Spec.
- **Mit dem Pfad zu einer Spec mit `Status: approved`** überspringt er die Spec und legt direkt den Branch an. Eine Spec mit `Status: draft` legt er dir erst zur Freigabe vor.
- Vorher muss der Arbeitsbaum sauber sein (`git status` leer), sonst fragt der Hauptagent nach.

`/feature` wird nur ausgeführt, wenn du es selbst aufrufst. Claude startet den Workflow nie von sich aus, weil er Branches anlegt.

### `/spec` – nur die Spezifikation

```
/spec Antworten als Markdown exportieren
```

Führt nur Schritt 1 aus: Rückfragen klären, Spec schreiben, zur Freigabe vorlegen. Kein Branch, kein Code. Praktisch, um mehrere Features vorab zu planen und später einzeln mit `/feature docs/features/<slug>.md` umzusetzen.

### `/review` – nur ein Review

```
/review
/review docs/features/upload-documents.md
```

Setzt den reviewer auf den aktuellen Diff gegen `main` an, inklusive uncommitteter und ungetrackter Dateien. Ohne Argument sucht er die passende Spec über den Branch-Namen (`feature/<slug>` → `docs/features/<slug>.md`). Gibt es keine, prüft er ohne Spec. Das Review ändert nichts. Danach bietet der Hauptagent an, die Findings beheben zu lassen.

`/review` funktioniert auch für Änderungen, die du von Hand gemacht hast.

## Ablauf von `/feature` im Detail

### 1. Spec

Der `feature-analyst` liest den Code und stellt zuerst Rückfragen zu Ziel, Nutzern, Randfällen und Nicht-Zielen, jeweils mit einem Vorschlag als Default. Der Hauptagent leitet sie an dich weiter. Danach schreibt der Analyst `docs/features/<slug>.md` mit:

- Ziel und User Stories
- Akzeptanzkriterien `AK-n`, testbar formuliert (Gegeben / Wenn / Dann) und markiert mit `[BE]`, `[FE]` oder `[BE+FE]`
- API-Vertrag: Endpunkte, Felder, Grenzen, Statuscodes, dazu die passenden TypeScript-Interfaces
- betroffene Module, Nicht-Ziele, offene Fragen
- Tasks `BE-n` und `FE-n`
- `Status: draft`

**⏸ Checkpoint:** Du bekommst eine Zusammenfassung und gibst frei oder nennst Änderungen. Erst nach deiner ausdrücklichen Freigabe wird `Status: approved` gesetzt und der Workflow geht weiter. Du kannst die Spec vorher auch selbst im Editor anpassen.

### 2. Branch

`git checkout -b feature/<slug>` vom aktuellen `main`. Während des Workflows wird nicht committet, alle Änderungen bleiben im Arbeitsbaum.

### 3. Backend und 4. Frontend

`backend-dev` und `frontend-dev` setzen ihre Tasks um, schreiben zu jedem betroffenen Akzeptanzkriterium einen Test und melden sich erst, wenn alle Checks grün sind:

| Agent | Checks |
|---|---|
| backend-dev | `pytest`, `ruff check .`, `ruff format --check .`, Import von `app` |
| frontend-dev | `npm run test:unit`, `lint`, `type-check`, `build` |

Standardmäßig läuft das Frontend nach dem Backend, damit es gegen den echten Code arbeiten kann. Parallel laufen beide nur, wenn der API-Vertrag vollständig feststeht.

**Vertragsprobleme:** Passt der API-Vertrag nicht zur Realität, stoppt der Dev-Agent und meldet `VERTRAGSPROBLEM`, statt eigenmächtig abzuweichen. Der Hauptagent legt dir das Problem vor. Du entscheidest, ob die Spec angepasst wird (über den feature-analyst, mit erneuter Freigabe) oder ob es anders gelöst werden soll.

### 5. Review und 6. Fix-Schleife

Der `reviewer` prüft den Diff gegen die Spec und führt die Checks aus. Seine Findings:

- **blocker:** Akzeptanzkriterium nicht erfüllt, Vertrag verletzt, Tests rot oder fehlend, Sicherheitslücke
- **should-fix:** lückenhafte Fehlerbehandlung, Verstoß gegen eine Konvention
- **nit:** Stil, Kleinigkeiten

blocker und should-fix gehen an den zuständigen Dev-Agent zurück, danach wird erneut reviewt. Nach höchstens 2 Fix-Runden bekommst du die offenen Punkte vorgelegt und entscheidest selbst. nits werden nicht automatisch umgesetzt, sondern im Abschluss gelistet.

### 7. Abschluss

Die Spec wird auf `Status: done` gesetzt. Du bekommst eine Zusammenfassung mit geänderten Dateien, Akzeptanzkriterien und ihren Tests, Checks und offenen Punkten, dazu einen Commit-Vorschlag.

**⏸ Checkpoint:** Commit, Push, PR (`gh pr create --base main`) und Merge nur nach deiner Freigabe.

## Subagents direkt verwenden

Du kannst die Subagents auch ohne Skill ansprechen, etwa für Einzelaufgaben. Weil sie ohne Kontext starten, gib Spec-Pfad und Aufgabe immer ausdrücklich mit:

```
Lass den backend-dev Task BE-2 aus docs/features/upload-documents.md umsetzen.
Lass den reviewer nur das Backend auf Sicherheitsprobleme prüfen.
Nutze den feature-analyst, um docs/features/export-markdown.md um einen Fehlerfall für leere Antworten zu ergänzen.
```

| Agent | Modell | Darf | Darf nicht |
|---|---|---|---|
| `feature-analyst` | opus | Code lesen, `docs/features/*.md` schreiben | Produktivcode schreiben. Ein Hook blockiert Write außerhalb von `docs/features/`. |
| `backend-dev` | sonnet | `backend/` ändern, Tests und Linter ausführen | `frontend/` ändern, Vertrag ändern, committen |
| `frontend-dev` | sonnet | `frontend/` ändern, Tests, Lint und Build ausführen | `backend/` ändern, Vertrag ändern, committen |
| `reviewer` | opus | lesen, `git diff`, Checks ausführen | Dateien ändern |

## Specs

- Ablage: `docs/features/<slug>.md`, Slug englisch in kebab-case
- Lebenszyklus: `draft` → `approved` (nur nach deiner Freigabe) → `done`
- Specs werden mit dem Feature committet und bleiben als Dokumentation erhalten.
- Ändert ein Feature das Embedding-Modell oder die Chunk-Logik, steht das in der Spec. Danach muss der Index mit `uv run python ingest.py --reset` neu aufgebaut werden.

## Hooks

| Hook | Wann | Was |
|---|---|---|
| `.claude/hooks/format.sh` | nach jedem Edit/Write (`.claude/settings.json`) | `backend/**/*.py`: `ruff format` und Import-Sortierung. `frontend/**/*.{vue,ts,js,css,json}`: `prettier --write`. Fehlt ein Tool, wird still übersprungen. |
| `.claude/hooks/only-feature-docs.sh` | vor Write des feature-analyst (Agent-Frontmatter) | blockiert Pfade außerhalb von `docs/features/*.md` |

Tests und ESLint laufen bewusst nicht im Hook, damit Edits schnell bleiben. Die Dev-Agents und der Reviewer führen sie aus.

## Anpassen

- **Agent-Verhalten:** Prompts in `.claude/agents/<name>.md`. Das Frontmatter steuert `description` (wann der Agent eingesetzt wird), `tools` und `model`.
- **Workflow-Schritte:** `.claude/skills/feature/SKILL.md`. `/spec` verweist auf Schritt 1 darin, Änderungen dort gelten also für beide Skills.
- **Spec-Vorlage:** im Abschnitt „Spec-Vorlage“ von `.claude/agents/feature-analyst.md`.
- **Neue Prüfbefehle:** in CLAUDE.md unter „Befehle“ ergänzen und in den Abschnitten „Befehle“ von `backend-dev.md`, `frontend-dev.md` und `reviewer.md` nachziehen.

## Fehlerbehebung

| Problem | Lösung |
|---|---|
| `/feature` oder ein Agent wird nicht gefunden | Claude Code neu starten, `.claude/` liegt im Projekt-Root |
| Dateien werden nicht formatiert | `backend/.venv` (per `uv sync`) bzw. `frontend/node_modules` installiert? `jq` vorhanden? |
| Dev-Agent meldet rote Tests in fremdem Code | Vor `/feature` prüfen, ob `main` grün ist (`uv run pytest`, `npm run test:unit`) |
| Workflow bricht wegen lokaler Änderungen ab | Änderungen committen oder stashen, dann neu starten |
| Fix-Schleife nach 2 Runden beendet | Offene Findings selbst bewerten: Spec anpassen, gezielt `backend-dev`/`frontend-dev` beauftragen oder bewusst akzeptieren |
