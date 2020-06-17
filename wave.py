"""
Subcontroller module for Alien Invaders

This module contains the subcontroller to manage a single level or wave in the Alien
Invaders game.  Instances of Wave represent a single wave.  Whenever you move to a
new level, you are expected to make a new instance of the class.

The subcontroller Wave manages the ship, the aliens and any laser bolts on screen.
These are model objects.  Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Piazza and we will answer.

Ronin Chasan (rcc263), Jacob Wise (jmw555)
December 4, 2018
"""
from game2d import *
from consts import *
from models import *
import random
import copy

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Wave is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Alien Invaders.

    This subcontroller has a reference to the ship, aliens, and any laser bolts on screen.
    It animates the laser bolts, removing any aliens as necessary. It also marches the
    aliens back and forth across the screen until they are all destroyed or they reach
    the defense line (at which point the player loses). When the wave is complete, you
    should create a NEW instance of Wave (in Invaders) if you want to make a new wave of
    aliens.

    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 24 for an example.  This class will be similar to
    than one in how it interacts with the main class Invaders.

    #UPDATE ME LATER
    INSTANCE ATTRIBUTES:
        _ship:   the player ship to control [Ship]
        _alien: the 2d list of aliens in the wave [rectangular 2d list of Alien or None]
        _bolts:  the laser bolts currently on screen [list of Bolt, possibly empty]
        _dline:  the defensive line being protected [GPath]
        _lives:  the number of lives left  [int >= 0]
        _time:   The amount of time since the last Alien "step" [number >= 0]

    As you can see, all of these attributes are hidden.  You may find that you want to
    access an attribute in class Invaders. It is okay if you do, but you MAY NOT ACCESS
    THE ATTRIBUTES DIRECTLY. You must use a getter and/or setter for any attribute that
    you need to access in Invaders.  Only add the getters and setters that you need for
    Invaders. You can keep everything else hidden.

    You may change any of the attributes above as you see fit. For example, may want to
    keep track of the score.  You also might want some label objects to display the score
    and number of lives. If you make changes, please list the changes with the invariants.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

        _fireRate: a randomly generated number between 1 and BOLT_RATE
        determining when alien bolts will be fired [int or float >= 1 and
        <= BOLT_RATE]

        _alienSteps: an integer between 0 and self._fireRate counting the number
        of steps aliens have taken since firing the last bolt
        [int >=0 and <= self._fireRate]

        _lives: the number of lives the player has remaining. Starts at
        SHIP_LIVES and is incremented down to 0 when the ship is destroyed
        [int <= SHIP_LIVES and >=0]

        _alienSpeed = the speed of the aliens, as set by the app.py

        _pewSound = sound made when ship fires bolt [Sound() object]

        _alienPew = sound made when alien fires bolt [Sound() object]

        _shipExplode = sound made when ship collides with bolt [Sound() object]

        _alienDie = sound made when alien collides with bolt [Sound() object]

        _muted = bool, is True if user mutes game, False otherwise [bool]

    """

    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    # INITIALIZER (standard form) TO CREATE SHIP AND ALIENS
    def __init__(self, view, input, speed):
        """
        Initializes a wave of alien objects.

        This method should make sure that all of the attributes satisfy the given
        invariants. It sets the x, y, height, width, and source of each alien object.
        """
        self._time = 0
        self._bolts = []
        self._alien = self.fill()
        self._ship = Ship()
        self._adirection = 'right'
        self._dline = GPath(linewidth=1,points=[0,DEFENSE_LINE, GAME_WIDTH,
        DEFENSE_LINE], linecolor='black')
        self.input = input
        self._fireRate = random.randrange(1,BOLT_RATE)
        self._alienSteps = 0
        self._lives = SHIP_LIVES
        self._alienSpeed = speed
        self._pewSound = Sound('pew1.wav')
        self._alienPew = Sound('pew2.wav')
        self._shipExplode = Sound('blast1.wav')
        self._alienDie = Sound('blast1.wav')
        self._muted = False
        self.draw(view)

    def fill(self):
        """
        Filling _alien attribute with alien objects.

        This method should make sure that _alien satisfies the given invariants.
        It repeatedly calls the Alien class and passes on the parameters row and col.
        """
        alienList = []
        rowList=[]
        row = 0
        col = 0
        while row < ALIEN_ROWS:
            while col < ALIENS_IN_ROW:
                x = ALIEN_H_SEP+((1+col)*ALIEN_H_SEP)+(col*ALIEN_WIDTH)
                y = GAME_HEIGHT-ALIEN_CEILING-(((row)*ALIEN_V_SEP)+
                (row*ALIEN_HEIGHT))
                if row == 0:
                    source = 'alien3.png'
                elif row == 1 or row == 2:
                    source = 'alien2.png'
                elif row > 2 and row <=5:
                    source = 'alien1.png'
                elif row > 5:
                    row = row-5

                if row <=5:
                    rowList.append(Alien(x,y,source))
                col+=1
            alienList.append(rowList)
            rowList=[]
            col=0
            row +=1

        return alienList

    # UPDATE METHOD TO MOVE THE SHIP, ALIENS, AND LASER BOLTS
    def update(self, dt):
        """
        Draws the game objects to the view.

        Every object being drawn is a GObject.

        """
        if self._time <= self._alienSpeed:
            self._time += dt
        elif self._time > self._alienSpeed:
            self.alienWalk()
        self.handleShip()
        self.alienFire()
        self.boltActions()
        self.defenseLine()
        self.mute()

    # HELPER METHODS FOR update()
    def handleShip(self):
        """
        Moves ship left and right, shoots bolts when proper commands are entered.
        """
        players=False
        for bolt in self._bolts:
            if bolt.isPlayers()==True:
                players = True
                break

        if self._ship != None:
            if self.input.is_key_down('left') or self.input.is_key_down('a'):
                x = self._ship.x - SHIP_MOVEMENT
                self._ship.x = max(x,SHIP_WIDTH/2)
            if self.input.is_key_down('right') or self.input.is_key_down('d'):
                x = self._ship.x + SHIP_MOVEMENT
                self._ship.x = min(x, (GAME_WIDTH-SHIP_WIDTH/2))

            if ((self.input.is_key_down('up') or
            self.input.is_key_down('spacebar') or self.input.is_key_down('w'))
            and players == False):
                self._bolts.append(Bolt(self._ship.x,self._ship.y, True))
                if self._muted == False:
                    self._pewSound.play()

    def alienWalk(self):
        """
        Moves ship left and right, shoots bolts when proper commands are entered.
        """
        maxRight = 0
        maxLeft = GAME_WIDTH
        self._alienSteps += 1
        for row in self._alien:
            for alien in row:
                if alien.x > maxRight:
                    maxRight= alien.x
                if alien.x < maxLeft:
                    maxLeft = alien.x
                if self._adirection=='right':
                    if maxRight <= (GAME_WIDTH-ALIEN_H_SEP-(.5*ALIEN_WIDTH)):
                        alien.x += ALIEN_H_WALK
                    elif maxRight > (GAME_WIDTH-ALIEN_H_SEP-(.5*ALIEN_WIDTH)):
                        alien.x += ALIEN_H_WALK
                        for alienfar in row:
                            alienfar.x -= (ALIEN_H_WALK)
                        self.alienDown()
                        self._adirection = 'left'
                elif self._adirection=='left':
                    if maxLeft >= ALIEN_H_SEP+(.5*ALIEN_WIDTH):
                        alien.x -= ALIEN_H_WALK
                    elif maxLeft < ALIEN_H_SEP+(.5*ALIEN_WIDTH):
                        for alienfar1 in row:
                            alienfar1.x += (.5*ALIEN_H_WALK)
                        alien.x += ALIEN_H_WALK
                        self.alienDown()
                        self._adirection = 'right'
        self._time = 0

    def alienDown(self):
        """
        Mutes or unmutes game using user input.
        """
        for row in self._alien:
            for alien1 in row:
                alien1.y -= ALIEN_V_WALK

    def mute(self):
        """
        Mutes or unmutes game using user input.
        """
        if self.input.is_key_down('m'):
            if self._muted == False:
                self._pewSound = None
                self._alienPew = None
                self._shipExplode = None
                self._alienDie = None
                self._muted = True
            elif self._muted == True:
                self._pewSound = Sound('pew1.wav')
                self._alienPew = Sound('pew2.wav')
                self._shipExplode = Sound('blast1.wav')
                self._alienDie = Sound('blast1.wav')
                self._muted = False

    def boltActions(self):
        """
        Assigns bolt objects their speed, deletes bolts that are off screen,
        detects collisions between a bolt and a ship or alien

        """
        for bolt in self._bolts:
            bolt.y += bolt.getVelocity()
            if bolt.y > GAME_HEIGHT or bolt.y < -BOLT_HEIGHT:
                self._bolts.remove(bolt)
            else:
                for alienRow in self._alien:
                    for alienObj in alienRow:
                        if alienObj.collides(bolt):
                            alienRow.remove(alienObj)
                            if self._bolts != []:
                                self._bolts.remove(bolt)
                            if self._muted == False:
                                self._alienDie.play()
            if self._ship != None and self._ship.collides(bolt):
                self._ship = None
                self._bolts=[]
                if self._muted == False:
                    self._shipExplode.play()

    def defenseLine(self):
        """
        Makes the player automatically lose if alien object reaches below
        defense line

        """
        for row in self._alien:
            for alien in row:
                if (alien.y-(.5*ALIEN_HEIGHT)) < DEFENSE_LINE:
                    self._lives = 0

    def alienFire(self):
        """
        Makes alien objects fire bolts downward towards the ship. Bolts are
        fired once per anywhere between 1 and BOLT_RATE alien steps. The alien
        that is firing is selected randomly from the bottommost aliens

        """
        if self._alienSteps == self._fireRate and self._alien != []:
            selectedAlien = self.alienSelect()
            self._bolts.append(Bolt(selectedAlien.x,selectedAlien.y, False))
            if self._muted == False:
                self._alienPew.play()
            self._alienSteps = 0
            self._fireRate = random.randrange(1,BOLT_RATE)

    def colSelect(self):
        """
        Organizes aliens into columns and selects one column from which to
        select an alien.

        """
        if self._alien==None or self._alien==[]:
            return None
        alienList = []
        alienList = copy.copy(self._alien)
        colList = []
        newAlienList = []

        rows = len(alienList)
        for row in range(0, rows):
            cols = len(alienList[row])
            for col in range(0, cols):
                colList.append(alienList[row][col])
            newAlienList.append(colList)
            colList = []
        return random.choice(newAlienList)

    def alienSelect(self):
        """
        Selects the bottom most alien of the selected column.
        """
        selectedColumn = self.colSelect()
        bottom = GAME_HEIGHT


        if selectedColumn is None or selectedColumn is [] or selectedColumn is [[]]:
            return None

        elif len(selectedColumn)==0:
            print("The code went here")
            print(self._alien)
            return random.choice(self._alien[0])
        else:
            try:
                bottomAlien = selectedColumn[-1]
                return bottomAlien
            except:
                selectedColumn = self.colSelect()
                return selectedColumn[-1]
            

    # DRAW METHOD TO DRAW THE SHIP, ALIENS, DEFENSIVE LINE AND BOLTS
    def draw(self, view):
        """
        Draws the game objects to the view.

        Every object being drawn is a GObject.

        """
        for row in self._alien:
            for alien in row:
                if alien != None:
                    alien.draw(view)
                elif alien == None:
                    alien.draw(view)

        if self._ship != None:
            self._ship.draw(view)
        self._dline.draw(view)
        for bolt in self._bolts:
            bolt.draw(view)

    # HELPER METHODS FOR COLLISION DETECTION
