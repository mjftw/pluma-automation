import time

from farmcore import farm



def main():
    paladin = farm.Board(
        name='paladin',
        power=farm.PowerRelay('3-3.3'),
        hub=farm.Hub('3-3'),
        sdmux=None,
        logfile="paladin.log"
        # logfile=None
    )

    paladin.power.off()
    paladin.power.on()
    paladin.console.wait_for_quiet(timeout=20, quiet=5)


if __name__ == '__main__':
    main()