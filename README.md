# Pokemon Chain Breeding Solver

Determines a shortest set of breeding steps to produce a pokemon with a given
move.

## Motivation

Pokemon may learn [move](https://bulbapedia.bulbagarden.net/wiki/Move)s in a
variety of ways, including via [levelling up](https://bulbapedia.bulbagarden.net/wiki/Level)
or by [TM](https://bulbapedia.bulbagarden.net/wiki/TM)/[HM](https://bulbapedia.bulbagarden.net/wiki/HM).

In particular, a pokemon may learn a given move if the father (or mother,
post-Generation VI) knows the move. As an example, if a Male Skity knowing Wish
breeds with a female Eevee, the resulting offspring (an Eevee) will also know
Wish, despite Eevee not learning Wish via level-up or TM/HM. These moves are
termed [Egg move](https://bulbapedia.bulbagarden.net/wiki/Egg_Move)s.

However, in the above eample, Skitty _also_ can only learn Wish as an Egg Move.
We thus need to determine:

 - a "starting" parent that learns the move not as an Egg move.
 - the shortest sequence of breeding steps to produce the desired Pokemon with
   the Egg move.

## Dependencies

 - [clingo](https://github.com/potassco/clingo)
 - [Python](https://www.python.org/)
 - [Docker](https://www.docker.com/)

## Running

### Setup

We first need to produce a `dump.json` that can be re-used for solving. To
generate it, run the following script:

```sh
./dump.py
```

This only needs to be executed once.

### Solving

Run `solve.py`:

```sh
./solve.py -m wish -p eevee -v emerald
```

This will produce ouput like the following:

```
...
Solving...
Answer: 1
can_breed(skitty,eevee) can_breed(togetic,skitty)
Optimization: 2
OPTIMUM FOUND
...
```

This tells us that we found a the shortest set of breeding steps:

- `togetic` / `skitty`
- `skity` / `eevee`

This means we need to:
 - obtain a male Togetic that has learned the move Wish (which it can do via level-up),
 - breed it wih a female Skitty to obtain a male Skitty wih Wish.
 - breed this male Skitty wih a female Eevee to obtain an Eevee wih Wish.

## How it works

### [`dump.py`](./dump.py)

[`dump.py`](./dump.py) will pull down an [optimized dump](https://github.com/AlexandreCarlton/pokeapi-dump)
of [PokeAPI](https://pokeapi.co/) and produce a `dump.json` containing, for all pokemon:

 - egg moves across all version groups
 - gender rates
 - egg groups

This only needs to be run once; the `dump.json` can be re-used by the next
step.

### [`solve.py`](./solve.py)

[`solve.py`](./solve.py) is the workhorse of this project. It takes in:

  - a target pokemon
  - the desired egg move for the target pokemon
  - a version group (e.g. Crystal, Ruby/Sapphire)

and produces a minimal set of 'facts' as can be interpreted by
[Clingo](https://github.com/potassco/clingo) (a logic solver). An example of
these facts is as follows:

```prolog
learns_via(eevee, egg).
learns_via(skitty, egg).
learns_via(togetic, level_up).
% ...
egg_group(eevee, ground).
egg_group(skitty, ground).
egg_group(skitty, fairy).
egg_group(togetic, fairy).
egg_group(togetic, flying).
% ...
gender_rate(eevee, 1).
gender_rate(skity, 6).
gender_rate(togetic, 1).
```

We generate as few facts as possible to optimise Clingo's solving; as such, we
only:

 - generate `learns_via` facts for the desired move.
 - generate `egg_group` facts for pokemon found in `learns_via`.
 - generate `gender_rate` facts for pokemon found in `learns_via`.

We then combine this file with [`solver.pl`](./solver.pl) and run it through
Clingo. This `solver.pl` will try to find the minimal set of breeding steps
(should such a set exist) to produce a pokemon - the above example will
produce:

```
...
Solving...
Answer: 1
can_breed(skitty,eevee) can_breed(togetic,skitty)
Optimization: 2
OPTIMUM FOUND
...
```

## Further reading

 - [Chain breeding](https://bulbapedia.bulbagarden.net/wiki/Chain_breeding)
 - [Programming with CLINGO](https://www.cs.utexas.edu/~vl/teaching/378/pwc.pdf)
 - [A User’s Guide to gringo, clasp, clingo, and iclingo](https://wp.doc.ic.ac.uk/arusso/wp-content/uploads/sites/47/2015/01/clingo_guide.pdf)
