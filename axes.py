from zaber_motion import Units, wait_all
from zaber_motion.ascii import Axis, Connection, Device, Lockstep
from typing import List
import asyncio

class ZaberAxes():
    """
    Class representing the Zaber Axes.

    This class provides methods to connect to Zaber devices, home the axes, get positions, and perform boundary checks.

    Attributes:
        MAxis: Zaber device for the meter long axis.
        ZAxis: Zaber device for the z-axis.
        XAxis: Zaber device for the x-axis.
        YAxis: Zaber device for the y-axis.
    """

    def __init__(self, COMPort:str):

        self.COMPort = COMPort
        self.connectionStatus = True

        device_list = self._connect()

        try: 
            self.MAxis = device_list[0].get_axis(1)
        except Exception as e:
            print("Could not get meter long axis"); self.connectionStatus = False
            self.MAxis = None
        
        try:
            self.ZAxis = device_list[1].get_axis(1)
        except Exception as e:
            print("Could not get z axis"); self.connectionStatus = False
            self.ZAxis = None

        try:
            self.XAxis = device_list[2].get_axis(3)
        except Exception as e:
            print("Could not get x axis"); self.connectionStatus = False
            self.XAxis = None
        
        try:
            self.YAxis = device_list[2].get_lockstep(1)
            if not self.YAxis.is_enabled():
                self.YAxis.enable(1, 2)
        except Exception as e:
            print("Could not get y axis"); self.connectionStatus = False
            self.YAxis = None
        
        if self.connectionStatus:
            print("Connected to all devices")
            
            self.axes:List[Axis] = [self.XAxis, self.YAxis, self.ZAxis] # excludes M Axis

        else: print("WARNING: Some axes are not connected")

        return
    
    def _connect(self) -> list[Device]:
        
        try:
            connection = Connection.open_serial_port(self.COMPort)
            connection.enable_alerts()

            device_list = connection.detect_devices()
            print("Found {} devices".format(len(device_list)))
        
        except Exception as e:
            print(e)
            print(f"Could not connect to {self.COMPort}")
            self.connectionStatus = False
        
        return device_list

    def getPositions(self):
        """
        Get the current positions of all axes.

        Returns:
            dict: A dictionary containing the current positions of the axes.
                  The keys represent the axis names ('X', 'Y', 'Z', 'M') and the values
                  represent the corresponding positions in millimeters.
        """
        positions = {"X": 0, "Y": 0, "Z": 0, "M": 0}

        for axis in positions.keys():
            positions[axis] = self.get_position(axis)
        return positions


    def get_position(self, axis_name:str) -> float:
        """
        Get the current position of a specific axis.

        Args:
            axis_name: The name of the axis to get the position of.

        Returns:
            float: The current position of the axis in millimeters.

        Raises:
            AttributeError: If the axis does not exist.
        """
        axis:Axis = getattr(self, f"{axis_name}Axis")

        return axis.get_position(Units.LENGTH_MILLIMETRES)

    def home(self):
        """
        Home all axes.
            (CURRENTLY DISABLED FOR METER LONG AXIS)

        Returns:
            None
        """

        wait_all(
            self.YAxis.home_async(),
            self.XAxis.home_async(),
            self.ZAxis.home_async()
        )

        return
    
    def scroll(self, distance:int, velocity:int):
        '''
        Scroll the axes by a given distance at a given velocity.
        Units are in mm, or mm/s.
        '''
        self.YAxis.move_relative(distance, Units.LENGTH_MILLIMETRES, True,
                                velocity, Units.VELOCITY_MILLIMETRES_PER_SECOND)

        return
    
    def increment_layer(self, layer_height:int):
        ''''
        Increment the Z axis by a given layer height.
        Units are in mm.
        '''

        # I have set this at a slow speed to compensate for material suction from resin path into print area
        self.ZAxis.move_relative(-layer_height, Units.LENGTH_MILLIMETRES, True, 0.5, Units.VELOCITY_MILLIMETRES_PER_SECOND)
        return
    
    def increment_lateral(self, distance:int):
        '''
        Increment the X axis by a given distance.
        Units are in mm.
        '''
        self.XAxis.move_relative(distance, Units.LENGTH_MILLIMETRES)
        return
    
    def to_point(self, x:int, y:int, z:int):
        '''
        Move the axes to a given point asynchronously.
        Units are in mm.
        '''
        wait_all(
            self.XAxis.move_absolute_async(x, Units.LENGTH_MILLIMETRES),
            self.YAxis.move_absolute_async(y, Units.LENGTH_MILLIMETRES),
            self.ZAxis.move_absolute_async(z, Units.LENGTH_MILLIMETRES)
        )

        return
    
    def park(self):
        '''
        Park all axes in preperation for powering off.
        When powered back on, the axes will not need to be homed.
        '''

        wait_all(
            *[axis.park_async() for axis in self.axes]
        )
        
        return
    
    

    

    