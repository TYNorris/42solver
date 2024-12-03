from __future__ import annotations
from src.dominoes import Domino, Suit
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.gameplay import Player, Trick, Play


class Bid( object ):
    """A bid."""

    def __init__( self, player: Player, contract: Contract, bid: Bid ):
        """Constructor."""

        self.bid = bid
        self.contract = contract
        self.player = player

class Contract( object ):
    """A contract."""

    def adjudicate( self, trick: Trick, player: Player, play: Play ):
        """Determine the result of the specified play in the specified trick."""

    def identify( self, trick: Trick, domino: Domino ):
        """Identifies the suit and trump status of the specified domino  in the specified trick."""

class TrumpContract( Contract ):
    """A trumps contract."""

    def __init__( self, trump: Suit):
        """Constructor."""

        self.trump = trump

    def adjudicate( self, trick: Trick, player: Player, play: Play ):
        """Determine the result of the specified play in the specified trick."""

        trump, winner = self.trump, trick.winning_play
        if play.trump:
            if trick.suit is trump:
                play.role = 'suit'
                if trump.higher( play.domino , winner.domino  ):
                    trick.winning_play, trick.winning_player = play, player
            else:
                play.role = 'trump'
                if not winner.trump or trump.higher( play.domino , winner.domino  ):
                    trick.winning_play, trick.winning_player = play, player
        elif play.suit is trick.suit:
            play.role = 'suit'
            if not winner.trump and trick.suit.higher( play.domino , winner.domino  ):
                trick.winning_play, trick.winning_player = play, player
        else:
            play.role = 'off'
        
    def identify( self, trick, domino  ):
        """Identifies the suit and trump status of the specified domino  in the specified trick."""

        if self.trump.includes( domino  ):
            return self.trump, True
        elif trick.suit and trick.suit.includes( domino  ):
            return trick.suit, False
        else:
            return domino .suits[ 0 ], False

class NoTrumpContract( Contract ):
    """A no trump contract."""

    def __init__( self, doubles = 'high' ):
        """Constructor."""

        self.doubles = doubles

    def adjudicate( self, trick, player, play ):
        """Determine the result of the specified play in the specified trick."""

        winner = trick.winning_play
        if play.suit in trick.suit:
            play.role = 'suit'
            if trick.suit.higher( play.domino , winner.domino  ):
                trick.winning_play, trick.winning_player = play, player
        else:
            play.role = 'off'

    def identify( self, trick, domino  ):
        """Identifies the suit and trump status of the specified domino  in the specified trick."""

        if trick.suit and trick.suit.includes( domino  ):
            return trick.suit, False
        else:
            return domino .suits[ 0 ], False

