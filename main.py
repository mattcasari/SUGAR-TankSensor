from machine import reset
from src.lib.microdot import Microdot, Response, send_file
from src.lib.tr_evo_mini import EvoMini
from src.tank import Tank

from config import MOUNT_DEPTH

app = Microdot()
ev = EvoMini(1, 3, 4)
tank = Tank(get_distance=ev.read_range_in, mounted_distance=MOUNT_DEPTH)
current_task = None
Response.default_content_type = "text/html"


def get_html():
    with open("index.html") as f:
        html = f.read()

    return html


@app.route("/volume")
async def get_volume(request):
    #
    print("volume request received")
    return str(tank.read_tank()[0])


@app.route("/")
async def main(request):
    global tank
    # return send_file("index.html")
    print("\nMain page request received")
    with open("index.html") as f:
        html = f.read()

    (volume, depth) = (None, None)

    try:
        (volume, depth) = tank.read_tank()
    except:
        pass
    # volume = tank.get_volume_average(3)

    if volume:
        percent = 100 * volume / tank.TOTAL_VOLUME_GALLONS

        html = html.replace("TANK_VOLUME", f"{volume:.0f}")
        html = html.replace("TANK_PERCENT", f"{percent:.0f}")
        html = html.replace("TANK_DEPTH", f"{depth:.0f}")
    else:
        html = html.replace("TANK_VOLUME", "ERROR")
        html = html.replace("TANK_PERCENT", "ERROR")
        html = html.replace("TANK_DEPTH", "ERROR")
    return html


def start_server():
    print("Starting app...")
    try:
        app.run(port=80)
    except:
        app.shutdown()
        reset()

    # finally:


start_server()
