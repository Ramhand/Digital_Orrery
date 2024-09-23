from api_requests import position_recall
import datetime as dt
import math

class Orrery:
    """
    A class that represents an orrery (mechanical model of the solar system) 
    for tracking the positions of planets.
    """

    def __init__(self):
        """
        Initializes the Orrery object by recalling the position data and setting up a data frame for tracking.
        """
        global df, phase
        if 'df' not in globals():
            # Retrieve planetary position data from the API
            df, phase = position_recall()
        self.df = df

    def location_return(self):
        """
        Calculates the position of planets based on the current time and their rise and set times.
        
        Returns:
            dict: A dictionary with planet names as keys and their progress in the sky as values.
        """
        loc = {}
        for k in self.df.columns:
            rs = []
            # Convert the rise/set time from string to datetime object
            for v in self.df.loc[3, k]:
                rs.append(dt.datetime.strptime(v, '%H:%M').time())
            # Check if the current time is within the planet's visible window
            if rs[0] < dt.datetime.now().time() < rs[1]:
                progress = self.dt_calculations(rs)
            else:
                progress = None
            loc[k] = progress
        return loc

    def dt_calculations(self, rs):
        """
        Helper function to calculate the progress of a planet in the sky.
        
        Args:
            rs (list): List of rise and set times for the planet.
        
        Returns:
            float: Progress of the planet in the sky as a fraction.
        """
        rs1 = dt.datetime.combine(dt.date.min, rs[0])
        rs2 = dt.datetime.combine(dt.date.min, rs[1])
        span = rs2 - rs1
        span = span.seconds
        now = dt.datetime.combine(dt.date.min, dt.datetime.now().time())
        progress = now - rs1
        # Calculate the fraction of time the planet has been in the sky
        progress = (progress.seconds / span)
        return progress

    def center_rotate(self, point, origin, angle):
        """
        Rotates a point around a center point (origin) by a given angle.
        
        Args:
            point (tuple): The (x, y) coordinates of the point to rotate.
            origin (tuple): The (x, y) coordinates of the center point.
            angle (float): The angle of rotation in degrees.
        
        Returns:
            list: The new (x, y) coordinates of the rotated point.
        """
        px, py = point
        ox, oy = origin
        rad = math.radians(-angle)
        cos = math.cos(rad)
        sin = math.sin(rad)
        adj_x, adj_y = px - ox, py - oy
        # Apply rotation matrix
        new_point = [(adj_x * cos) - (adj_y * sin) + ox, (adj_x * sin) + (adj_y * cos) + oy]
        return new_point
