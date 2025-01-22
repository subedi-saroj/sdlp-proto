import asyncio
from zaber_motion import Units
from zaber_motion import Measurement
from zaber_motion.ascii import Connection
from zaber_motion.ascii import LockstepAxes

with Connection.open_serial_port("COM3") as connection:
    connection.enable_alerts()

    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device = device_list[0]

    y = device.get_lockstep(1) # lockstep axes 1 and 2 -> y

    if not y.is_enabled():
        y.enable(1, 2)

    x = device.get_axis(3) # axis 3 -> x

    # home the axes
    def home_axes():
        x_coroutine = x.move_absolute_async(0)
        y_coroutine = y.move_absolute_async(0)

        move_coroutine = asyncio.gather(x_coroutine, y_coroutine)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(move_coroutine)
        
    home_axes()

    # # move the axes in a scrolling fashion
    # x_step_spacing = 30 # mm
    # units = Units.LENGTH_MILLIMETRES

    # for i in range(5):
    #     y.move_absolute(0)
    #     x.move_relative(x_step_spacing, units)
    #     y.move_absolute(300, units)
    #     x.move_relative(x_step_spacing, units)

    # home_axes()
    velocity = 11
    length = 200 # at inum size 20000
    y.move_absolute(length, Units.LENGTH_MILLIMETRES, velocity=velocity, velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
    y.move_absolute(0, Units.LENGTH_MILLIMETRES, velocity=velocity, velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)
