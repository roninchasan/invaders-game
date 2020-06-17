"""
Primary module for Alien Invaders

This module contains the main controller class for the Alien Invaders application. There
is no need for any additional classes in this module.  If you need more classes, 99% of
the time they belong in either the wave module or the models module. If you are unsure
about where a new class should go, post a question on Piazza.

Ronin Chasan (rcc263), Jacob Wise (jmw555)
December 4, 2018
"""
from consts import *
from game2d import *
from wave import *

# PRIMARY RULE: Invaders can only access attributes in wave.py via getters/setters
# Invaders is NOT allowed to access anything in models.py

class Invaders(GameApp):
    """
    The primary controller class for the Alien Invaders application

    This class extends GameApp and implements the various methods necessary for processing
    the player .aliens and starting/running a game.

        Method start begins the application.

        Method update either changes the state or updates the Play object

        Method draw displays the Play object and any other elements on screen

    Because of some of the weird ways that Kivy works, you SHOULD NOT create an
    initializer __init__ for this class.  Any initialization should be done in
    the start method instead.  This is only for this class.  All other classes
    behave normally.

    Most of the work handling the game is actually provided in the class Wave.
    Wave should be modeled after subcontrollers.py from lecture, and will have
    its own update and draw method.

    The primary purpose of this class is to manage the game state: which is when the
    game started, paused, completed, etc. It keeps track of that in an attribute
    called _state.

    INSTANCE ATTRIBUTES:
        view:   the game view, used in drawing (see examples from class)
                [instance of GView; it is inherited from GameApp]
        input:  the user input, used to control the ship and change state
                [instance of GInput; it is inherited from GameApp]
        _state: the current state of the game represented as a value from consts.py
                [one of STATE_INACTIVE, STATE_NEWWAVE, STATE_ACTIVE, STATE_PAUSED, STATE_CONTINUE, STATE_COMPLETE]
        _wave:  the subcontroller for a single wave, which manages the ships and aliens
                [Wave, or None if there is no wave currently active]
        _text:  the currently active message
                [GLabel, or None if there is no message to display]

    STATE SPECIFIC INVARIANTS:
        Attribute _wave is only None if _state is STATE_INACTIVE.
        Attribute _text is only None if _state is STATE_ACTIVE.

    For a complete description of how the states work, see the specification for the
    method update.

    You may have more attributes if you wish (you might want an attribute to store
    any score across multiple waves). If you add new attributes, they need to be
    documented here.

    LIST MORE ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY

        keydown:   is of bool type, is True if 'x' key is pressed, is False otherwise
        _speed:  the speed of the next alien wave
                [float >= ALIEN_SPEED]
        _timeCount:  the speed of the next alien wave
                [float >= 0, <SCREEN_TIME]

    """

    # DO NOT MAKE A NEW INITIALIZER!

    # THREE MAIN GAMEAPP METHODS
    def start(self):
        """
        Initializes the application.

        This method is distinct from the built-in initializer __init__ (which you
        should not override or change). This method is called once the game is running.
        You should use it to initialize any game specific attributes.

        This method should make sure that all of the attributes satisfy the given
        invariants. When done, it sets the _state to STATE_INACTIVE and create a message
        (in attribute _text) saying that the user should press to play a game.
        """
        # IMPLEMENT ME
        self._state = STATE_INACTIVE
        self._keyCount = 0
        self._text = GLabel(text="Press 'X' to play", font_name = 'arcade.ttf',
        font_size = 50, x=400, y=350)
        self.speed = ALIEN_SPEED
        self._timeCount = 0


    def update(self,dt):
        """
        Animates a single frame in the game.

        It is the method that does most of the work. It is NOT in charge of playing the
        game.  That is the purpose of the class Wave. The primary purpose of this
        game is to determine the current state, and -- if the game is active -- pass
        the input to the Wave object _wave to play the game.

        As part of the assignment, you are allowed to add your own states. However, at
        a minimum you must support the following states: STATE_INACTIVE, STATE_NEWWAVE,
        STATE_ACTIVE, STATE_PAUSED, and STATE_COMPLETE.  Each one of these
        does its own thing and might even needs its own helper.  We describe these below.

        STATE_INACTIVE: This is the state when the application first opens.  It is a
        paused state, waiting for the player to start the game.  It displays a simple
        message on the screen. The application remains in this state so long as the
        player never presses a key.  In addition, this is the state the application
        returns to when the game is over (all lives are lost or all aliens are dead).

        STATE_NEWWAVE: This is the state creates a new wave and shows it on the screen.
        The application switches to this state if the state was STATE_INACTIVE in the
        previous frame, and the player pressed a key. This state only lasts one animation
        frame before switching to STATE_ACTIVE.

        STATE_ACTIVE: This is a session of normal gameplay.  The player can move the
        ship and fire laser bolts.  All of this should be handled inside of class Wave
        (NOT in this class).  Hence the Wave class should have an update() method, just
        like the subcontroller example in lecture.

        STATE_PAUSED: Like STATE_INACTIVE, this is a paused state. However, the game is
        still visible on the screen.

        STATE_COMPLETE: The wave is over, and is either won or lost.

        You are allowed to add more states if you wish. Should you do so, you should
        describe them here.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)
        """
        # IMPLEMENT ME
        if self.input.is_key_down('x') and self._keyCount<1:
            self.keydown = True
            self._keyCount +=1
            self._state = STATE_NEWWAVE
            self.draw()
        elif not self.input.is_key_down('x'):
            self.keydown = False

        if self._state == STATE_NEWWAVE:
            self._wave = Wave(self.view, self.input, self.speed)
            self._state = STATE_ACTIVE
        elif self._state == STATE_ACTIVE:
            self.toActive(dt)
        elif self._state == STATE_PAUSED:
            self.toPause()
        elif self._state == STATE_COMPLETE:
            self.toComplete(dt)


    def draw(self):
        """
        Draws the game objects to the view.

        Every single thing you want to draw in this game is a GObject.  To draw a GObject
        g, simply use the method g.draw(self.view).  It is that easy!

        Many of the GObjects (such as the ships, aliens, and bolts) are attributes in
        Wave. In order to draw them, you either need to add getters for these attributes
        or you need to add a draw method to class Wave.  We suggest the latter.  See
        the example subcontroller.py from class.
        """
        if self.keydown == True:
            self._text = GLabel(text="")

        self._text.draw(self.view)


    # HELPER METHODS FOR THE STATES GO HERE
    def toActive(self, dt):
        """
        Performs all actions to change the state of the game to STATE_ACTIVE

        """
        self.keydown = True
        self._wave.draw(self.view)
        k=0
        for x in range(0, len(self._wave._alien)-1):
            if self._wave._alien[x] == []:
                k+=1
        if k == len(self._wave._alien)-1:
            self._state = STATE_COMPLETE
        else:
            Wave.update(self._wave, dt)
        if self._wave._ship == None:
            self._wave._lives -=1
            self._wave._ship = Ship()
            self._state = STATE_PAUSED
        if self._wave._lives == 0:
            self._state = STATE_COMPLETE

        if self.input.is_key_down('p'):
            self._state = STATE_PAUSED


    def toComplete(self, dt):
        """
        Performs all actions to change the state of the game to STATE_COMPLETE

        """
        if self._wave._lives == 0:
            self._text = GLabel(text="Game over!", font_name = 'arcade.ttf',
            font_size = 60, x=400, y=350)
        else:
            if self._timeCount < SCREEN_TIME:
                self._text=GLabel(text="Wave complete! Prepare for next wave...", font_name = 'arcade.ttf',font_size = 35, x=400, y=350)
                self._timeCount += dt
            else:
                self.draw()
                self.speed = (self.speed)/(ALIEN_SPEED_UP)
                self._state = STATE_NEWWAVE
                self._timeCount = 0


    def toPause(self):
        """
        Performs all actions to change the state of the game to STATE_PAUSED

        """
        self._text = GLabel(text= str(self._wave._lives) + " lives remaining. Press 'R' to resume", font_name = 'arcade.ttf',font_size = 40, x=400, y=350)
        self.keydown = False
        if self.input.is_key_down('r'):
            self.keydown = True
            self._state = STATE_ACTIVE
        self.draw()
