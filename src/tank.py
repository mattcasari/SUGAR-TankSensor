import math
import asyncio
from time import sleep_ms
from src.lib.tr_evo_mini import EvoMini


class Tank:
    RADIUS = 38.5  # in
    CONE_MAX_HEIGHT = 16  # in
    CYLINDER_MAX_HEIGHT = 48  # in

    def __init__(self, get_distance: function, mounted_distance: float):
        """_summary_

        Args:
            get_distance (function): Function that reads the distance sensor distance
            mounted_distance (float): Distance sensor is mounted above top of tank (in)
        """
        print("Init TANK")
        print(f"Mounted distance passed: {mounted_distance} in")
        self.get_distance = get_distance
        self._mounted_distance = mounted_distance
        self.TOTAL_VOLUME_GALLONS = self._calculate_combined_volume(
            self.CONE_MAX_HEIGHT + self.CYLINDER_MAX_HEIGHT
        )
        self.TOTAL_MAX_HEIGHT = self.CONE_MAX_HEIGHT + self.CYLINDER_MAX_HEIGHT
        print(f"Max volume calculated: {self.TOTAL_VOLUME_GALLONS}")
        print(f"Total Max Height = {self.TOTAL_MAX_HEIGHT} in")
        print(f"Mounted height = {self._mounted_distance}")

    def get_volume_average(self, num_reads) -> float:
        reads = [self.get_volume() for i in range(num_reads)]
        print(f"{reads=}")
        mean = sum(reads) / len(reads)
        print(f"Average volume: {mean:.1f} gallons")
        return mean

    def read_tank(self):
        retry_cnt = 0
        while retry_cnt < 3:
            try:
                (volume, depth) = self._get_volume()
                print(f"Volume: {volume:.1f} gallons")
                return (volume, depth)
            except ValueError as e:
                print(f"Error in read.  Message was: {e}")
                retry_cnt += 1
                print(f"Retrying... attempt {retry_cnt}")
                sleep_ms(1000)
                # asyncio.sleep(0.5)

    def _get_volume(self):
        """Get the current tank volume

        Returns:
            float: Tank volume (cm3)
        """
        print("\nGet volume...")
        distance = self.get_distance()
        depth = self._mounted_distance + self.TOTAL_MAX_HEIGHT - distance
        print(f"Dist = {distance:.2f} in, Depth = {depth:.2f}in")

        volume = self._calculate_combined_volume(depth=depth)

        if volume < 0.0:
            return (0, 0)

        if volume < self.TOTAL_VOLUME_GALLONS:
            return (volume, depth)

        return (self.TOTAL_VOLUME_GALLONS, self.TOTAL_MAX_HEIGHT)

    def _cone_volume(self, height: float):
        # V=πr2h/3
        val = math.pi * (self.RADIUS**2) * height / 3
        # print(f"Cone volume = {val}in3")
        return self._in3_to_gallons(val)

    def _cylinder_volume(self, height: float):
        val = math.pi * (self.RADIUS**2) * height
        # print(f"Cylinder volume = {val}in3")
        return self._in3_to_gallons(val)

    def _calculate_combined_volume(self, depth: float):
        if depth > self.CONE_MAX_HEIGHT:
            volume = self._cylinder_volume(depth - self.CONE_MAX_HEIGHT)
            volume += self._cone_volume(self.CONE_MAX_HEIGHT)
        else:
            volume = self._cone_volume(depth)

        # Convert to gallons
        return volume

    def _in3_to_gallons(self, volume: float):
        return volume * 0.004329


async def tank_routine(set_data: function):
    ev = EvoMini(1, 8, 9)
    tank = Tank(ev.read_range, 210)

    while True:
        volume = tank.get_volume()
        await set_data(volume)
        print(f"{volume=} Gallons\n")
        await asyncio.sleep(1)
