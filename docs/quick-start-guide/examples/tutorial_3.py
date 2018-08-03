# Tutorial example 3:
#     - Set up our farm script environment
#     - Get a board instance
#     - Reboot the board

# Setup references
import sys
sys.path.append('/home/my_user/farm-core')

# In order to interact with the farm, we need to import our
# hardware configuration file
from farmconfigs.farm_uk import farm

# Get a handle to the simple board class for the board named 'bbb'.
my_board = farm.get_board('bbb')

# In order to gain exclusive use of a board, we must issue a use request.
# This will return an instance of the FarmBoard class, with which we can
# interact with the board.
my_farmboard = b.use()

# Turn on the board
my_farmboard.on()

# Turn off the board
my_farmboard.off()
