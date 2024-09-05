#!/usr/bin/env python3

import click
import os
import sqlite3
import sys
from datetime import datetime

DB_FILE = 'pokemon.db'

def getdb():
    con = sqlite3.connect(DB_FILE)
    con.execute('PRAGMA foreign_keys = ON')
    return con

@click.group()
def cli():
    pass

@click.command()
@click.argument('pokedex_id')
@click.argument('move1')
@click.argument('move2')
@click.argument('move3')
@click.argument('move4')
#input a pokemon with custom moves. Could be useful in creating fully customized teams
def create_specific_pokemon(pokedex_id, move1, move2, move3, move4):
    with getdb() as con:
        c = con.cursor()
        c.execute("INSERT INTO specificpokemon (pokedex_id, move1, move2, move3, move4) VALUES (?,?,?,?,?)", (pokedex_id, move1, move2, move3, move4))
        con.commit()
    print(f"--> New Pokemon caught with id: {pokedex_id} with: {move1}, {move2}, {move3}, and {move4}")



@click.command()
@click.argument('pokemon1')
@click.argument('pokemon2')
@click.argument('pokemon3')
@click.argument('pokemon4')
@click.argument('pokemon5')
@click.argument('pokemon6')
def create_team(pokemon1, pokemon2, pokemon3, pokemon4, pokemon5, pokemon6):
    with getdb() as con:
        c = con.cursor()
        c.execute("INSERT INTO team (poke1, poke2, poke3, poke4, poke5, poke6) VALUES (?,?,?,?,?,?)", (pokemon1, pokemon2, pokemon3, pokemon4, pokemon5, pokemon6))
        con.commit()
    print(f"--> created team: [{pokemon1},{pokemon2},{pokemon3},{pokemon4},{pokemon5},{pokemon6}]")

@click.command()
@click.argument('team_id')
def team_coverage(team_id):
    #this query would look through all the pokemon on a team and sum up how many different types their moves cover
    with getdb() as con:
        c = con.cursor()
        c.execute("",team_id) #TODO
        coverage = c.fetchall()
        print(f"team {team_id} has a coverage of {coverage} types")
        con.commit()

@click.command()
def best_coverage():
    #this query could look through every pokemon's possible moves and see which pokemon have the best coverage possibility (top 10?)
    #tie could be settled with Base Stat Total
    with getdb() as con:
        c = con.cursor()
        c.execute("") #TODO
        data = c.fetchall()
        print(data)
        con.commit()

@click.command()
@click.argument('your_pokemon')
@click.argument('enemy_pokemon')
#currently a work in progress, fixing some bugs within the query
def powerful_moves(your_pokemon,enemy_pokemon):
    with getdb() as con:
        c = con.cursor()
        c.execute("""
WITH move_damage AS (
    SELECT 
        c.pokedex_id AS attacker_id,
        m.name AS move_name,
        m.pow AS move_power,
        m.moveType AS move_type,
        m.physical AS is_physical,
        t1.damagemultiplier AS type1_multiplier,
        t2.damagemultiplier AS type2_multiplier,
        p1.attack AS attacker_attack,
        p2.defense AS defender_defense,
        p1.special_attack AS attacker_special_attack,
        p2.special_defense AS defender_special_defense
    FROM canlearn AS c
    JOIN moves AS m ON c.move = m.name
    JOIN pokemon AS p1 ON c.pokedex_id = p1.pokedex_id
    JOIN pokemon AS p2 ON p2.pokedex_id = ?
    LEFT JOIN typeeffective AS t1 ON m.moveType = t1.attackingtype AND p2.type1 = t1.defendingtype
    LEFT JOIN typeeffective AS t2 ON m.moveType = t2.attackingtype AND IFNULL(p2.type2, '???') = t2.defendingtype
    WHERE c.pokedex_id IN (?, ?) 
)
SELECT 
    attacker_id,
    move_name,
    move_power * type1_multiplier * type2_multiplier AS total_damage,
    CASE 
        WHEN move_type = p1.type1 OR move_type = IFNULL(p1.type2, '???') THEN 1.5 
        ELSE 1 
    END AS type_bonus,
    CASE 
        WHEN is_physical = 1 THEN attacker_attack / defender_defense 
        ELSE attacker_special_attack / defender_special_defense 
    END AS attack_factor
FROM move_damage
WHERE total_damage = (
    SELECT MAX(move_power * type1_multiplier * type2_multiplier * type_bonus * attack_factor)
    FROM move_damage
)
""", (enemy_pokemon, your_pokemon, enemy_pokemon))
        moves = c.fetchall()
        print(moves)
        con.commit()

@click.command()
@click.argument('team_id')
@click.argument('enemy_pokemon')
def counterpick(team_id,enemy_pokemon):
    #this query could look through the team provided and see which pokemon has the best attack advantage over the provided enemy pokemon
    #more research needed to determine calculating best attack advantage
    with getdb() as con:
        c = con.cursor()
        c.execute("""
            SELECT pokemon_a.pokemon_id, SUM(damagemultiplier) AS score
            FROM team
            JOIN specificpokemon AS pokemon_a
                ON (pokemon_a.pokemon_id = poke1
                OR pokemon_a.pokemon_id = poke2
                OR pokemon_a.pokemon_id = poke3
                OR pokemon_a.pokemon_id = poke4
                OR pokemon_a.pokemon_id = poke5
                OR pokemon_a.pokemon_id = poke6)
            JOIN moves
                ON (moves.name = pokemon_a.move1
                OR moves.name = pokemon_a.move2
                OR moves.name = pokemon_a.move3
                OR moves.name = pokemon_a.move4)
            JOIN typeeffective
                ON attackingtype = moveType
            JOIN pokemon
                ON (defendingtype = type1
                OR defendingtype = type2)
            JOIN specificpokemon AS pokemon_b
                ON pokemon.pokedex_id = pokemon_b.pokedex_id
            
            WHERE teamid = ?
            AND pokemon_b.pokemon_id = ?
            
            GROUP BY pokemon_a.pokemon_id
            ORDER BY score
                """, (team_id, enemy_pokemon))
        pokemon = c.fetchall()
        print(pokemon)
        con.commit()


@click.command()
def topBST():
    with getdb() as con:
        c = con.cursor()
        c.execute("SELECT Name, BST FROM pokemon ORDER BY bst DESC LIMIT 10") #TODO: make it so the user can specify how many to return
        rows = c.fetchall()
        for row in rows: #go through the names collected and list all
            print(row)
        con.commit()

@click.command()
@click.argument('move')
# input a move and get a list of all pokemon who can learn that move
def shared_move(move):
    with getdb() as con:
        c = con.cursor()
        c.execute('''
        SELECT p.name, m.name AS move_name
        FROM pokemon p
        JOIN canlearn c ON p.pokedex_id = c.pokedex_id
        JOIN moves m ON c.move = m.name
        WHERE m.name = ?''', (move,))
        rows = c.fetchall()
        for row in rows:
            print(row)
        con.commit()

@click.command()
@click.argument('name')
#list all moves a specific pokemon can learn
def pokemon_moves(name):
    with getdb() as con:
        c = con.cursor()
        c.execute('''
        SELECT p.name, m.move 
        FROM canlearn AS m
        JOIN pokemon p ON m.pokedex_id = p.pokedex_id
        WHERE p.name = ?''', (name,))
        rows = c.fetchall()
        for row in rows:
            print(row)
        con.commit()

cli.add_command(create_specific_pokemon)
cli.add_command(create_team)
cli.add_command(team_coverage)
cli.add_command(best_coverage)
cli.add_command(powerful_moves)
cli.add_command(counterpick)
cli.add_command(topBST) #needs improvements but functional
cli.add_command(shared_move) #functional
cli.add_command(pokemon_moves) #functional
cli()



#EXAMPLE ON HOW TO DO CLI
#@click.group()
#def cli():
#    pass
#
#@click.command()
#@click.argument('email_addr')
#def insert_user(email_addr):
#    with getdb() as con:
#        c = con.cursor()
#        c.execute("INSERT INTO users (email_address) VALUES (?)", (email_addr,))
#        con.commit()
#    print("--> created user:", email_addr)
#
#cli.add_command(insert_user)

