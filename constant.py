# command constants
DICE_NUMBER_LIST = [4,6,8,10,12,20,100]
DICE_COMMAND_LIST = ['dice']
CRAPS_COMMAND_LIST = ['craps']
CEELO_COMMAND_LIST = ['cee-lo','ceelo']
COIN_COMMAND_LIST = ['coin','coinflip','flip']
ALL_COMMAND_LIST = ['diceall','alldice']
HELP_COMMAND_LIST = ['dicehelp']

# useful numbers
REG_DICE_MAX = 6
COIN_MAX = 2
NUM_OF_REG_DICE_VARIATIONS = 2
NUM_ROLLS_CRAPS = 2
NUM_ROLLS_CEELO = 3
MAX_NUMBER_ROLLS = 21

# folder and picture constants
BLACK_DICE_FOLDER_PATH = "pictures/black_dice/"
WHITE_DICE_FOLDER_PATH = "pictures/white_dice/"
COIN_FOLDER_PATH = 'pictures/coin/'
SAD_DICE_KING_FILE_PATH = 'pictures/dice_king/sad_dice_king.png'
TEMP_FILE_PATH = 'pictures/temp/combined.png'

# printed strings
HELP_ME_STRING = "I'm King Dice, proprietor of this server. Your one and only stop for all dice-related needs. Here is how to use me, and good luck friend!\n\n!dice – roll a regular 6-sided die \n!craps – rolls 2 6-sided die\n!ceelo – rolls 3 6-sided die\n!20 – rolls a d20 die, also works for 12/10/8/6/4\n!100 – rolls 2d10, one for the first digit and one for the second (000 is 100)\n!coin or !coinflip - flips a coin\nAdding a number after a command will perform that command X amount of times (ex: !20 4). Max 20 times.\n\nAnd don’t even think about doing a number after the exclamation mark that isn’t listed above this.. "