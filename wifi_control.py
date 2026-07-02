import network
import socket
from time import sleep_ms, ticks_ms, ticks_diff


HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0, user-scalable=no"
    >

    <title>Robot ESP32-C6</title>

    <style>
        * {
            box-sizing: border-box;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            margin: 0;
            padding: 20px;
            min-height: 100vh;

            background: #101114;
            color: #ffffff;

            font-family: Arial, sans-serif;
            text-align: center;

            touch-action: manipulation;
        }

        .panel {
            width: 100%;
            max-width: 430px;

            margin: 0 auto;
            padding: 22px;

            background: #1b1d22;
            border: 1px solid #343840;
            border-radius: 22px;
        }

        h1 {
            margin: 0 0 20px;
            font-size: 26px;
        }

        .telemetry {
            display: grid;
            grid-template-columns: 1fr 1fr;

            gap: 10px;
            margin-bottom: 18px;
        }

        .telemetry-box {
            padding: 14px 8px;

            background: #252830;
            border-radius: 12px;
        }

        .telemetry-label {
            display: block;

            margin-bottom: 6px;

            color: #aeb4c0;
            font-size: 13px;
        }

        .telemetry-value {
            font-size: 21px;
            font-weight: bold;
        }

        .obstacle-status {
            margin: 18px 0;
            padding: 16px;

            border-radius: 14px;

            font-size: 19px;
            font-weight: bold;

            background: #343842;
        }

        .obstacle-clear {
            background: #1f6f43;
            color: #ffffff;
        }

        .obstacle-danger {
            background: #a52b2b;
            color: #ffffff;

            animation: alertPulse 0.7s infinite alternate;
        }

        .obstacle-error {
            background: #755719;
            color: #ffffff;
        }

        @keyframes alertPulse {
            from {
                opacity: 1;
            }

            to {
                opacity: 0.6;
            }
        }

        .speed-container {
            margin: 22px 0;
        }

        #speed {
            width: 100%;
            height: 32px;
        }

        .controls {
            display: grid;
            grid-template-columns: repeat(3, 1fr);

            gap: 12px;
            margin-top: 18px;
        }

        button {
            min-height: 78px;
            padding: 8px;

            border: none;
            border-radius: 16px;

            background: #343842;
            color: white;

            font-size: 16px;
            font-weight: bold;

            cursor: pointer;
            user-select: none;
            touch-action: none;
        }

        button:active,
        button.active {
            background: #666e7d;
            transform: scale(0.97);
        }

        .stop {
            background: #a52b2b;
        }

        .stop:active,
        .stop.active {
            background: #e04444;
        }

        .empty {
            visibility: hidden;
        }

        .connection {
            margin-top: 18px;

            color: #9ca3af;
            font-size: 13px;
        }

        .connected {
            color: #68d391;
        }

        .disconnected {
            color: #ff6b6b;
        }
    </style>
</head>

<body>
    <div class="panel">
        <h1>Robot ESP32-C6</h1>

        <div class="telemetry">
            <div class="telemetry-box">
                <span class="telemetry-label">Distance</span>
                <span class="telemetry-value">
                    <span id="distance">--</span> cm
                </span>
            </div>

            <div class="telemetry-box">
                <span class="telemetry-label">Angle radar</span>
                <span class="telemetry-value">
                    <span id="angle">--</span> deg
                </span>
            </div>

            <div class="telemetry-box">
                <span class="telemetry-label">Commande</span>
                <span
                    id="command"
                    class="telemetry-value"
                >
                    STOP
                </span>
            </div>

            <div class="telemetry-box">
                <span class="telemetry-label">Vitesse</span>
                <span class="telemetry-value">
                    <span id="speedValue">55</span> %
                </span>
            </div>
        </div>

        <div
            id="obstacleStatus"
            class="obstacle-status obstacle-error"
        >
            CAPTEUR EN ATTENTE
        </div>

        <div class="speed-container">
            <input
                id="speed"
                type="range"
                min="20"
                max="100"
                value="55"
            >
        </div>

        <div class="controls">
            <button class="empty"></button>

            <button data-command="forward">
                AVANT
            </button>

            <button class="empty"></button>

            <button data-command="left">
                GAUCHE
            </button>

            <button
                class="stop"
                data-command="stop"
            >
                STOP
            </button>

            <button data-command="right">
                DROITE
            </button>

            <button class="empty"></button>

            <button data-command="backward">
                ARRIERE
            </button>

            <button class="empty"></button>
        </div>

        <div
            id="connection"
            class="connection"
        >
            Connexion au robot...
        </div>
    </div>

    <script>
        const speedSlider =
            document.getElementById("speed");

        const speedValue =
            document.getElementById("speedValue");

        const commandValue =
            document.getElementById("command");

        const connectionValue =
            document.getElementById("connection");

        const obstacleStatus =
            document.getElementById("obstacleStatus");

        let repeatTimer = null;
        let activeCommand = null;

        speedSlider.addEventListener(
            "input",
            function () {
                speedValue.textContent =
                    speedSlider.value;
            }
        );

        function sendCommand(command) {
            const speed = speedSlider.value;

            fetch(
                "/cmd?name="
                + encodeURIComponent(command)
                + "&speed="
                + encodeURIComponent(speed),
                {
                    cache: "no-store"
                }
            )
            .then(function () {
                connectionValue.textContent =
                    "Robot connecte";

                connectionValue.className =
                    "connection connected";
            })
            .catch(function () {
                connectionValue.textContent =
                    "Connexion perdue";

                connectionValue.className =
                    "connection disconnected";
            });

            commandValue.textContent =
                command.toUpperCase();
        }

        function startCommand(command, button) {
            stopRepeating(false);

            activeCommand = command;
            button.classList.add("active");

            sendCommand(command);

            if (command !== "stop") {
                repeatTimer = setInterval(
                    function () {
                        sendCommand(command);
                    },
                    350
                );
            }
        }

        function stopRepeating(sendStop) {
            if (repeatTimer !== null) {
                clearInterval(repeatTimer);
                repeatTimer = null;
            }

            document
                .querySelectorAll("button.active")
                .forEach(function (button) {
                    button.classList.remove("active");
                });

            activeCommand = null;

            if (sendStop) {
                sendCommand("stop");
            }
        }

        document
            .querySelectorAll(
                "button[data-command]"
            )
            .forEach(function (button) {
                const command =
                    button.dataset.command;

                button.addEventListener(
                    "pointerdown",
                    function (event) {
                        event.preventDefault();

                        startCommand(
                            command,
                            button
                        );
                    }
                );

                button.addEventListener(
                    "pointerup",
                    function (event) {
                        event.preventDefault();

                        stopRepeating(
                            command !== "stop"
                        );
                    }
                );

                button.addEventListener(
                    "pointercancel",
                    function () {
                        stopRepeating(true);
                    }
                );

                button.addEventListener(
                    "contextmenu",
                    function (event) {
                        event.preventDefault();
                    }
                );
            });

        window.addEventListener(
            "blur",
            function () {
                stopRepeating(true);
            }
        );

        document.addEventListener(
            "visibilitychange",
            function () {
                if (document.hidden) {
                    stopRepeating(true);
                }
            }
        );

        function updateStatus() {
            fetch(
                "/status",
                {
                    cache: "no-store"
                }
            )
            .then(function (response) {
                return response.json();
            })
            .then(function (status) {
                document
                    .getElementById("distance")
                    .textContent =
                    status.distance;

                document
                    .getElementById("angle")
                    .textContent =
                    status.angle;

                const distance =
                    parseFloat(status.distance);

                if (isNaN(distance)) {
                    obstacleStatus.textContent =
                        "CAPTEUR INDISPONIBLE";

                    obstacleStatus.className =
                        "obstacle-status obstacle-error";
                }
                else if (distance <= 20) {
                    obstacleStatus.textContent =
                        "OBSTACLE DETECTE A "
                        + distance.toFixed(1)
                        + " CM";

                    obstacleStatus.className =
                        "obstacle-status obstacle-danger";
                }
                else {
                    obstacleStatus.textContent =
                        "ZONE LIBRE";

                    obstacleStatus.className =
                        "obstacle-status obstacle-clear";
                }

                connectionValue.textContent =
                    "Robot connecte";

                connectionValue.className =
                    "connection connected";
            })
            .catch(function () {
                connectionValue.textContent =
                    "Connexion perdue";

                connectionValue.className =
                    "connection disconnected";

                obstacleStatus.textContent =
                    "DONNEES INDISPONIBLES";

                obstacleStatus.className =
                    "obstacle-status obstacle-error";
            });
        }

        updateStatus();

        setInterval(
            updateStatus,
            500
        );
    </script>
</body>
</html>"""


def connect_wifi(ssid, password, timeout_ms=20000):
    try:
        wlan = network.WLAN(network.WLAN.IF_STA)
    except AttributeError:
        wlan = network.WLAN(network.STA_IF)

    wlan.active(True)

    if not wlan.isconnected():
        print("Connexion au Wi-Fi :", ssid)
        wlan.connect(ssid, password)

        start = ticks_ms()

        while not wlan.isconnected():
            if ticks_diff(ticks_ms(), start) > timeout_ms:
                raise RuntimeError("Connexion Wi-Fi impossible")

            sleep_ms(250)

    ip = wlan.ifconfig()[0]
    print("Wi-Fi connecte :", ip)
    print("Ouvre http://" + ip)

    return ip


class WebController:
    def __init__(self):
        self.command = "stop"
        self.speed = 55
        self.last = ticks_ms()

        self.distance = None
        self.angle = 90

        self.socket = socket.socket()

        self.socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.socket.bind(
            ("0.0.0.0", 80)
        )

        self.socket.listen(2)
        self.socket.settimeout(0.02)

    @staticmethod
    def _parse_query(path):
        values = {}

        if "?" not in path:
            return values

        query = path.split("?", 1)[1]

        for item in query.split("&"):
            if "=" in item:
                key, value = item.split("=", 1)
                values[key] = value

        return values

    @staticmethod
    def _send_response(
        client,
        body,
        content_type="text/html"
    ):
        if isinstance(body, str):
            body = body.encode("utf-8")

        header = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: {}; charset=utf-8\r\n"
            "Content-Length: {}\r\n"
            "Connection: close\r\n"
            "Cache-Control: no-store\r\n"
            "\r\n"
        ).format(
            content_type,
            len(body)
        )

        client.send(
            header.encode("utf-8")
        )

        client.send(body)

    def poll(self):
        try:
            client, _ = self.socket.accept()
        except OSError:
            return

        try:
            request = client.recv(1024).decode(
                "utf-8",
                "ignore"
            )

            first_line = request.split(
                "\r\n",
                1
            )[0]

            parts = first_line.split(" ")

            if len(parts) < 2:
                self._send_response(
                    client,
                    "Requete invalide",
                    "text/plain"
                )

                return

            path = parts[1]

            if path.startswith("/cmd"):
                query = self._parse_query(path)

                command = query.get(
                    "name",
                    "stop"
                )

                if command not in (
                    "forward",
                    "backward",
                    "left",
                    "right",
                    "stop"
                ):
                    command = "stop"

                try:
                    speed = int(
                        query.get(
                            "speed",
                            self.speed
                        )
                    )
                except ValueError:
                    speed = self.speed

                self.command = command
                self.speed = max(
                    20,
                    min(100, speed)
                )

                self.last = ticks_ms()

                self._send_response(
                    client,
                    "OK",
                    "text/plain"
                )

            elif path.startswith("/status"):
                if self.distance is None:
                    distance = "N/A"
                else:
                    distance = "{:.1f}".format(
                        self.distance
                    )

                body = (
                    '{{'
                    '"distance":"{}",'
                    '"angle":{},'
                    '"command":"{}",'
                    '"speed":{}'
                    '}}'
                ).format(
                    distance,
                    self.angle,
                    self.command.upper(),
                    self.speed
                )

                self._send_response(
                    client,
                    body,
                    "application/json"
                )

            else:
                self._send_response(
                    client,
                    HTML,
                    "text/html"
                )

        except Exception as exc:
            print(
                "Erreur serveur web :",
                exc
            )

        finally:
            client.close()
