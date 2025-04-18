# save.py
import os
import json
from typing import Dict, Any
from Data.Config import load_spaces, load_config, load_chance, load_community_chest
from Data.Saves import load_save
from board import Board
from Cards import Deck
from bank import Bank
from dice import Dice
from Players import Player

def save_game(game, save_slot: int):
    """
    Saves the current game state to a JSON file.
    """
    save_folder = 'Saves'
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    save_file = os.path.join(save_folder, f'Save_{save_slot}.json')

    game_state = {
        "Config": game.config,
        "Players": [player.to_dict() for player in game.players],
        "Current_Turn": game.current_turn,
        "Bank": game.bank.to_dict(),
        "Save_Slot": save_slot
    }

    with open(save_file, 'w') as file:
        json.dump(game_state, file, indent=4)

    print(f"Game saved successfully in slot {save_slot}.")

def load_game(game, save_slot: int):
    """
    Loads a saved game state from a JSON file into an existing Game instance.
    """
    try:
        game_state: Dict[str, Any] = load_save(save_slot)
    except FileNotFoundError as e:
        print(str(e))
        return

    game.config = game_state.get("Config", load_config())
    game.bank = Bank(**game_state.get("Bank", {"houses": 32, "hotels": 16}))
    game.dice = Dice(game.config)
    game.save_slot = save_slot
    game.current_turn = game_state.get("Current_Turn", 0)

    # Load board and decks
    decks_data = {"Chance": load_chance(), "Comunity_Chest": load_community_chest()}
    game.decks = {
        "Chance": Deck(decks_data["Chance"]),
        "Comunity_Chest": Deck(decks_data["Comunity_Chest"])
    }
    game.board = Board(load_spaces(), game.config, game.decks)

    # Link cards to players
    card_lookup = {space.name: card for space, card in game.board.ownable_properties().items()}
    game.players = [Player.from_dict(p_data, card_lookup) for p_data in game_state.get("Players", [])]

    # Remove Jail cards from decks
    if any(p.get_out_of_jail_free_cards[0] for p in game.players):
        game.decks["Chance"].remove_card("get_out_of_jail_free")
    if any(p.get_out_of_jail_free_cards[1] for p in game.players):
        game.decks["Comunity_Chest"].remove_card("get_out_of_jail_free")

    print(f"Game loaded successfully from slot {save_slot}.")

def delete_save(save_slot: int):
    """
    Deletes the specified save file.
    """
    save_folder = 'Saves'
    save_file = os.path.join(save_folder, f'Save_{save_slot}.json')
    if os.path.exists(save_file):
        os.remove(save_file)
        print(f"Save slot {save_slot} deleted successfully.")
    else:
        print(f"Save {save_slot} does not exist.")

def list_saves():
    """
    Lists all available save files in the Saves folder.
    """
    save_folder = 'Saves'
    if os.path.exists(save_folder):
        saves = os.listdir(save_folder)
        print("Available save files:")
        for save in saves:
            print(save)
        return saves
    else:
        print("No saves found.")
        return []