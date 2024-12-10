#!/usr/bin/env python3

"""
Determines a shortest set of breeding steps to produce a pokemon with a given
move in a given version group.

As an example:

    ./solve.py --pokemon nosepass --move endure --version-group x-y

It does this by taking our existing dump.json and producing the smallest
feasible set of facts (to optimise runtime) and runs clingo on this.
"""

import argparse
import json
import tempfile
import subprocess


parser = argparse.ArgumentParser(prog='Find shortest breeding path for a pokemon/move in a given version group.')
parser.add_argument('-m', '--move', required=True)
parser.add_argument('-p', '--pokemon', required=True)
parser.add_argument('-v', '--version-group', required=True)
args = parser.parse_args()

with open('dump.json') as dump_json:
    dump = json.load(dump_json)

# Grab only the pokemon/learn method that match our move/vesion group.
moves = [{'pokemon': m['pokemon'], 'learn_method': m['learn_method']}
         for m in dump['moves']
         if m['move'] == args.move and m['version_group'] == args.version_group]

# Grab the pokemon that can learn the move we're interested in.
pokemon = {m['pokemon'] for m in moves}

# Grab the egg groups for the pokemon that can learn the move we're interested in.
egg_groups = [g for g in dump['egg_groups'] if g['pokemon'] in pokemon]

# Grab the gender rates for the pokemon that can learn the move we're interested in.
gender_rates = [r for r in dump['gender_rates'] if r['pokemon'] in pokemon]

with tempfile.NamedTemporaryFile(mode='a') as facts:
    for egg_group in egg_groups:
        print(f"egg_group({egg_group['pokemon'].replace('-', '_')}, {egg_group['egg_group'].replace('-', '_')}).", file=facts)
    for gender_rate in gender_rates:
        print(f"gender_rate({gender_rate['pokemon'].replace('-', '_')}, {gender_rate['gender_rate']}).", file=facts)
    for move in moves:
        print(f"learns_via({move['pokemon'].replace('-', '_')}, {move['learn_method'].replace('-', '_')}).", file=facts)
    print(f"target({args.pokemon}).", file=facts)
    facts.flush()

    # subprocess.run(['cat', facts.name]) # Useful to poke at the generated facts.
    subprocess.run(['clingo', '--opt-mode=optN', '--quiet=1', 'solver.pl', facts.name])
