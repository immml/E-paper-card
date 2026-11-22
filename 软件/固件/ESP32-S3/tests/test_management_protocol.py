import struct
import unittest

SOF = 0xA5
VERSION = 1
MAX_PAYLOAD = 64


def crc16(data: bytes) -> int:
    crc = 0xFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = ((crc >> 1) ^ 0xA001) if crc & 1 else crc >> 1
    return crc


def encode(command: int, sequence: int, payload: bytes) -> bytes:
    if len(payload) > MAX_PAYLOAD:
        raise ValueError("payload too large")
    header = bytes((SOF, VERSION, command, sequence)) + struct.pack("<H", len(payload)) + b"\0"
    return header + payload + struct.pack("<H", crc16(header[1:] + payload))


def decode(frame: bytes):
    if len(frame) < 9 or frame[0] != SOF or frame[1] != VERSION:
        raise ValueError("invalid header")
    payload_length = struct.unpack_from("<H", frame, 4)[0]
    if payload_length > MAX_PAYLOAD or len(frame) != 9 + payload_length:
        raise ValueError("invalid length")
    if crc16(frame[1:-2]) != struct.unpack_from("<H", frame, len(frame) - 2)[0]:
        raise ValueError("invalid crc")
    return frame[2], frame[3], frame[7:-2]


def classify(duration_ms: int) -> str:
    if duration_ms < 200: return "tap"
    if duration_ms <= 1500: return "short"
    if duration_ms <= 2000: return "invalid"
    return "long"


def release_off(duration_ms: int, usb_during_press: bool, usb_present: bool) -> str:
    if usb_during_press: return "rescue" if usb_present else "off"
    return "booting" if classify(duration_ms) == "long" else "off"


class ManagementProtocolTests(unittest.TestCase):
    def test_round_trip_empty_and_max_payload(self):
        for payload in (b"", bytes(range(MAX_PAYLOAD))):
            self.assertEqual(decode(encode(1, 7, payload)), (1, 7, payload))

    def test_rejects_header_length_and_crc_errors(self):
        frame = bytearray(encode(1, 2, b"abc"))
        for index in (0, 1):
            broken = bytearray(frame); broken[index] ^= 1
            with self.assertRaises(ValueError): decode(broken)
        broken = bytearray(frame); broken[4] = 0; broken[5] = 0
        with self.assertRaises(ValueError): decode(broken)
        broken = bytearray(frame); broken[-1] ^= 1
        with self.assertRaises(ValueError): decode(broken)

    def test_rejects_oversized_payload(self):
        with self.assertRaises(ValueError): encode(1, 1, bytes(MAX_PAYLOAD + 1))

    def test_power_boundaries_and_rescue_release(self):
        self.assertEqual([classify(i) for i in (199, 200, 1500, 1501, 2000, 2001)], ["tap", "short", "short", "invalid", "invalid", "long"])
        self.assertEqual(release_off(2001, True, True), "rescue")
        self.assertEqual(release_off(2001, True, False), "off")
        self.assertEqual(release_off(2001, False, True), "booting")


if __name__ == "__main__": unittest.main()
