"""Module responsible for the startup of the system. The only one that can be called by the end-users."""
from src.startup.thread_starter import Starter


if __name__ == '__main__':
    starter = Starter()
    starter.start()
