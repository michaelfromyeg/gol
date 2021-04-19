FILENAME=conway_game_of_life.py

make lint:
	black $(FILENAME)

make run:
	python $(FILENAME)