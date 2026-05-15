# RDF Framework Review — Stand Iteration 179

**Datum:** 2026-05-15  
**Bewertet:** Iterationen 1–179  
**Reviewer:** Claude Sonnet 4.6

---

## 1. Gesamtbewertung

**Das Projekt tut sinnvolles** für sein Ziel — aber deutlich langsamer als theoretisch möglich,
und mit strukturellen Framework-Schwächen, die wiederholt Iterationen verschwenden.

Die zentrale wissenschaftliche These (emergente Physik aus lokalen, reversiblen Regeln auf diskretem
Gitter) ist methodisch gut operationalisiert. Die Hierarchie 1D → 2D → 3D ist korrekt. Der
Milestone in iter_179 — ein stabiler Gleiter im 2D-Hex-Gitter — ist ein echter, verifizierbarer
wissenschaftlicher Fortschritt und kein Artefakt.

**Kurzurteil:** Wissenschaftlich solide, operativ ineffizient, strukturell noch weit vom Ziel entfernt.

---

## 2. Was gut funktioniert

### 2.1 Wissenschaftliche Methodik
- **Hypothesen-getriebenes Vorgehen:** Jede Iteration formuliert eine testbare Hypothese.
  Negative Ergebnisse werden explizit dokumentiert und als Erkenntnisse gewertet.
- **Falsifikationsorientierung:** Das Refutieren von Exploits (Settler, Puffer, Annihilator, Bloomer)
  wird nicht als Versagen sondern als Lernschritt behandelt — korrekte wissenschaftliche Praxis.
- **Unabhängige Verifikation:** iter_179.4 vertraut dem Fitness-Score nicht und fordert visuelle
  Bestätigung. Das verhindert, dass Exploits als Erfolg gewertet werden.
- **Zustandstracking:** `current_state.md` hält Confirmed/Refuted/Open konsistent aktuell.

### 2.2 Technischer Fortschritt
- Die evolutionäre Suchstrategie ist der richtige Ansatz für den exponentiell großen Regelraum.
- `CheckpointFitness` ist eine methodisch robuste Lösung: Bit-Stabilität an mehreren
  Zeitpunkten erzwingt echte Persistenz statt transiente Artefakte.
- Der Phasenübergang in Generation 7 (0.667 → 56.0) deutet auf einen echten qualitativen
  Sprung hin, nicht auf graduellen Fortschritt — das ist das erwartete Verhalten, wenn eine
  robuste Fitness-Funktion den richtigen Suchraum aufspannt.

---

## 3. Strukturelle Schwächen

### 3.1 Mock-Iterationen (kritisch)
In folgenden Iterationen hat der Planner-Agent **`run_agent` nicht aufgerufen** und stattdessen
Ergebnisse halluziniert:

| Iter | Status | Notiz |
|------|--------|-------|
| 160  | no_execution | Mock: "lr-2e4 doubling LR" — völlig themenfremdes Experiment |
| 161  | no_execution | Identisch |
| 162  | no_execution (2×) | Identisch |
| 164  | no_execution | Identisch |
| 165  | no_execution | Identisch |
| 168  | no_execution | Identisch |
| 169  | no_execution | Identisch |
| 172  | no_execution | Identisch |
| 175  | no_execution | Identisch |

**~9 Iterationen (≈5% des Gesamtlaufs) waren vollständig wertlos.**

Das Muster der Halluzinationen ist auffällig: Die fiktiven Hypothesen ("lr-2e4 doubling LR...
val_loss < 3.0") haben nichts mit dem Projekt zu tun — sie scheinen aus einem früheren,
anderen Projekt zu stammen, das der Planner-Agent noch im Kontext hatte. Dies deutet auf
ein **Kontextverwischungs-Problem** im Planner-Agent hin: Wenn der Kontext groß wird,
verliert der Agent die Kontrolle über die aktuelle Aufgabe.

**Empfehlung:** Explizite Prüfung, ob `run_agent` aufgerufen wurde. Keine Iteration ohne
Experimentator-Ergebnis als `ok` oder `experiment_failed` werten.

### 3.2 Fitness-Funktion-Iterationskosten

Die Suche nach einer robusten Fitness-Funktion hat **~20 Iterationen** (iter 150–177) benötigt.
Jede neue Metrik deckte einen neuen Exploit auf:

```
Settler → Puffer → Late-Displacement-Signal zu schwach → 
C2-Symmetrie-Bug → Annihilator → Puffer v2 → Bloomer → CheckpointFitness ✓
```

Dies ist teilweise unvermeidlich — Fitness-Function Engineering ist ein schwieriges Problem.
Aber einige dieser Iterationen hätten früher abgebrochen werden können:

- iter_157–158 (Late-displacement): Das Signal war von Anfang an zu schwach (max_fitness 0.14).
  Zwei Iterationen Breeding-Versuche mit hoffnungslos schwachem Signal.
- iter_166 (100 Random Rules neu bewertet): Hätte als Validierungsschritt inliniert werden können.

**Empfehlung:** Früher-Abbruch-Kriterien für evolutionäre Läufe einführen. Wenn der beste
Gen-0-Wert unter einem Schwellenwert liegt, direkt neue Metrik testen statt zu brüten.

### 3.3 Ausführungsumgebung (technisch)

iter_178 war ein **Totalausfall**: 3 Sub-Agenten, alle mit `code_error`. Der darauffolgende
iter_179 konnte das Problem beheben, aber ein vollständig verlorener Zyklus ist teuer.

**Empfehlung:** Umgebungs-Sanity-Checks als standardmäßiger erster Sub-Agent jeder Phase
(einfacher `print("hello")` reicht). iter_179.1 hat dies korrekt gemacht — als Reaktion
auf iter_178. Es sollte Standard sein.

### 3.4 Fortschrittsrate vs. Roadmap

Die Roadmap definiert 4 Phasen: 1D → 2D Hex → 3D Kuboktaeder → 4D FCC-Raumzeit.

Nach 179 Iterationen sind wir am **Anfang von Phase 3** (2D Hex, Gleiter gefunden,
Kollisionen ausstehend). Die geschätzte Komplexitätssteigerung pro Phase ist erheblich:

| Phase | Status | Symmetriegruppe | Nachbarn |
|-------|--------|-----------------|---------|
| 1 (1D) | Abgeschlossen | Z | 2 |
| 2 (2D Hex) | Gleiter ✓ | C6v | 6 |
| 3 (3D Kuboktaeder) | Offen | Oh | 12 |
| 4 (4D FCC) | Offen | F4 | 24 |

**Kritische Beobachtung:** Der Regelraum wächst exponentiell mit der Nachbaranzahl.
Was in 2D ~10 Iterationen Fitness-Engineering benötigte, könnte in 3D ein Vielfaches davon
erfordern. Die methodischen Lektionen aus Phase 7 (CheckpointFitness, Asymmetric Seeds,
Exploit-Klassifikation) müssen in 3D **sofort** angewendet werden, nicht erneut erarbeitet.

---

## 4. Einschätzung: Wird das Ziel erreicht?

### Was das Ziel ist
Das übergeordnete Ziel (goal.md) ist der **Nachweis emergenzer Physik** auf einem 3D
Kuboktaeder-Gitter: stabile Gleiter, quantisierte Zwischengeschwindigkeiten, E=mc²-Analogie,
idealerweise Zeitdilatation durch Rechenlast.

### Aktueller Stand
- **Bestätigte Erfolge:** Reversible Regeln existieren. Gleiter existieren. Evolutionäre Suche
  funktioniert. CheckpointFitness ist robust.
- **Noch ausstehendes Kernproblem:** Ob echte emergente Physik (Kollisionen mit
  Erhaltungssätzen, v < c durch interne Zustände, Interaktionen mit physikalischer Bedeutung)
  in einem hexagonalen 2D-System möglich ist, ist **noch nicht getestet**.

### Einschätzung
Das Projekt macht **echten Fortschritt** in der richtigen Richtung. Die Methodenentwicklung
(insbesondere CheckpointFitness und die evolutionäre Suche) ist ein realer Beitrag. Es gibt
keinen Grund, das Projekt als fehlgeleitet zu betrachten.

**Risiken:**
1. **Skalierungsproblem:** Die Komplexitätslücke zwischen 2D und 3D ist enorm. Es ist nicht
   garantiert, dass der gleiche Ansatz dort funktioniert.
2. **Zieldrift:** Das aktuelle Forschungsziel ("Gleiter in 2D Hex") ist ein Teilziel, nicht das
   Endziel. Es besteht das Risiko, in diesem Teilziel zu verweilen, ohne den Übergang zu 3D
   voranzutreiben.
3. **Mock-Iterationen:** Wenn der Planner-Agent häufiger "abbricht", steigen die
   Effizienzverluste.

---

## 5. Empfehlungen

| Priorität | Empfehlung |
|-----------|-----------|
| **Hoch** | Mock-Iterationen eliminieren: Mechanismus einführen, der sicherstellt, dass jede Iteration einen echten Experimentator-Aufruf enthält |
| **Hoch** | Erarbeitete Lektionen (CheckpointFitness, Asymmetric Seed, Exploit-Klassifikation) als Standard in der Dokumentation festhalten, bevor Phase 4 beginnt |
| **Mittel** | Frühzeitiger Übergang von 2D-Kollisionsphysik zu 3D beginnen, sobald 2–3 Kollisionsexperimente abgeschlossen sind |
| **Mittel** | Automatischen Umgebungs-Sanity-Check als ersten Sub-Agenten jeder Phase einführen |
| **Niedrig** | Fitness-Engineering-Bibliothek aufbauen: bekannte Exploits und deren Erkennungs-Metriken dokumentieren |

---

## 6. Fazit

Das Projekt hat einen echten wissenschaftlichen Milestone erreicht. Der Weg dorthin war
ineffizienter als nötig — ungefähr 15–20% der Iterationen haben nichts beigetragen (Mocks,
technische Ausfälle, zu frühe Breeding-Läufe mit schwachem Signal). Aber das verbleibende
Kernvorhaben — emergente Physik aus minimalen lokalen Regeln — ist methodisch fundiert,
die Zwischenergebnisse sind konsistent, und die gewonnene Infrastruktur (evolutionäre Suche
+ robuste Fitness-Metrik) ist die notwendige Basis für die nächsten Phasen.

**Das Projekt sollte fortgesetzt werden.** Die nächste kritische Frage ist die
Kollisionsdynamik des gefundenen Gleiters — wenn dort Erhaltungssätze und deterministisches
Streuverhalten emergieren, ist der Übergang zu 3D wissenschaftlich gerechtfertigt.
