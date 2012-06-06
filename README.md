Shoreditch EshwariAI
=====================

This AI has been built to compete in SiliconMilkRoundabout Competition

Get it running
==============

To get the AI running it's easiest to set up a virtualenv, install the requirements, then run player.py, like so:
	virtualenv ve
	source ve/bin/activate
	pip install -r requirements
	python player.py

The AI runs on 8099 
Logic behind the AI
-------------------

The main objective is to understand the previous actions of the opponents to make calculate better trades.

Basic overview
--------------

When a game is started, the `start_game` method will be called.

When it's your turn to take a turn, the `start_turn` method will be called. the `actions` parameter includes a list of actions taken by other players since your last turn. All turn actions should be taken in this method, and the method should end with game.end_turn().

If the turn runs out the `time_up` method will be called. When this is called it also sets game.turn to be False, which can be checked in the `start_turn` method.

`end_game` will be called when a game is over. Error will be set if there was a problem (e.g. another player doesn't exist), otherwise it will be None. This method can be used to clean up temporary data from the game.

`incoming_trade` will be called when a trade is offered from another player. `player` is the ID of the player offering the trade, `offering` is resource -> number of what is being offered for trade, `requestings` is resource -> number of what the other person wants for trade. Return True to accept the offer and False to reject.

game
-----
The object "game" is passed in all calls, and it represents the game in progress.

a Game has the following attributes:

* `game` which is the unique id of the game
* `resources` which is resource -> number for every resource the player has
* `generators` which is resource -> number for every basic generator the player has
* `improved_generators` which is resource -> number for every improved generator the player has
* `pr` which is the amount of PR the player has
* `customers` which is the amount of customers the player has
* `turn` which indicates if it's the player's turn or not

and the following methods:

* `can_purchase_pr` returns True if the player has enough resources to purchase PR
* `can_purchase_generator` returns true if the player has enough resources to purchase a generator and doesn't have more than the maximum limit
* `can_upgrade_generator` returns true if the player has enough resources to upgrade a generator, doesn't have more than the maximum limit, and has at least one generator to be upgraded
* `purchase_pr` will purchase 1 PR, returning True if the player now has the most PR in the game (and a 2 customer bonus), and false if they do not.
* `purchase_generator` will purchase 1 random generator, returning the generator type purchased. If you cannot purchase a generator it will return False
* `upgrade_generator` will upgrade either the generator type passed as the first parameter, or a random generator. If it is able to upgrade the generator it will return the type of the generator upgraded, otherwise it will return False.
* `trade` should be called with `offering` and `requesting` as resource -> number indicating what is being offered/requested. This will return the id of the user who accepted, if it is accepted (or "bank" if accepted by the bank), and False if it is rejected.
* `end_turn` will end then turn.

db
----

The object "db" is passed in all calls, and it can be used to store information across requests. It supports the following calls:
* db.save(doc) - Save a document to the store (with a unique 'id' key) - if no id is present in the document, one is generated and returned.
* db.get(id) - Get a doc from the store by its id
* db.exists(id) - Does a document with the given id exist?
* db.get_by_keys([keys]) - Get a number of documents by keys


