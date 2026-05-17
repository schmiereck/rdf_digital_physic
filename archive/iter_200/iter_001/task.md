Führen Sie eine evolutionäre Suche nach einem stabilen v<c-Gleiter (massives Teilchen) durch.

**Kontext:** Phase 199 hat eine neue, robuste Fitnessfunktion, `SparseGliderFitness`, entwickelt, die frühere Exploits ("Grid-Filling") verhindert. Diese Phase soll diese neue Funktion nutzen, um das langjährige Ziel der Entdeckung eines v<c-Gleiters zu erreichen.

**Anweisungen:**
1.  **Fitness-Funktion:** Verwenden Sie die in `iter_199` entwickelte und validierte `SparseGliderFitness`. Diese Funktion belohnt die Verschiebung und bestraft gleichzeitig eine hohe Dichte oder das Füllen des Gitters.
2.  **Evolutionärer Lauf:** Führen Sie einen vollständigen evolutionären Lauf für mindestens 10 Generationen durch. Beginnen Sie mit einer neuen, zufälligen Population von C2-symmetrischen Regeln.
3.  **Seed-Partikel:** Verwenden Sie das Standard-3-Bit-L-Tromino als Ausgangspartikel.
4.  **Erfolgskriterium:** Das Ziel ist die Entdeckung einer Regel, die ein Teilchen erzeugt, das sich stabil mit einer Geschwindigkeit von deutlich weniger als 1 Zelle pro Schritt bewegt (v < 1c).
5.  **Artefakte:**
    *   Speichern Sie die Champion-Regel in `archive/iter_200/results/champion_vc_rule.json`.
    *   Erstellen Sie eine Animation des resultierenden v<c-Gleiters und speichern Sie sie als `archive/iter_200/results/champion_vc_glider.gif`.
    *   Protokollieren Sie die Fitness jeder Generation in `archive/iter_200/results/evolution_log.csv`.
6.  **Synthese:** Berichten Sie über den Erfolg der Suche, die höchste erreichte Fitness und ob ein stabiler v<c-Gleiter gefunden wurde.