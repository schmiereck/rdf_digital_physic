import json
import os

with open(os.path.join('archive', 'iter_215', 'results', 'final_population.json')) as f:
    final_pop = json.load(f)
print("FINAL POPULATION (first element):")
import pprint
pprint.pprint(final_pop[0])

with open(os.path.join('archive', 'iter_215', 'results', 'warm_start_population.json')) as f:
    warm_pop = json.load(f)
print("\nWARM START POPULATION keys:", list(warm_pop.keys()))
print("warm_pop['population'] type:", type(warm_pop['population']))
print("warm_pop['population'] length:", len(warm_pop['population']))
if len(warm_pop['population']) > 0:
    print("First element in warm_pop['population'] type:", type(warm_pop['population'][0]))
    pprint.pprint(warm_pop['population'][0])
