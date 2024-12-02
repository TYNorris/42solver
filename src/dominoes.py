
from src.util import shuffle

Dominoes = {}
Deck = []
Suits = {}

class Domino( object ):
    """A domino."""

    class __metaclass__( type ):
        def __repr__( cls ):
            return "%s(%dpt)" % ( cls.__name__, cls.value )

    double = False
    identity = ()
    rank = {}
    suits = ()
    value = 0
    terms = ( 'Zero', 'One', 'Two', 'Three', 'Four', 'Five', 'Six' )

    def __lt__( self, other ):
        return self.identity > other.identity

    def __repr__( self ):
        return '%d:%d' % self.identity

    @classmethod
    def construct( cls, t, b ):
        """Constructs a version of this class for the specified domino ."""

        # re-worked to remove "jump" in ranks
        # i.e. rank(6,6)=7, (6,5)=5, (6,4)=4, (6,3)=3, (6,2)=2, (6,1)=1, (6,0)=0
        # should be...
        # rank(6,6)=6, (6,5)=5, (6,4)=4, (6,3)=3, (6,2)=2, (6,1)=1, (6,0)=0
        # rank(3,3)=6, (3,6)=5, (3,5)=4, (3,4)=3, (3,2)=2, (3,1)=1, (3,0)=0

        if t == b:
            rnk = {t:6}
        elif t > b:
            rnk = {t: b, b: t-1}
        else:
            rnk = {t: b-1, b: t}
        return type( '%s%s' % ( cls.terms[ t ], cls.terms[ b ] ), ( cls, ), {
            'double': ( t == b ),
            'identity': ( t, b ),
            'rank': ( rnk ),
            'value': ( t + b if ( t + b ) % 5 == 0 else 0 ),
        } )

for t in range( 6, -1, -1 ):
    for b in range( t, -1, -1 ):
        domino  = Dominoes[ ( t, b ) ] = Dominoes[ ( b, t ) ] = Domino.construct( t, b )
        Deck.append( domino  )

def suit( suit):
    """Constructs a suit implementation."""

    suit.dominoes = tuple([ Dominoes[ domino  ] for domino  in suit.dominoes ])
    if suit.value is not None:
        for domino  in suit.dominoes:
            if domino .suits:
                if domino .suits[ 0 ].value > suit.value:
                    domino .suits = ( domino .suits[ 0 ], suit )
                else:
                    domino .suits = ( suit, domino .suits[ 0 ] )
            else:
                domino .suits = ( suit, )

    Suits[ suit.identity ] = suit
    return suit

class Suit( object ):
    """A suit."""

    dominoes = ()
    identity = None
    value = None

    @classmethod
    def higher( cls, first, second ):
        """Indicates if the first domino  is higher than the second domino  within this suit."""

        return cls.dominoes.index( type( first ) ) < cls.dominoes.index( type( second ) )

    @classmethod
    def includes( cls, domino  ):
        """Determines if the specified domino  is part of this suit."""

        return ( type( domino  ) in cls.dominoes )

@suit
class Sixes( Suit ):
    dominoes = ( (6,6), (6,5), (6,4), (6,3), (6,2), (6,1), (6,0) )
    identity = 'sixes'
    value = 6

@suit
class Fives( Suit ):
    dominoes = ( (5,5), (5,6), (5,4), (5,3), (5,2), (5,1), (5,0) )
    identity = 'fives'
    value = 5

@suit
class Fours( Suit ):
    dominoes = ( (4,4), (4,6), (4,5), (4,3), (4,2), (4,1), (4,0) )
    identity = 'fours'
    value = 4

@suit
class Threes( Suit ):
    dominoes = ( (3,3), (3,6), (3,5), (3,4), (3,2), (3,1), (3,0) )
    identity = 'threes'
    value = 3

@suit
class Twos( Suit ):
    dominoes = ( (2,2), (2,6), (2,5), (2,4), (2,3), (2,1), (2,0) )
    identity = 'twos'
    value = 2

@suit
class Ones( Suit ):
    dominoes = ( (1,1), (1,6), (1,5), (1,4), (1,3), (1,2), (1,0) )
    identity = 'ones'
    value = 1

@suit
class Blanks( Suit ):
    dominoes = ( (0,0), (0,6), (0,5), (0,4), (0,3), (0,2), (0,1) )
    identity = 'blanks'
    value = 0

@suit
class Doubles( Suit ):
    dominoes = ( (6,6), (5,5), (4,4), (3,3), (2,2), (1,1), (0,0) )
    identity = 'doubles'
    value = None

class RandomDeck( object ):
    """A deck of dominoes."""

    def __init__( self, handsize = 7, handcount = 4, multiplier = 1, deck = Deck ):
        """Constructor."""

        self.deck = deck
        self.handcount = handcount
        self.handsize = handsize
        self.multiplier = multiplier

    def deal( self ):
        """Deals hands in random order."""

        # shuffle a new deck of dominoes
        deck = list( self.deck ) * self.multiplier
        shuffle( deck )

        # create and return the proper number of hands
        hands, handsize = [], self.handsize
        for i in range( self.handcount ):
            offset = i * handsize
            hands.append( tuple( sorted( domino () for domino  in deck[ offset:offset + handsize ] ) ) )
        else:
            return tuple( hands )

