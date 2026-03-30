#!/usr/bin/env python3
from enum import IntEnum
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Joy
from synapse_msgs.msg import Input


class Channel(IntEnum):
    RIGHT_STICK_RIGHT=0
    RIGHT_STICK_UP=1
    LEFT_STICK_UP=2
    LEFT_STICK_RIGHT=3
    SWA_DOWN=4
    SWB_DOWN=5
    SWC_DOWN=6
    SWD_DOWN=7
    VRA_CW=8
    VRB_CCW=9

class Axes(IntEnum):
    LEFT_STICK_LEFT=0
    LEFT_STICK_UP=1
    RIGHT_STICK_LEFT=2
    RIGHT_STICK_UP=3
    LEFT_TRIGGER_OUT=4
    RIGHT_TRIGGER_OUT=5

class Button(IntEnum):
    X=0
    CIRCLE=1
    SQUARE=2
    TRIANGLE=3
    SHARE=4
    CENTER=5
    OPTIONS=6
    LEFT_STICK=7
    RIGHT_STICK=8
    LEFT_BUMPER=9
    RIGHT_BUMPER=10
    DPAD_UP=11
    DPAD_DOWN=12
    DPAD_LEFT=13
    DPAD_RIGHT=14
    TOUCH=15

SwitchPosUp = -1
SwitchPosDown = 1
SwitchPosMiddle = 0

button_map = {
    Button.OPTIONS: [(Channel.SWA_DOWN, SwitchPosDown)], # arm
    Button.SHARE: [(Channel.SWA_DOWN, SwitchPosUp)], # disarm
    Button.LEFT_BUMPER: [(Channel.SWD_DOWN, SwitchPosUp)], # topic source input
    Button.RIGHT_BUMPER: [(Channel.SWD_DOWN, SwitchPosDown)], # topic source ethernet
    Button.X: [(Channel.SWB_DOWN, SwitchPosUp), (Channel.SWC_DOWN, SwitchPosUp)], # attitude
    Button.CIRCLE: [(Channel.SWB_DOWN, SwitchPosUp), (Channel.SWC_DOWN, SwitchPosMiddle)], # velocity
    Button.SQUARE: [(Channel.SWB_DOWN, SwitchPosUp), (Channel.SWC_DOWN, SwitchPosDown)], # bezier
    Button.DPAD_RIGHT: [(Channel.SWB_DOWN, SwitchPosMiddle), (Channel.SWC_DOWN, SwitchPosUp)], # attitude rate
    Button.TRIANGLE: [(Channel.SWB_DOWN, SwitchPosDown), (Channel.SWC_DOWN, SwitchPosDown)], # calibration
}

axes_map= {
    Axes.RIGHT_STICK_LEFT: (Channel.RIGHT_STICK_RIGHT, -1),
    Axes.RIGHT_STICK_UP: (Channel.RIGHT_STICK_UP, 1),
    Axes.LEFT_STICK_UP: (Channel.LEFT_STICK_UP, 1),
    Axes.LEFT_STICK_LEFT: (Channel.LEFT_STICK_RIGHT, -1)
}

class JoyToInput(Node):

    def __init__(self):
        super().__init__('joy_to_input')
        self.subscription = self.create_subscription(
            Joy,
            '/cerebri/in/joy',
            self.listener_callback,
            10)
        self.publisher = self.create_publisher(
            Input,
            '/cerebri/in/input', 10)

        self.subscription  # prevent unused variable warning
        self.msg = Input() 
        self.set_default()

    def set_default(self):
        self.msg.channel[Channel.RIGHT_STICK_UP] = 0;
        self.msg.channel[Channel.RIGHT_STICK_RIGHT] = 0;
        self.msg.channel[Channel.LEFT_STICK_UP] = 0;
        self.msg.channel[Channel.LEFT_STICK_RIGHT] = 0;
        self.msg.channel[Channel.SWA_DOWN] = SwitchPosUp;
        self.msg.channel[Channel.SWB_DOWN] = SwitchPosUp;
        self.msg.channel[Channel.SWC_DOWN] = SwitchPosUp;
        self.msg.channel[Channel.SWD_DOWN] = SwitchPosUp;

    def listener_callback(self, msg_joy):

        for i in range(len(msg_joy.buttons)):
            if msg_joy.buttons[i] < 0.5:
                continue
            try:
                b = Button(i)
            except ValueError:
                continue
            print('pressed', b)
            ch_list = button_map[b]
            for ch, val in  ch_list:
                print('channel', ch, 'val', val)
                self.msg.channel[int(ch)] = val
                
        for i in range(len(msg_joy.axes)):
            try:
                ax = Axes(i)
            except ValueError:
                continue
            if ax in axes_map.keys():
                ch, scale = axes_map[ax]
                self.msg.channel[int(ch)] = scale*msg_joy.axes[i]

        self.publisher.publish(self.msg)


def main(args=None):
    rclpy.init(args=args)

    node = JoyToInput()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt as e:
        pass




if __name__ == '__main__':
    main()
