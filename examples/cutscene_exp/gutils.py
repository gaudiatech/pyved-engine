import pygame
# from ..components.component_input import InputComponent
# from ..managers.manager_input import controller, keys


# functions to sort by x, y, or z position
def sortByX(e):
    pos = e.getComponent('position')
    if pos is None:
        return 1
    return pos.x


def sortByY(e):
    pos = e.getComponent('position')
    if pos is None:    
        return 1
    return pos.y


def sortByZ(e):
    #return e.z
    pos = e.getComponent('position')
    if pos is None:    
        return 1
    return pos.z


def drawRect(s,x,y,w,h,c,a=255):
    # only add transparency if needed
    if a < 255:
        overlay = pygame.Surface((w,h), pygame.SRCALPHA)
        overlay.set_alpha(a)
    else:
        overlay = pygame.Surface((w,h))
    overlay.fill(c)
    s.blit(overlay, (x,y))

def drawImage(s, image, x, y, xAnchor='left', yAnchor='top', scale=1):
    
    imageRect = image.get_rect()
    ow = imageRect.w
    oh = imageRect.h

    if xAnchor == 'center':
        x -= imageRect.w*scale/2
    elif xAnchor == 'right':
        x -= imageRect.w*scale

    if yAnchor == 'middle':
        y -= imageRect.h*scale/2
    elif yAnchor == 'bottom':
        y -= imageRect.h*scale
    
    s.blit(pygame.transform.scale(image, (ow*scale,oh*scale)), (x,y))

def createControllerInputComponent(controllerNumber, entityControllerFunction):

    controllerInputComponent = InputComponent(
        # left dpad
        up          = controller[controllerNumber].dpad_up,
        down        = controller[controllerNumber].dpad_down,
        left        = controller[controllerNumber].dpad_left,
        right       = controller[controllerNumber].dpad_right,
        # 4 main buttons
        b1          = controller[controllerNumber].a,
        b2          = controller[controllerNumber].b,
        b3          = controller[controllerNumber].x,
        b4          = controller[controllerNumber].y,
        # shoulder and trigger buttons
        b5          = controller[controllerNumber].leftShoulder,
        b6          = controller[controllerNumber].rightShoulder,
        b7          = controller[controllerNumber].leftTrigger,
        b8          = controller[controllerNumber].rightTrigger,
        # left thumb
        b9          = controller[controllerNumber].leftDir_up,
        b10         = controller[controllerNumber].leftDir_down,
        b11         = controller[controllerNumber].leftDir_left,
        b12         = controller[controllerNumber].leftDir_right,
        # right thumb
        b13         = controller[controllerNumber].rightDir_up,
        b14         = controller[controllerNumber].rightDir_down,
        b15         = controller[controllerNumber].rightDir_left,
        b16         = controller[controllerNumber].rightDir_right,
        # start and select
        b17         = controller[controllerNumber].start,
        b18         = controller[controllerNumber].select,
        # entity controller
        inputContext   = entityControllerFunction
    )

    return controllerInputComponent

def createKeyboardInputComponent(entityControllerFunction):

    keyboardInputComponent = InputComponent(
        up          = keys.w,
        down        = keys.s,
        left        = keys.a,
        right       = keys.d,
        b1          = keys.k,
        b2          = keys.l,
        b3          = keys.j,
        b4          = keys.i,
        b5          = keys.u,
        b6          = keys.o,
        b7          = keys.q,
        b8          = keys.e,
        b9          = keys.t,
        b10         = keys.g,
        b11         = keys.f,
        b12         = keys.h,
        b13         = keys.up,
        b14         = keys.down,
        b15         = keys.left,
        b16         = keys.right,
        b17         = keys.enter,
        b18         = keys.esc,
        inputContext   = entityControllerFunction
    )

    return keyboardInputComponent

