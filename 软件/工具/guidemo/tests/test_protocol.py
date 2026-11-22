# SPDX-License-Identifier: AGPL-3.0-or-later
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))
from protocol import Frame, ProtocolError, decode, encode

class ProtocolTests(unittest.TestCase):
    def test_round_trip_boundaries(self):
        for payload in (b"", bytes(range(64))):
            self.assertEqual(decode(encode(Frame(1, 3, payload))), Frame(1, 3, payload))

    def test_rejects_bad_crc_and_headers(self):
        frame = bytearray(encode(Frame(1, 1, b"x")))
        for index in (0, 1, len(frame) - 1):
            invalid = bytearray(frame); invalid[index] ^= 1
            with self.assertRaises(ProtocolError): decode(invalid)

    def test_rejects_oversized_payload(self):
        with self.assertRaises(ProtocolError): encode(Frame(1, 1, bytes(65)))
