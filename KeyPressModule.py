import pygame  # The libraries that need to install to run this program

def init():

    pygame.init()
    pygame.display.set_mode((200, 200))
    pygame.display.set_caption('Emergency Button')


def getKey(keyname):

    ans = False

    for _ in pygame.event.get():
        pass

    keyinput = pygame.key.get_pressed()

    mykey = getattr(pygame, 'K_{}'.format(keyname))

    # print('K_{}'.format(keyname))

    if keyinput[mykey]:

        ans = True

    pygame.display.update()

    return ans


def main():

    if getKey("LEFT"):

        print("Left key pressed")

    if getKey("RIGHT"):

        print("Right key Pressed")


if __name__ == '__main__':

    init()

    while True:

        main()
