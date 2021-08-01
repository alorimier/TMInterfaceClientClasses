from clients.triggers.shapes.cube import TriggerCube

# Delay before the server automatically close the connexion if no answer from the client.
# Consider that you won't have access to the game if the server is waiting for an answer
CLIENT_TIMEOUT = 2000

# Starting bloc counter delay
TIMER_DELAY = 2610

trigger_shape = TriggerCube(x1=930.0, y1=5.0, z1=324.0, x2=931.0, y2=20.0, z2=347.0)
