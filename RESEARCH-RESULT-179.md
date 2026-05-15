# Research Result: Milestone — Glider Discovery (Iteration 179)

**Datum:** 2026-05-15  
**Milestone:** `milestone-glider-discovery`  
**Status:** Erreicht ✓

---

## 1. Kurzfassung

In Iteration 179 wurde das langfristige Forschungsziel der aktuellen Kampagne (Phase 7) erreicht:
Ein **stabiler, sich bewegender Gleiter** (Glider) in einem 2D hexagonalen Zellautomat wurde mittels
evolutionärer Suche erstmals erfolgreich entwickelt. Das 3-Bit "L-Tromino"-Muster bewegt sich mit
exakt **v = 1 Zelle/Schritt** (v = c) bei perfekter Bit-Erhaltung über beliebig viele Schritte.

---

## 2. Forschungsreise — Von iter_001 bis iter_179

### Phase 1: 1D-Grundlagen (iter 1–14)
| Iteration | Ergebnis |
|-----------|---------|
| iter_001 | **Formal:** 33 nicht-triviale, reversible, bit-erhaltende Regeln in 1D (3-Bit-Nachbarschaft) |
| iter_002 | **Dynamik:** 22 dieser Regeln erzeugen v=c-Gleiter aus einer einzelnen Zelle |
| iter_003–004 | **2-Bit/Zelle:** Existenzbeweis + stabiler stationärer Periode-2-Oszillator |
| iter_005–006 | **v=c/2-Gleiter:** Einteilchen- und Zweiteilchen-Gleiter mit halbierter Geschwindigkeit |
| iter_007 (=018) | **Kollisionen (1D):** 8 elastisch, 6 Fusion, 8 chaotisch aus 22 getesteten Regeln |

**Meilenstein Phase 1:** Katalog reversibler Regeln + stabile Solitonen in 1D bestätigt.  
**Meilenstein Phase 2:** v < c durch interne Oszillation (Masse-Simulation) nachgewiesen.

### Phase 3: 2D Hexagonales Gitter (iter 15–~149)
| Iteration | Ergebnis |
|-----------|---------|
| iter_015 | Formaler Existenzbeweis für 2D-Hex-Regeln (128 Zustände, Binomialverteilung) |
| iter_016 | Erste 2D-Gleiter (triviale Gitter-Shift-Regel, v=(0,−1)) |
| iter_017–019 | Erkenntnis: einfache lokale Regeln ≡ globaler Shift, nicht echte Teilchendynamik |
| iter_018 | 1D-Kollisionscharakterisierung: Fusionen und elastische Stöße nachgewiesen |

**Problem identifiziert:** Einfache Regeln erzeugen triviale globale Verschiebung, keine lokalen Teilchen.
Das erforderte einen Übergang zu **evolutionärer Regelsuche** statt konstruktiver Regeldefinition.

### Phase 7: Velocity-Stable Evolution (iter 150–179)

#### Fitness-Funktion-Iterationen — Die zentrale Herausforderung

| Iteration | Metrik | Problem |
|-----------|--------|---------|
| iter_150–151 | `total_displacement / (1 + std_dev)` | "Settler"-Exploit: ruhende Regeln erzielen Höchstnoten |
| iter_152–154 | Composite-Metrik | "Transient Puffer"-Exploit: kurzer Ausbruch, dann Stillstand |
| iter_155–156 | Late-displacement (t=1200–2000) | Zu schwaches Signal, kein evolutionärer Druck |
| iter_157–158 | Late-displacement Gen-2 | Fitness-Signal nicht vererbbar, Population degradiert |
| iter_159–166 | `late_displacement / (1 + final_bit_count)` | "Asche"-Muster: diffuse Felder ohne Struktur |
| iter_167 | Partikel-Fitness mit C2-Seed | **Kritischer Bug:** C2-Regel + C2-Seed → CoM-Invarianz = immer 0 |
| iter_170 | Asymmetrischer L-Tromino-Seed | **Durchbruch:** Bewegung möglich; aber "Annihilations"-Exploit entdeckt |
| iter_171 | `displacement * (final_bits / initial_bits)` | "Puffer"-Exploit: explosives Wachstum statt Gleiter |
| iter_173 | `StableVelocityFitness` | Korrekt, aber zu schwaches Signal in 3 Generationen |
| iter_174 | Verlängerter Lauf (10 Gen.) | **Durchbruch:** Gen-7-Sprung, komplexe intermittierende Bewegung (Fitness 0.674) |
| iter_176 | `SimpleMotionFitness` (max_bit_count-Strafe) | Neuer Champion, aber "Transient Bloomer"-Exploit |
| iter_177 | `CheckpointFitness` entwickelt | Neue Metrik korrekt: bewertet Bit-Stabilität an 4 Checkpoints |
| iter_178 | — | Kompletter technischer Ausfall (code_error in allen Sub-Agenten) |

#### Iteration 179 — Der Milestone

**179.1 — Neubewertung:** Alle 101 Regeln aus iter_174 und iter_176 erzielen unter `CheckpointFitness`
exakt 0.0. Dies beweist zweifelsfrei: ein Neustart ist nötig, ältere "Champions" sind keine echten Gleiter.

**179.2 — Transiente Ausführungsfehler** (behoben durch Retry).

**179.3 — Evolutionäre Suche:**
```
Gen  0: max=0.471  mean=0.011  non_zero=3
Gen  1: max=0.667  mean=0.018  non_zero=4
Gen  2: max=0.667  mean=0.037  non_zero=9
...
Gen  6: max=0.667  mean=0.250  non_zero=51
Gen  7: max=56.00  mean=0.982  non_zero=77   ← Phasenübergang (~84x Sprung!)
Gen  8: max=56.00  mean=1.088  non_zero=83
Gen  9: max=56.00  mean=1.632  non_zero=79
Gen 10: max=56.00  mean=2.150  non_zero=74
```

**Phase-Transition in Generation 7:** Fitness-Sprung von 0.667 → 56.0 (~84-fach).
74/100 Regeln der Schluss-Population sind bit-stabil — starker Selektionsdruck bestätigt.

**179.4 — Visuelle Verifikation (Champion: `g10_rule_001`, Fitness = 56.0):**

```
step=  50  bit_count=3  unwrapped_com=(113.67, 63.33)
step= 100  bit_count=3  unwrapped_com=(163.67, 63.33)
step= 150  bit_count=3  unwrapped_com=(213.67, 63.33)
...
step= 500  bit_count=3  unwrapped_com=(563.67, 63.33)
Netto-Versatz (Step 100–500): 400.0 Zellen (3.125 Torusumläufe)
```

**Ergebnis:** Perfekter Gleiter — 3-Bit L-Tromino, v=1 Zelle/Schritt, null Dispersion, null Bit-Drift.

---

## 3. Technische Details des Champions

| Parameter | Wert |
|-----------|------|
| Regel | `g10_rule_001` |
| Partikel | 3-Bit L-Tromino |
| Geschwindigkeit | 1.0 Zellen/Schritt (= v_max) |
| Bit-Erhaltung | Perfekt (immer 3 Bits an allen Checkpoints) |
| Dispersion | 0 (transversale Drift = 0) |
| Nicht-triviale Regeleinträge | 23 |
| Fitness-Score | 56.0 |
| Artefakt | `archive/iter_179/results/champion_glider.gif` |

**Drei Regeln teilen den Top-Score** (g10_rule_001 bis _003), was auf Konvergenz der Population
auf dieselbe Gleiter-Lösung hindeutet.

---

## 4. Offene Fragen / Nächste Schritte

Die Entdeckung des Gleiters öffnet eine neue Forschungsphase:

1. **Kollisionsdynamik:** Was passiert, wenn zwei Gleiter aufeinanderprallen?
2. **Robustheit:** Überlebt der Gleiter Rauschen oder Strukturstörungen?
3. **Regelminimierung:** Welche der 23 nicht-trivialen Einträge sind für die Bewegung essentiell?
4. **Weitere Gleiter:** Existieren Gleiter mit v < c (durch interne Oszillation)?
5. **Andere Strukturen:** Unterstützt die Champion-Regel stationäre Oszillatoren?

**Geplante nächste Phase:** Untersuchung der Kollisionsdynamik zweier Gleiter.

---

## 5. Einordnung in den Gesamtplan

```
Roadmap:          Phase 1 (1D)   Phase 2 (Zappel)   Phase 3 (2D Hex)   Phase 4.x (3D/4D)
                  ████████████   █████████████████   ████░░░░░░░░░░░░   ░░░░░░░░░░░░░░░░
Status:           ABGESCHLOSSEN  ABGESCHLOSSEN        IN BEARBEITUNG     OFFEN
                                                      (Gleiter ✓,
                                                       Kollisionen ?)
```

Der Milestone `milestone-glider-discovery` markiert den **Abschluss des ersten Teilziels von Phase 3**.
Ein stabiler, lokaler Gleiter im 2D-Hex-Gitter ist die notwendige Voraussetzung für die Kollisionsphysik,
die den Übergang zu Phase 4 (3D Kuboktaeder) motivieren soll.
