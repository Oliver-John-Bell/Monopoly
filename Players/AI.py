from typing import Optional, List, Dict, Tuple
from Players import Player
from Core import Game
from Board import Ownable_Space
from Space_Types import Property
from Board import Ownable_Card

class AI(Player):
    def __init__(self, name: str, starting_balance: int):
        super().__init__(name, starting_balance)

    # === Core Turn Logic ===
    def decide_turn_actions(self, game: Game) -> None:
        """
        Determine and execute the AI's actions for this turn:
        - Build houses
        - Unmortgage properties
        - Propose trades
        """
        actions = self.prioritize_actions(game)

        for action in actions:
            if action == "unmortgage":
                for card in self.decide_unmortgage(game):
                    self.unmortgage_property(card)

            elif action == "build":
                for prop in self.decide_build(game):
                    game.bank.upgrade_property(prop.get_card())

            elif action == "trade":
                trade = self.decide_trade(game)
                if trade:
                    proposer, offer, request = trade
                    self.trade(self, proposer, offer, request)

            elif action == "mortgage":
                for card in self.decide_mortgage(game):
                    self.mortgage_property(card)

    def decide_jail_strategy(self, game: Game) -> str:
        """
        Determine how to handle being in jail.
        Returns one of: "use_card", "pay_bail", or "roll".
        """
        if self.use_get_out_of_jail_free_card():
            return "use_card"
        if self.can_afford(game.config.get("Bail_Amount", 50)):
            return "pay_bail"
        return "roll"

    def decide_buy(self, property: Ownable_Space, game: Game) -> bool:
        """
        Decide whether to buy a property the AI has landed on.
        Return True to buy, False to decline.
        """
        value = self.evaluate_property_value(property, game)
        return value >= property.buying_price

    def decide_build(self, game: Game) -> List[Property]:
        """
        Return a list of properties to build houses on this turn.
        """
        build_list = []
        for card in self.owned_properties:
            if hasattr(card, 'houses') and card.houses < 5:
                group = card.location.group
                if group.count_owned(self) == len(group.properties):
                    if self.can_afford(card.location.build_cost):
                        build_list.append(card.location)
        return build_list

    def decide_sell(self, game: Game) -> List[Property]:
        """
        Return a list of properties to downgrade/sell buildings from.
        """
        sell_list = []
        for card in self.owned_properties:
            if hasattr(card, 'houses') and card.houses > 0:
                sell_list.append(card.location)
        return sell_list

    def decide_trade(self, game: Game) -> Optional[Tuple[Player, Dict, Dict]]:
        """
        Return a proposed trade as (target_player, offer_dict, request_dict), or None.
        """
        pass

    def decide_mortgage(self, game: Game) -> List[Ownable_Card]:
        """
        Return a list of property cards to mortgage for cash.
        """
        mortgage_list = []
        for card in self.owned_properties:
            if not card.mortgaged and self.project_cashflow_risk(game) != "safe":
                mortgage_list.append(card)
        return mortgage_list

    def decide_unmortgage(self, game: Game) -> List[Ownable_Card]:
        """
        Return a list of property cards to unmortgage this turn.
        """
        unmortgage_list = []
        for card in self.owned_properties:
            if card.mortgaged:
                cost = int(card.location.mortgage_value * 1.1)
                if self.can_afford(cost):
                    unmortgage_list.append(card)
        return unmortgage_list

    # === Auction ===
    def decide_auction_bid(self, property: Ownable_Space, current_bid: int, game: Game) -> int:
        """
        Return the maximum bid the AI is willing to make for a property in auction.
        Return 0 to pass.
        """
        value = self.evaluate_property_value(property, game)
        if value > current_bid:
            increment = min(100, value - current_bid)
            return current_bid + increment
        return 0

    # === Evaluation ===
    def evaluate_property_value(self, property: "Ownable_Space", game: "Game") -> int:
        """
        Evaluate how much this property is worth to the AI based on monopoly potential,
        blocking others, scarcity, and current balance.
        """
        group = property.group
        group_props = group.properties
        owned_by_self = group.count_owned(self)
        total_in_group = len(group_props)
        owned_by_others = sum(1 for p in group_props if p.get_card().owner not in [None, self])
        remaining_unowned = sum(1 for p in group_props if p.get_card().owner is None)

        base_value = property.buying_price

        if owned_by_self == total_in_group - 1:
            base_value *= 1.75  # Completing monopoly
        elif owned_by_others == total_in_group - 1:
            base_value *= 1.5  # Blocking opponent

        remaining_ownables = sum(1 for p in game.board.spaces if isinstance(p, Ownable_Space) and p.get_card().owner is None)
        scarcity_multiplier = 1.1 if remaining_ownables < 10 else 1.0
        base_value *= scarcity_multiplier

        max_bid = self.balance - self.calculate_safe_cash_reserve(game)
        return min(int(base_value), max_bid)

    def evaluate_group_value(self, group_name: str, game: Game) -> int:
        """
        Evaluate the strategic value of an entire group (monopoly potential, rent, build cost).
        """
        group = game.board.groups.get(group_name)
        if not group:
            return 0

        total_value = 0
        for prop in group.properties:
            card = prop.get_card()
            value = prop.buying_price
            if hasattr(card, 'houses'):
                value += card.houses * prop.build_cost
            total_value += value

        monopoly_factor = 2 if group.count_owned(self) == len(group.properties) else 1
        return total_value * monopoly_factor

    def calculate_safe_cash_reserve(self, game: Game) -> int:
        """
        Calculate how much cash the AI wants to keep in reserve.
        """
        avg_rent = 0
        opponent_properties = [p for p in game.board.spaces if isinstance(p, Ownable_Space) and p.get_card().owner not in [None, self]]
        if opponent_properties:
            rent_values = [sum(card.rent.values()) / len(card.rent) for card in (p.get_card() for p in opponent_properties)]
            avg_rent = sum(rent_values) / len(rent_values)
        return max(200, int(avg_rent * 2))  # Keep at least double the average rent

    def project_cashflow_risk(self, game: Game) -> str:
        """
        Analyze rent risk based on opponents' properties.
        Returns: "safe", "moderate", or "danger"
        """
        high_rent_zones = [p.get_card().rent[max(p.get_card().rent.keys())] for p in game.board.spaces
                           if isinstance(p, Ownable_Space) and p.get_card().owner not in [None, self]]
        if not high_rent_zones:
            return "safe"

        risk_threshold = max(high_rent_zones)
        if self.balance >= risk_threshold * 2:
            return "safe"
        elif self.balance >= risk_threshold:
            return "moderate"
        else:
            return "danger"

    # === Analysis ===
    def predict_landing_distribution(self, game: Game) -> Dict[str, float]:
        """
        Estimate the chance of landing on each property in the next few turns.
        """
        steps_ahead = 12
        distribution = {}
        board_size = len(game.board.spaces)

        for i in range(2, steps_ahead + 1):  # Typical dice roll is 2-12
            pos = (self.position + i) % board_size
            space = game.board.spaces[pos]
            distribution[space.name] = distribution.get(space.name, 0) + 1

        total = sum(distribution.values())
        return {name: count / total for name, count in distribution.items()}

    def prioritize_actions(self, game: Game) -> List[str]:
        """
        Return a list of recommended actions this turn, sorted by importance.
        """
        priorities = []
        risk = self.project_cashflow_risk(game)

        if risk == "danger":
            priorities.append("mortgage")
        if self.balance > 300:
            priorities.append("unmortgage")
            priorities.append("build")
        if risk != "safe":
            priorities.append("trade")
        priorities.append("end_turn")

        return priorities
    # === Trading Strategy ===
    def is_trade_worth_it(self, offer: Dict, request: Dict, game: Game) -> bool:
        """
        Evaluate if the proposed trade is favorable.
        """
        pass

    def select_trade_partner(self, game: Game) -> Optional[Player]:
        """
        Select a player to propose a trade to.
        """
        pass

    def generate_trade_offer(self, game: Game) -> Tuple[Dict, Dict]:
        """
        Create a trade offer dictionary (offering and requesting resources).
        """
        pass

    # === Endgame ===
    def switch_to_endgame_mode(self, game: Game) -> bool:
        """
        Return True if AI should adopt an endgame strategy (e.g., last 2 players).
        """
        pass
