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
    LEFT_TRIGGER_OUT=2
    RIGHT_STICK_LEFT=3
    RIGHT_STICK_UP=4
    RIGHT_TRIGGER_OUT=5
    DPAD_LEFT=6
    DPAD_UP=7

class Button(IntEnum):
    A=0
    B=1
    X=2
    Y=3
    LEFT_BUMPER=4
    RIGHT_BUMPER=5
    BACK=6
    START=7
    CENTER=8
    LEFT_STICK=9
    RIGHT_STICK=10


SwitchPosUp = -1
SwitchPosDown = 1
SwitchPosMiddle = 0

button_map = {
    Button.START: [(Channel.SWA_DOWN, SwitchPosDown)], # arm
    Button.BACK: [(Channel.SWA_DOWN, SwitchPosUp)], # disarm
    Button.LEFT_BUMPER: [(Channel.SWD_DOWN, SwitchPosUp)], # topic source input
    Button.RIGHT_BUMPER: [(Channel.SWD_DOWN, SwitchPosDown)], # topic source ethernet
    Button.A: [(Channel.SWB_DOWN, SwitchPosUp), (Channel.SWC_DOWN, SwitchPosUp)], # attitude
    Button.B: [(Channel.SWB_DOWN, SwitchPosUp), (Channel.SWC_DOWN, SwitchPosMiddle)], # velocity
    Button.X: [(Channel.SWB_DOWN, SwitchPosUp), (Channel.SWC_DOWN, SwitchPosDown)], # bezier
    Button.CENTER: [(Channel.SWB_DOWN, SwitchPosMiddle), (Channel.SWC_DOWN, SwitchPosUp)], # attitude rate
    Button.Y: [(Channel.SWB_DOWN, SwitchPosDown), (Channel.SWC_DOWN, SwitchPosDown)], # calibration
}

axes_map= {
    Axes.RIGHT_STICK_LEFT: (Channel.RIGHT_STICK_RIGHT, -1),
    Axes.RIGHT_STICK_UP: (Channel.RIGHT_STICK_UP, 1),
    Axes.LEFT_STICK_UP: (Channel.LEFT_STICK_UP, 1),
    Axes.LEFT_STICK_LEFT: (Channel.LEFT_STICK_RIGHT, -1),
    Axes.DPAD_LEFT: (Channel.VRA_CW, -1),
    Axes.DPAD_UP: (Channel.VRB_CCW, -1)

}

class JoyToInput(Node):

    def __init__(self):
        super().__init__('joy_to_input')
        self.subscription = self.create_subscription(
            Joy,
            '/joy',
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
        self.msg.channel[Channel.VRA_CW] = 0;
        self.msg.channel[Channel.VRB_CCW] = 0;

    def listener_callback(self, msg_joy):

        for i in range(len(msg_joy.buttons)):
            if msg_joy.buttons[i] < 0.5:
                continue
            try:
                b = Button(i)
            except KeyError as e:
                print(e)
                continue
            print('pressed', b)
            ch_list = button_map[b]
            for ch, val in  ch_list:
                print('channel', ch, 'val', val)
                self.msg.channel[int(ch)] = val
                
        for i in range(len(msg_joy.axes)):
            try:
                ax = Axes(i)
            except KeyError as e:
                print(e)
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
