---
name: spec
description: Nur die Spezifikationsphase für doc-dialog. Eine Feature-Idee mit dem feature-analyst in eine Spec unter docs/features/<slug>.md überführen und zur Freigabe vorlegen, ohne sie umzusetzen.
argument-hint: <Feature-Idee oder Pfad zu einer Draft-Spec>
---

# /spec

Eingabe: `$ARGUMENTS`

Führe **nur Schritt 1** aus `.claude/skills/feature/SKILL.md` aus. Lies den Abschnitt „Schritt 1 – Spec“ dort und befolge ihn genau: Auftrag an `feature-analyst`, Rückfragen weiterleiten, Spec zur Freigabe vorlegen, nach ausdrücklicher Freigabe `Status: approved` setzen.

Danach endest du. Kein Branch, keine Umsetzung, kein Commit. Weise am Ende darauf hin, dass sich die Spec mit `/feature docs/features/<slug>.md` umsetzen lässt.
