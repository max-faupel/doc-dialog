---
name: review
description: Den reviewer-Subagent auf den aktuellen Diff (Branch gegen main plus uncommittete Änderungen) von doc-dialog ansetzen, optional gegen eine Spec. Liefert Findings nach Schweregrad, ändert nichts.
argument-hint: "[Pfad zur Spec]"
---

# /review

Eingabe: `$ARGUMENTS` (optional: Pfad zu einer Spec unter `docs/features/`)

1. Ermittle Branch und Spec:
   - `git branch --show-current`
   - Ist `$ARGUMENTS` ein Spec-Pfad, nimm diesen. Sonst: Branch `feature/<slug>` mit existierender `docs/features/<slug>.md` → diese Spec. Andernfalls ohne Spec.
   - Gibt es weder Commits gegenüber main noch uncommittete Änderungen, sag das und brich ab.
2. Starte den Subagent `reviewer`:
   > Branch: <Branch>, Basis: main
   > Spec: <Pfad | keine>
   > Aufgabe: Reviewe den Diff main...HEAD inklusive uncommitteter und ungetrackter Änderungen nach deiner Checkliste. Führe die lesenden Checks aus. Liefere Findings als blocker / should-fix / nit mit Datei:Zeile, Zuständigkeit und Vorschlag.
3. Gib das Ergebnis des Reviewers unverändert an den Nutzer weiter. Setze selbst **nichts** um. Biete am Ende an, die blocker- und should-fix-Findings über `backend-dev` bzw. `frontend-dev` beheben zu lassen.
