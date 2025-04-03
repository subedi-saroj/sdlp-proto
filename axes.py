from zaber_motion import Units, wait_all
from zaber_motion.ascii import Axis, Connection, Device, Lockstep

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

    def __init__(self, COMPort:str="COM7"):

        self.COMPort = COMPort
        self.connectionStatus = True # connection status
        try:
            connection = Connection.open_serial_port(self.COMPort)
            connection.enable_alerts()

            device_list = connection.detect_devices()
            print("Found {} devices".format(len(device_list)))
        
        except Exception as e:
            print(e)
            print(f"Could not connect to {self.COMPort}")
            self.connectionStatus = False
            return

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
        
        # home all devices if they are connected successfully
        if self.connectionStatus:
            c4 = self.ZAxis.home_async()
            c1 = self.MAxis.home_async()
            c2 = self.YAxis.home_async()
            c3 = self.XAxis.home_async()
            wait_all(c4) # for safety reasons to avoid collision between resin container and build platform
            wait_all(c2, c3, c1)
            print("All axes are connected")
        else: print("WARNING: Some axes are not connected")

        return

    def _boundary_check(self, confirm_code):
        """
        Perform boundary check for all axes.

        Args:
            confirm_code: Confirmation code for boundary check.

        Returns:
            None

        This is primarily for testing purposes and should not be used during printing operations.
        Will move all axes to their maximum positions and then home them back to zero. If anything is
        in the way, it will likely cause damage to the machine.
        """

        # c1 = self.MAxis.move_max_async()
        # c2 = self.YAxis.move_max_async()
        # c3 = self.XAxis.move_max_async()
        # c4 = self.ZAxis.move_max_async()
        
        # wait_all(c1, c2, c3, c4)

        # c1 = self.MAxis.home_async()
        # c2 = self.YAxis.home_async()
        # c3 = self.XAxis.home_async()
        # c4 = self.ZAxis.home_async()

        # wait_all(c1, c2, c3, c4)
        return

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
            positions[axis] = self.getAxisPosition(axis)
        return positions


    def getAxisPosition(self, axis_name:str) -> float:
        """
        Get the current position of a specific axis.

        Args:
            axis_name: The name of the axis to get the position of.

        Returns:
            float: The current position of the axis in millimeters.

        Raises:
            AttributeError: If the axis does not exist.
        """
        axis = getattr(self, f"{axis_name}Axis")

        return axis.get_position(Units.LENGTH_MILLIMETRES)
    
    
    