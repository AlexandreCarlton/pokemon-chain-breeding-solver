#!/usr/bin/env python3

from itertools import chain
from urllib.request import urlopen

import atexit
import json
import subprocess
import time

DUMP_IMAGE = 'docker.io/alexandrecarlton/pokeapi-dump:sha-3a93e40'
ENDPOINT = 'http://localhost:8080'

print(f'Staring container for {DUMP_IMAGE}.')
completed = subprocess.run(
    ['docker', 'run',
     '-d',
     '--rm', '-it',
     '-p', '8080:80',
     '-e', f'ENDPOINT={ENDPOINT}',
     DUMP_IMAGE],
    text=True,
    stdout=subprocess.PIPE)
container_name = completed.stdout.strip()
print(f"{DUMP_IMAGE} container has name {container_name}")

# As we supplied '--rm', we stop (and therefore kill) the container on exit.
def stop_container():
    subprocess.run(['docker', 'stop', container_name], stdout=subprocess.PIPE)
atexit.register(stop_container)


# Repeatedly check the container until it returns a valid response (i.e. it's ready).
while True:
    print("Checking dump is ready...")
    try:
        with urlopen(f"http://localhost:8080/pokemon/1") as response:
            break
    except:
        time.sleep(1)


dump = {'egg_groups': [],
        'gender_rates': [],
        'moves': []}

pokemon_ids = chain(range(1, 1025 + 1), range(10001, 10277 + 1))
for id in pokemon_ids:
    with urlopen(f"http://localhost:8080/pokemon/{id}") as response:
        body = response.read()
    pokemon = json.loads(body)
    print(f"Loading Pokemon {id} {pokemon['name']}...")

    with urlopen(f"http://localhost:8080/pokemon-species/{pokemon['species']['name']}") as response:
        body = response.read()
    pokemon_species = json.loads(body)

    dump['gender_rates'].append({
        'pokemon': pokemon['name'],
        'gender_rate': pokemon_species['gender_rate']
    })

    for egg_group in pokemon_species['egg_groups']:
        dump['egg_groups'].append({
            'pokemon': pokemon['name'],
            'egg_group': egg_group['name']
        })

    for move in pokemon['moves']:
        for version_group_detail in move['version_group_details']:
            dump['moves'].append({
                'pokemon': pokemon['name'],
                'move': move['move']['name'],
                'learn_method': version_group_detail['move_learn_method']['name'],
                'version_group': version_group_detail['version_group']['name'],
            })


print('Writing to dump.json...')
with open('dump.json', 'w') as dump_json:
    json.dump(dump, dump_json, indent=2)
