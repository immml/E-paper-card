# SPDX-License-Identifier: AGPL-3.0-or-later
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from protocol import BUTTON_EVENT, Frame, GET_POWER, ProtocolError, USB_EVENT, decode, encode
from simulator import DeviceSimulator, PowerState

class SimulatorTests(unittest.TestCase):
    def setUp(self):
        self.device = DeviceSimulator()
        self.sequence = 0
    def send(self, command, payload=b""):
        self.sequence += 1
        return decode(self.device.transact(encode(Frame(command, self.sequence, payload))))
    def test_power_and_usb_commands(self):
        self.assertEqual(self.send(GET_POWER).payload, b"OFF")
        self.assertEqual(self.send(BUTTON_EVENT, b"long").payload, b"BOOTING")
        self.device.reset(); self.assertEqual(self.send(USB_EVENT, b"\1").payload, b"\1")
        self.assertTrue(self.device.usb_present)
    def test_duplicate_sequence_is_rejected(self):
        raw = encode(Frame(GET_POWER, 1))
        self.device.transact(raw)
        with self.assertRaises(ProtocolError): self.device.transact(raw)
    def test_invalid_state_is_rejected(self):
        with self.assertRaises(ValueError): self.send(2, b"NOT_A_STATE")

if __name__ == "__main__": unittest.main()
