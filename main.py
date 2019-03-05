from engine import Engine
import random as rn

if __name__ == '__main__':
    # Manual seeding so that bug are reproducible
    # TODO: random seed then
    rn.seed(42)

    engine = Engine()
    engine.init_display()

    while engine.game_state is not 'exit':
        engine.update()
        engine.render()

    engine.exit()