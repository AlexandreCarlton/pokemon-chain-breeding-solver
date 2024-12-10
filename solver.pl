% :vim:ft=prolog

% Contains a solver for determining the smallest number of eggs needed to produce a pokemon with a given egg move.
% It does this by treating each breeding as an 'edge' in a Graph, and minimising hte number of edges traversed
% to reach the desination.


% A pokemon potentially be always male or always female (or neither).
% Each integer bump represents a 12.5% chance to be female,
% so 0 means always male, 8 means always female, -1 is no gender.
can_be_father(Pokemon) :-
	% Post-generation VI the mother can also pass down the egg move;
	% however, this would create a redundant breeding step and so we disqualify this.
	gender_rate(Pokemon, Rate),
	Rate >= 0,
	Rate < 8.

can_be_mother(Pokemon) :-
	gender_rate(Pokemon, Rate),
	Rate > 0,
	Rate <= 8.


% This is our "edge" we want to minimise over.
% A given edge can only appear at most once in our solution (the '1' on the left)
0 { can_breed(Father, Mother) } 1 :-
	can_be_father(Father),
	can_be_mother(Mother),
	egg_group(Father, Group),
	egg_group(Mother, Group),
	Father != Mother.


% Base case - can pass down if the father can learn the move through any means, the mother via egg and they can breed.
can_pass_down(Father, Mother) :-
	learns_via(Father, _),
	learns_via(Mother, egg),
	can_breed(Father, Mother).
% Recursive case - Can pass down between two prospective generations.
can_pass_down(Grandfather, Mother) :-
	can_pass_down(Grandfather, Grandmother),
	Father=Grandmother, % Offspring of grandmother (the father, here) is same species as mother
	can_pass_down(Father, Mother).

% Chain can only exist if there's a father that can learn the move not as an egg move.
can_learn(Mother) :-
	learns_via(Father, Method),
	Method!=egg,
	can_pass_down(Father, Mother).


% Remove all solutions where, for a given target, they cannot learn the move.
:-
	target(Mother), not can_learn(Mother).

% Make the 'cost' of a breeding chain the number of times we see 'can_breed'.
cost(C) :-
	C = #count { Father, Mother : can_breed(Father, Mother) }.

#minimize { C : cost(C) }.
#show can_breed/2.
