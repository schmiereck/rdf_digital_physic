## Goal

Führen Sie eine evolutionäre Suche nach einem stabilen v<c-Gleiter unter Verwendung der in `iter_199` entwickelten Fitnessfunktion `SparseGliderFitness` durch.

### Anweisungen:

1.  **Neues Skript erstellen:** Erstellen Sie ein neues Python-Skript `src/run_vc_search.py`. Dieses Skript sollte die evolutionäre Suche orchestrieren.
2.  **Fitness-Funktion verwenden:** Importieren und verwenden Sie die Klasse `SparseGliderFitness` aus `src/fitness.py`.
3.  **Suchparameter:**
    *   Startpopulation: 50 zufällige C2-symmetrische Regeln.
    *   Generationen: Führen Sie den Lauf für 15 Generationen durch.
    *   Seed-Partikel: Verwenden Sie das 3-Bit-L-Tromino-Muster, das durch die folgenden Koordinaten definiert ist: `[(0, 0), (0, 1), (1, 1)]`.
    *   Gittergröße: Verwenden Sie ein 128x128-Gitter.
    *   Simulationsschritte: 250 Schritte pro Auswertung.
4.  **Artefakte generieren:**
    *   **Champion-Regel:** Speichern Sie am Ende des Laufs die beste gefundene Regel (den "Champion") in `archive/iter_200/results/champion_vc_rule.json`.
    *   **Evolutionsprotokoll:** Protokollieren Sie die Fitness des Champions jeder Generation in einer CSV-Datei unter `archive/iter_200/results/evolution_log.csv`. Die Spalten sollten `generation` und `champion_fitness` sein.
    *   **Animation:** Erstellen Sie eine GIF-Animation des Champion-Musters, das sich über 250 Schritte entwickelt, und speichern Sie sie als `archive/iter_200/results/champion_vc_glider.gif`.
5.  **Ausführung:** Führen Sie das Skript `src/run_vc_search.py` aus.

### Zusammenfassung der erwarteten Ergebnisse:

Der Agent muss am Ende seiner Ausführung den folgenden YAML-Block ausgeben:

```yaml
status: ok
artifacts:
  - "archive/iter_200/results/champion_vc_rule.json"
  - "archive/iter_200/results/evolution_log.csv"
  - "archive/iter_200/results/champion_vc_glider.gif"
metrics:
  final_champion_fitness: <float>
  max_fitness_achieved: <float>
  generations_completed: 15
log_excerpt: |
  <Letzte 20 Zeilen der Konsolenausgabe, die den Fortschritt der Generationen zeigen>
experimenter_view: |
  <Eine qualitative Beschreibung, ob ein stabiler v<c-Gleiter gefunden wurde, basierend auf der Beobachtung der endgültigen Animation und der Fitnesswerte.>
notes: "Evolutionärer Lauf zur Suche nach v<c-Gleitschirm abgeschlossen."
```

Stellen Sie sicher, dass alle Pfade relativ zum Projektstammverzeichnis sind. Der vorhandene Code in `src/` sollte wiederverwendet werden.