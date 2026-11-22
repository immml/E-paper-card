# SPDX-License-Identifier: AGPL-3.0-or-later
from dataclasses import dataclass
from enum import Enum
try:
    from .protocol import BUTTON_EVENT, Frame, GET_POWER, ProtocolError, SET_POWER, USB_EVENT, decode, encode
except ImportError:
    from protocol import BUTTON_EVENT, Frame, GET_POWER, ProtocolError, SET_POWER, USB_EVENT, decode, encode


class PowerState(str, Enum):
    OFF = "OFF"
    BOOTING = "BOOTING"
    RUN = "RUN"
    SLEEP = "SLEEP"
    RESCUE = "RESCUE"


@dataclass
class DeviceSimulator:
    state: PowerState = PowerState.OFF
    usb_present: bool = False
    last_sequence: int | None = None

    def reset(self) -> None:
        self.state = PowerState.OFF
        self.usb_present = False
        self.last_sequence = None

    def transact(self, raw: bytes) -> bytes:
        frame = decode(raw)
        if frame.sequence == self.last_sequence:
            raise ProtocolError("duplicate sequence")
        self.last_sequence = frame.sequence
        if frame.command == GET_POWER:
            payload = self.state.value.encode("ascii")
        elif frame.command == SET_POWER:
            self.state = PowerState(frame.payload.decode("ascii"))
            payload = self.state.value.encode("ascii")
        elif frame.command == USB_EVENT:
            self.usb_present = bool(frame.payload[0])
            payload = bytes((int(self.usb_present),))
        elif frame.command == BUTTON_EVENT:
            if frame.payload == b"long" and self.state == PowerState.OFF:
                self.state = PowerState.BOOTING
            payload = self.state.value.encode("ascii")
        else:
            raise ProtocolError("unsupported command")
        return encode(Frame(frame.command, frame.sequence, payload))
