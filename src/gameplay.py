
from __future__ import annotations
from src.dominoes import Domino, RandomDeck, Suits, Dominoes
from src.contract import Bid, TrumpContract
from src.util import reorder, shuffle
from src.evaluate import *

class Player( object ):
    """A player in a particular game."""

    def __init__( self, team: Team, name: str, controller ):
        """Constructor."""

        self.controller = controller    #
        self.hand: Hand = None                #
        self.name = name                #  Name of player
        self.team = team                #
        self.trick_evaluation:playEvaluation = None    #  trick_evaluation object

    def __repr__( self ):
        return 'Player(%s)' % self.name

    def __str__( self ):
        return self.name

    def offer( self, round: Round ) -> Bid:
        """Offer a bid for the specified round."""

        print('')
        print('                             : CONTROL : MAJORITY')
        evaluation = []
        for s in [Suits['blanks'], Suits['ones'], Suits['twos'], Suits['threes'], Suits['fours'], Suits['fives'], Suits['sixes']]:
            evaluation.append(bidEvaluation(self.hand, s))
            evaluation[-1].evaluate()

            '''
            print('5:5 vulnarability : ', calcVulnerability(offs, leadingOffs, s, Dominoes[(5, 5)]()))
            print('6:4 vulnerability : ', calcVulnerability(offs, leadingOffs, s, Dominoes[(6, 4)]()))
            print(controlProbability(self.hand, Suits['fours'], s))
            print(controlProbability(self.hand, Suits['sixes'], s))
            print('4:1 vulnerability : ', calcVulnerability(offs, leadingOffs, s, Dominoes[(4, 1)]()))
            print('3:2 vulnerability : ', calcVulnerability(offs, leadingOffs, s, Dominoes[(3, 2)]()))
            print('5:0 vulnerability : ', calcVulnerability(offs, leadingOffs, s, Dominoes[(5, 0)]()))
            '''
        print('%s has: %s' % ( self.name, self.hand.dump() ))
        #bid = []
        #for e in evaluation:
        #    bid.append(e[0], calcBid(e))
        bid = input( 'Bid (enter to pass): ' )
        if bid:
            trump = input( 'Trump: ' )
            return Bid( self, TrumpContract( Suits[ trump ] ), int( bid ) )

    def play( self, trick: Trick ):
        """Plays a domino  in the specified trick."""

        print()
        print('trick is: %s' % ( trick.dump() ))
        print('%s has: %s' % ( self.name, self.hand.dump() ))

        identity = eval( input( 'Play: ' ) )

        domino  = self.hand.play( identity )
        return domino        

class Team( object ):
    """A team in a particular game."""

    def __init__( self, name: str ):
        """Constructor."""

        self.name = name
        self.players: list[Player] = []

    def __repr__( self ):
        return 'Team(%s: %s)' % ( self.name, ', '.join([ str( player ) for player in  self.players ]) )

    def __str__( self ):
        return self.name

    @property
    def shuffled_players( self ):
        """A list of players for this team in random order."""

        players = list( self.players )
        shuffle( players )
        return players

    def add( self, name: str, controller ):
        """Adds a player to this team."""

        self.players.append( Player( self, name, controller ) )

class Hand( object ):
    """A hand of Dominoes for a particular round."""

    def __init__( self, round: Round, player: Player, hand: list[Domino] ):
        """Constructor."""

        self.dominoes = hand
        self.hand = dict( ( domino.identity, domino  ) for domino  in hand )
        self.player = player
        self.round = round

    def __repr__( self ):
        """String representation."""

        Dominoes = ' '.join([ repr( domino  ) for domino  in self.dominoes ])
        return 'Hand( %s %s )' % ( self.player, Dominoes )

    def dump( self ) -> str:
        """ Prints a String representation for the Dominoes left in the hand. """
        return ' '.join([ repr( domino  ) for domino  in self.hand ])

    def play( self, identity ) -> Domino:
        """Plays a domino  from this hand."""

        domino  = self.hand.pop( identity, None )
        if domino :
            return domino 
        else:
            raise KeyError( 'invalid domino ' )

class Play( object ):
    """A played domino  in a particular trick."""

    def __init__( self, trick: Trick, id: int, player: Player, domino: Domino, suit: Suit, trump: Suit ):
        """Constructor."""

        self.domino  = domino 
        self.id = id
        self.player = player
        self.role = 'unknown'
        self.suit = suit
        self.trick = trick
        self.trump = trump

    def __repr__( self ):
        """String representation."""

        return 'Play( r%d:t%d:p%d %r %s by %s )' % ( self.trick.round.id, self.trick.id,
            self.id, self.domino , self.role, self.player )

class Trick( object ):
    """A trick in a particular round."""

    def __init__( self, round, id, players ):
        """Constructor."""

        self.id = id
        self.players = players
        self.plays = []
        self.round = round
        self.suit = None
        self.value = 1
        self.winning_play = None
        self.winning_player = None

    def __repr__( self ):
        """String representation."""

        plays = ' '.join([ repr( play.domino  ) for play in self.plays ])
        return 'Trick( r%d:t%d [ %s ] won by %s with %r for %dpt )' % ( self.round.id,
            self.id, plays, self.winning_player, self.winning_play.domino , self.value )

    def dump( self ):
        return ' '.join([ repr( play.domino  ) for play in self.plays ])

    def play( self, player: Player, domino: Domino  ):
        """Plays the specified domino  in this trick."""

        # construct the play and associate it with the trick
        suit, trump = self.round.bid.contract.identify( self, domino  )
        play = Play( self, len( self.plays ) + 1, player, domino , suit, trump )
        self.plays.append( play )

        # determine the effects of the play
        self.value += domino .value
        if self.winning_play:                # If this NOT is the first domino in the trick, figure out if it is a winner
            self.round.bid.contract.adjudicate( self, player, play )
            print('domino is a %s' % play.role)
        else:                                # else, THIS is the winning play, by default, as it is the first domino in the trick
            play.role = 'suit'
            self.suit, self.winning_play, self.winning_player = play.suit, play, player
            print('trick suit is %s' % self.suit.identity)

class Round( object ):
    """A round in a particular game."""

    def __init__( self, game: Game, id: int, players: list[Player], bid = None ):
        """Constructor."""
    
        self.bid: Bid = bid
        self.game = game
        self.hands = []
        self.id = id
        self.marks = 1
        self.players = players
        self.points_made = 0
        self.points_set = 0
        self.status = 'unknown'
        self.tricks = []

    @property
    def points_to_make( self ) -> int:
        """Indicates the points remaining for this bid to be made."""
        return self.bid.bid - self.points_made

    @property
    def points_to_set( self ) -> int:
        """Indicates the points remaining for this bid to be set."""
        return ( 43 - self.bid.bid ) - self.points_set

    def deal( self ):
        """Deals a hand to each player in this round."""

        hands = self.game.deck.deal()
        for hand, player in zip( hands, self.players ):
            player.hand = Hand( self, player, hand )
            self.hands.append( player.hand )

    def run( self ):
        """Runs this round."""

        # deal a hand to each player, then collect the bids
        print('%r vs. %r' % ( self.game.home, self.game.away ))
        self.deal()
        for player in self.players:
            bid = player.offer( self )
            if bid:
                self.bid = bid
        else:
            if not self.bid:
                return None
            else:
                for player in self.players:
                    player.trick_evaluation = playEvaluation

        # identify the number of marks for this hand, then normalize the bid value
        target = self.bid.bid
        if bid is int and bid > 42:
            self.marks, target = target / 42, 42

        # play tricks until the round is complete
        player = self.bid.player
        while True:

            # create the next trick and request a play from each player
            trick = Trick( self, len( self.tricks ) + 1, reorder( self.players, player ) )
            for player in trick.players:
                trick.play( player, player.play( trick ) )

            # reference the winning player and update the points totals
            player = trick.winning_player
            if player.team is self.bid.player.team:
                self.points_made += trick.value
            else:
                self.points_set += trick.value

            # associate the trick with this round and determine if the round is over
            self.tricks.append( trick )
            if self.points_made >= target:
                print('BID WAS MADE')
                self.status = 'made'
                break
            elif self.points_set >= ( 43 - target ):
                print('BID WAS SET')
                self.status = 'set'
                break

class Game( object ):
    """A game."""

    DefaultDeck = RandomDeck

    def __init__( self, home: Team, away: Team, deck = None, players: list[Player] = None ):
        """Constructor."""

        self.away = away
        self.deck = deck or self.DefaultDeck()
        self.home = home
        self.players = players or self.seat( home, away )
        self.rounds: list[Round] = []

    def seat( self, home, away ) -> list[Player]:
        """Determines a suitable seating order for the specified teams."""

        # shuffle the set of players for this game
        players = [ home.shuffled_players, away.shuffled_players ]
        shuffle( players )

        # generate the seating order for this game
        seating = []
        for pair in zip( *players ):
            seating.extend( pair )
        else:
            return seating

