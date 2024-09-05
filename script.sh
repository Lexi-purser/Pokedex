#!/bin/bash
rm -f pokemon.db

sqlite3 pokemon.db < schema.sql

python3 main.py create-specific-pokemon 3 Tackle Growl Toxic Growth         #Venusaur
python3 main.py create-specific-pokemon 6 Ember Growl Flamethrower Slash    #Charizard
python3 main.py create-specific-pokemon 9 Bubble Tackle Bite Counter        #Blastoise
python3 main.py create-specific-pokemon 19 Tackle Tackle Tackle Tackle      #Rattata

python3 main.py create-team 1 1 2 2 3 3 #create team with 2 Venu, 2 Char, 2 Blas

#python3 main.py powerful-moves 3 9 #Venusaur and Blastoise
