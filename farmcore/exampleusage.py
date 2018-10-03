from hwconfig import boards
import farm
import board
import interact
import hostconsole

# Not much in farm class yet, as it's mostly a high level container
# but eventually it could contain things like an Automate class,
# for sending emails etc.
# Anyway, this is how you'd make one
f = farm.Farm(boards)

# Get board by name (could also do: b = boards[0], but this is more readable)
b = board.get_board('bbb')

# Print hierachy of board
print(b.show_hier())

# Create the instance of the board's console.
# This will likely change when detecting devices is a little more sophisticated
b.init_console()
# Send newline and check we get data back
if b.act.check_alive():
    # Send command, don't care about result
    b.send('echo "Hello Farm" > ~/farmtest.txt')
    # Send comand, print result
    print(b.send('ls ~', recieve=True))
    # Send command, wait for matching pattern recieved, print all up to pattern match
    print(b.send('ps', recieve=True, match='root@'))

# -------------------
# Use interact directly

# Create empty interact
i = interact.Interact()

# Create a Console instance and give it to interact
i.switch_console(HostConsole('bash --login'))

# Send command to console running on the farm, print result
print(i.send('ls ~', recieve=True))

#-------------------
# Switch sdmux to board

b.sdmux.sdboard()