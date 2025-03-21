from machine import UART
from time import sleep_ms


class EvoMini:
    TEXT_MODE = b"\x00\x11\x01\x45"
    BINARY_MODE = b"\x00\x01\x02\x4c"
    PIXEL_MODE_1PX = b"\x00\x21\x01\xbc"
    PIXEL_MODE_2PX = b"\x00\x21\x03\xb2"
    PIXEL_MODE_4PX = b"\x00\x21\x02\xb5"
    SHORT_RANGE_MODE = b"\x00\x61\x01\xe7"
    LONG_RANGE_MODE = b"\x00\x61\x03\xe9"

    def __init__(self, port: int, tx: int, rx: int):
        self._uart = UART(port, baudrate=115200, tx=tx, rx=rx, timeout=5)
        self._uart.init(115200, bits=8, parity=None, stop=1, timeout=5)
        sleep_ms(1000)
        self.config()

    def config(self):
        self._write(self.TEXT_MODE)
        sleep_ms(500)
        self._write(self.PIXEL_MODE_1PX)
        sleep_ms(500)
        self._write(self.LONG_RANGE_MODE)

        while self._uart.readline() != None:
            pass

    def read_range(self) -> float:
        """Read the sensor and calculate the distance

        Raises:
            ValueError: Bad string
            ValueError: Not enough fields returned

        Returns:
            float: Distance in cm
        """

        range = self._read()

        if type(range) is not str:
            raise ValueError("No response")

        range = range.strip()
        range = range.split(",")
        print(f"{range=}")

        # Remove +inf and -inf values
        range = [item for item in range if item is not "+Inf"]
        range = [item for item in range if item is not "-Inf"]

        # Remove None values from list
        range = [item for item in range if item is not None]

        # Convert the values to integers
        range = [int(r) for r in range]

        # Remove values of -1 from list
        range = [r for r in range if r != -1]

        # print(f"Final {range=}\n")

        if len(range) < 1:
            raise ValueError(f"No valid ranges reported")

        ave_range_mm = sum(range) / len(range)

        return ave_range_mm / 10  # Return cm

    def read_range_in(self):
        val = self.read_range() / 2.54
        print(f"Dist={val:.2f} in")
        return val

    def _write(self, msg: bytes):
        print(self._uart.write(msg))

    def _read(self) -> str | None:
        val_last = None
        while True:
            val = self._uart.readline()
            if val == None:
                value = val_last
                break
            val_last = val

        # print(f"{value=}")
        if value:
            return value.decode("utf-8")
        return None
