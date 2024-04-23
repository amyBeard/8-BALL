import phylib;
import sqlite3;
import os;
import math;

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS
FRAME_RATE = 0.06

# add more here

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />"""
FOOTER = """</svg>\n"""

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "DEEPPINK",
    "DEEPPINK",
    "DEEPPINK",
    "DEEPPINK",
    "DEEPPINK",
    "DEEPPINK",
    "DEEPPINK",
    "REBECCAPURPLE",
    "GOLD",
    "GOLD",
    "GOLD",
    "GOLD",
    "GOLD",
    "GOLD",
    "GOLD", 
    ]

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 )
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall


    # add an svg method here
    def svg( self ):
        colour = BALL_COLOURS[self.obj.still_ball.number % len(BALL_COLOURS)]
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n"""% (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, colour)

################################################################################
class RollingBall( phylib.phylib_object ):
    """
    Python RollingBall class.
    """

    def __init__( self, number, pos, vel, acc ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0 )
      
        # this converts the phylib_object into a RollingBall class
        self.__class__ = RollingBall


    # add an svg method here
    def svg( self ):
        colour = BALL_COLOURS[self.obj.rolling_ball.number % len(BALL_COLOURS)]
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n"""% (self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, colour)

################################################################################
class Hole( phylib.phylib_object ):
    """
    Python Hole class.
    """

    def __init__( self, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HOLE, 
                                       pos,
                                       None, None, None, 
                                       0.0, 0.0 )
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = Hole


    # add an svg method here
    def svg( self ):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n"""% (self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)

################################################################################
class HCushion( phylib.phylib_object ):
    """
    Python HCushion class.
    """

    def __init__( self,y):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HCUSHION, 
                                       None, 
                                       None, None, None, 
                                       0.0,y)
      
        # this converts the phylib_object into a HCushion class
        self.__class__ = HCushion


    # add an svg method here
    def svg( self ):
        if self.obj.hcushion.y == 0:
            y = -25
        else:
            y = 2700
        return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n"""%y

################################################################################
class VCushion( phylib.phylib_object ):
    """
    Python VCushion class.
    """

    def __init__( self, x ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_VCUSHION, 
                                       None, 
                                       None, None, None, 
                                        x , 0.0 )
      
        # this converts the phylib_object into a VCushion class
        self.__class__ = VCushion

    # add an svg method here
    def svg( self ):
        if self.obj.vcushion.x == 0:
            x = -25
        else:
            x = 1350
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n"""%x

################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self )
        self.current = -1

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other )
        return self

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self )
        if result:
            result.__class__ = Table
            result.current = -1
        return result

    # add svg method here
    def svg(self):
        svg_representation = HEADER  # Append the header outside the loop
        for obj in self:
            if obj is not None:
                svg_representation += obj.svg()  # Append SVG content for each object
        svg_representation += FOOTER  # Append the footer outside the loop
        return svg_representation

    def roll( self, t ):
        new = Table()
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number,
                Coordinate(0,0),
                Coordinate(0,0),
                Coordinate(0,0) )
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t )
                # add ball to table
                new += new_ball
            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number,
                Coordinate( ball.obj.still_ball.pos.x,
                ball.obj.still_ball.pos.y ) )
                # add ball to table
                new += new_ball
        # return table
        #print(new)
        return new
    
    def cueBall( self, table, xvel, yvel):

        for ball in table:
            if isinstance(ball, StillBall):
                if ball.obj.still_ball.number == 0:
                    xpos = ball.obj.still_ball.pos.x
                    ypos = ball.obj.still_ball.pos.y
                    ball.type = phylib.PHYLIB_ROLLING_BALL
                    cue_ball = ball.obj.rolling_ball
                    cue_ball.number = 0

        cue_ball.pos.x = xpos
        cue_ball.pos.y = ypos

        cue_ball.vel.x = xvel
        cue_ball.vel.y = yvel

        rb_speed = math.sqrt( xvel**2 + yvel**2 )
        rb_acc_x = 0.0
        rb_acc_y = 0.0

        if rb_speed > VEL_EPSILON:
            rb_acc_x = (-1.0 * xvel) / rb_speed * DRAG
            rb_acc_y = (-1.0 * yvel) / rb_speed * DRAG
            if (rb_acc_x == -0.0):
                rb_acc_x *= -1.0
            if (rb_acc_y == -0.0):
                rb_acc_y *= -1.0
        acc = Coordinate(rb_acc_x, rb_acc_y)
        cue_ball.acc.x = acc.x
        cue_ball.acc.y = acc.y


################################################################################
class Database():

    def __init__( self, reset=False ):

        if os.path.exists( 'phylib.db' ) and reset == True:
            os.remove( 'phylib.db' )

        self.conn = sqlite3.connect( 'phylib.db' )

    def createDB(self):
        cur = self.conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS Ball 
                        (BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
                        BALLNO INTEGER NOT NULL,
                        XPOS FLOAT NOT NULL,
                        YPOS FLOAT NOT NULL,
                        XVEL FLOAT,
                        YVEL FLOAT);""")

        cur.execute("""CREATE TABLE IF NOT EXISTS TTable 
                        (TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                        TIME FLOAT NOT NULL);""")

        cur.execute("""CREATE TABLE IF NOT EXISTS BallTable
                        (BALLID INTEGER NOT NULL,
                        TABLEID INTEGER NOT NULL,
                        FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
                        FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID));""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Shot
                        (SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                        PLAYERID INTEGER NOT NULL,
                        GAMEID INTEGER NOT NULL,
                        FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
                        FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID));""")

        cur.execute("""CREATE TABLE IF NOT EXISTS TableShot
                        (TABLEID INTEGER NOT NULL,
                        SHOTID INTEGER NOT NULL,
                        FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                        FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID));""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Game
                        (GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                        GAMENAME VARCHAR(64) NOT NULL);""")

        cur.execute("""CREATE TABLE IF NOT EXISTS Player
                        (PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                        GAMEID INTEGER NOT NULL,
                        PLAYERNAME TEXT NOT NULL,
                        FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID));""")
        
        cur.close()
        self.conn.commit()

    
    def readTable( self, tableID ):

        cur = self.conn.cursor()

        table= Table()

        tableID += 1
        balls = cur.execute("""SELECT Ball.BALLID, Ball.BALLNO, Ball.XPOS, Ball.YPOS, Ball.XVEL, Ball.YVEL 
                        FROM Ball 
                        JOIN BallTable ON Ball.BALLID = BallTable.BALLID 
                        WHERE BallTable.TABLEID = ?""", (tableID,))

        ball_info = balls.fetchall()
        if (len(ball_info) == 0):
            return None
        else:
            for ball in ball_info:
                pos = Coordinate(ball[2], ball[3])
                num = ball[1]
                if (ball[4] == None and ball[5] == None):
                    sb = StillBall(num, pos)
                    table+=sb
                else:
                    vel = Coordinate(ball[4], ball[5])
                    rb_speed = math.sqrt( ball[4]**2 + ball[5]**2 )
                    rb_acc_x = 0.0
                    rb_acc_y = 0.0

                    if rb_speed > VEL_EPSILON:
                        rb_acc_x = (-1.0 * ball[4]) / rb_speed * DRAG
                        rb_acc_y = (-1.0 * ball[5]) / rb_speed * DRAG
                        if (rb_acc_x == -0.0):
                            rb_acc_x *= -1.0
                        if (rb_acc_y == -0.0):
                            rb_acc_y *= -1.0
                    acc = Coordinate(rb_acc_x, rb_acc_y)

                    rb = RollingBall(num, pos, vel, acc)
                    table+=rb

            table_time = cur.execute("""SELECT TTable.TIME FROM TTable
                                        WHERE TTable.TABLEID = ?""", (tableID,))
            
            for time in table_time:
                table.time = time[0]
            
            #print(table)

        cur.close()
        self.conn.commit()

        return table
    
    def writeTable( self,table ):
        
        #print(table)

        cur = self.conn.cursor()

        cur.execute("INSERT INTO TTable (TIME) VALUES (?);", (table.time,))
        table_id = cur.lastrowid

        ball_ids = []
        for ball in table:
            if isinstance( ball, StillBall):
                # print(ball)
                cur.execute("""INSERT INTO Ball (BALLNO,    XPOS,   YPOS) 
                VALUES (?,  ?,  ?);""", (ball.obj.still_ball.number, ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y,))
                ball_ids.append(cur.lastrowid)

            if isinstance( ball, RollingBall):
                # print(ball)
                cur.execute("""INSERT INTO Ball (BALLNO,    XPOS,   YPOS,   XVEL,   YVEL) 
                VALUES (?,  ?,  ?,  ?,  ?);""", (ball.obj.rolling_ball.number, ball.obj.rolling_ball.pos.x, ball.obj.rolling_ball.pos.y,
                ball.obj.rolling_ball.vel.x, ball.obj.rolling_ball.vel.y,))
                ball_ids.append(cur.lastrowid)
        
        # print(ball_ids)
        for ball_id in ball_ids:
            #print(table_id, ball_id)
            cur.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?);", (ball_id, table_id))

        cur.close()
        self.conn.commit()

        return (table_id-1)

    def setGame( self, gameName, player1Name, player2Name ):

        cur = self.conn.cursor()
        
        cur.execute("INSERT INTO Game (GAMENAME) VALUES (?);", (gameName,))
        game_id = cur.lastrowid

        cur.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?);", (game_id, player1Name,))
        cur.execute("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?);", (game_id, player2Name,))

        cur.close()
        self.conn.commit()

        return game_id
    
    def getGame( self, game_id):
        
        cur = self.conn.cursor()

        game_data = cur.execute("""SELECT Player.PLAYERID, Player.PLAYERNAME FROM Player
                                        WHERE Player.GAMEID = ?""", (game_id,))
        
        players = game_data.fetchall()

        if players[0][0] < players[1][0]:
            player1 = players[0][1]
            player2 = players[1][1]
        else:
            player1 = players[1][1]
            player2 = players[0][1]

        game_data2 = cur.execute("""SELECT Game.GAMENAME FROM Game
                                        WHERE Game.GAMEID = ?""", (game_id,))

        gameName = game_data2.fetchone()
        
        cur.close()
        self.conn.commit()

        return gameName[0], player1, player2
    
    def newShot( self, gameName, playerName):
        
        cur = self.conn.cursor()

        player_id = cur.execute("""SELECT Player.PLAYERID FROM Player
                                        WHERE Player.PLAYERNAME = ?""", (playerName,))

        player_id = player_id.fetchone()[0]

        game_id = cur.execute("""SELECT GAME.GAMEID FROM Game
                                        WHERE Game.GAMENAME = ?""", (gameName,))
        game_id = game_id.fetchone()[0]
        
        cur.execute("INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?);", (player_id, game_id,))

        shot_id = cur.lastrowid

        cur.close()
        self.conn.commit()

        return shot_id
    
    def tableShot( self, tableID, shotID):

        cur = self.conn.cursor()

        cur.execute("INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?);", (tableID, shotID,))

        cur.close()
        self.conn.commit()
    

    def close( self ):
        self.conn.commit()
        self.conn.close()
    

################################################################################
class Game():

    def __init__( self, gameID=None, gameName=None, player1Name=None, player2Name=None ):
        
        db= Database()
        ################################################################################
        #Call game with just the gameID
        if gameID!= None:
            
            self.gameID = int(gameID)+1

            game_info = db.getGame(self.gameID)

            self.gameName = game_info[0]
            self.player1Name = game_info[1]
            self.player2Name = game_info[2]

            #print(self.gameID, self.gameName, self.player1Name, self.player2Name)

        ################################################################################
        #Call game with gameName, player1Name, and player2Name
        elif gameName != None and player1Name != None and player2Name != None:
            
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            
            self.gameID = db.setGame(self.gameName, self.player1Name, self.player2Name)

            #print(self.gameID, self.gameName, self.player1Name, self.player2Name)

        ################################################################################
        else:
            raise TypeError("Invalid Constructor for Game Class")
            
        ################################################################################
    
    def shoot( self, gameName, playerName, table, xvel, yvel ):
        
        db = Database()
        table = table
        shot_id = db.newShot(gameName, playerName)

        table.cueBall(table, xvel, yvel)

        while table:
            segment_table = table.segment()
            if segment_table is None:
                print(table)
                table_id = db.writeTable(table)
                db.tableShot(table_id, shot_id)
                break

            segment_length = int((segment_table.time - table.time) / FRAME_RATE)

            for i in range (segment_length):
                new_table = table.roll(i * FRAME_RATE)
                new_table.time = (table.time + i * FRAME_RATE)

                table_id = db.writeTable(new_table)
                db.tableShot(table_id, shot_id)
            
            print(table)
            table = segment_table
    
