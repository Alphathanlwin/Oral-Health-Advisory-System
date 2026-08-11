parent(john, mary).
parent(mary, alice).
parent(john, bob).
parent(bob, sam).

grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).