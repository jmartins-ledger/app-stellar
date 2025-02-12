#!/usr/bin/env python3

"""
./speculos.py --log-level automation:DEBUG --automation file:$HOME/app-xrp/tests/automation.json ~/app-xrp/bin/app.elf &

export LEDGER_PROXY_ADDRESS=127.0.0.1 LEDGER_PROXY_PORT=9999
pytest-3 -v -s
"""

import binascii
import json
import pytest
import sys
import time
from enum import IntEnum

from ledgerwallet.client import LedgerClient, CommException
from ledgerwallet.crypto.ecc import PrivateKey
from ledgerwallet.params import Bip32Path
from ledgerwallet.transport import enumerate_devices

DEFAULT_PATH = "44'/148'/0'"
CLA = 0xE0


class Ins(IntEnum):
    GET_PUBLIC_KEY = 0x02
    SIGN = 0x04


class P1(IntEnum):
    NO_SIGNATURE = 0x00
    SIGNATURE = 0x01
    FIRST = 0x00
    MORE = 0x80


class P2(IntEnum):
    NON_CONFIRM = 0x00
    CONFIRM = 0x01
    LAST = 0x00
    MORE = 0x80


@pytest.fixture(scope="module")
def client():
    devices = enumerate_devices()
    if len(devices) == 0:
        print("No Ledger device has been found.")
        sys.exit(0)

    return LedgerClient(devices[0], cla=CLA)


class TestGetPublicKey:
    INS = Ins.GET_PUBLIC_KEY

    def test_get_public_key(self, client):
        path = Bip32Path.build(DEFAULT_PATH)
        client.apdu_exchange(
            self.INS, path, P1.NO_SIGNATURE, P2.NON_CONFIRM)

    def test_path_too_long(self, client):
        path = Bip32Path.build(
            DEFAULT_PATH + "/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0/0")
        with pytest.raises(CommException) as e:
            client.apdu_exchange(
                self.INS, path, P1.NO_SIGNATURE, P2.NON_CONFIRM)
        assert e.value.sw == 0x6a80


class TestSign:
    INS = Ins.SIGN

    def _send_payload(self, client, payload):
        chunk_size = 255
        first = True
        while payload:
            if first:
                p1 = P1.FIRST
                first = False
            else:
                p1 = P1.MORE

            size = min(len(payload), chunk_size)
            if size != len(payload):
                p2 = P2.MORE
            else:
                p2 = P2.LAST

            client.apdu_exchange(self.INS, payload[:size], p1, p2)
            payload = payload[size:]

#     def test_sign_too_large(self, client):
#         max_size = 8000
#         path = Bip32Path.build(DEFAULT_PATH)
#         payload = path + b"a" * (max_size - 4)
#         with pytest.raises(CommException) as e:
#             self._send_payload(client, payload)
#         assert e.value.sw == 0x6700

#     def test_sign_invalid_tx(self, client):
#         path = Bip32Path.build(DEFAULT_PATH)
#         payload = path + b"a" * (40)
#         with pytest.raises(CommException) as e:
#             self._send_payload(client, payload)
#         assert e.value.sw == 0x6803

    def test_sign_valid_tx(self, client, raw_tx_path):

        with open(raw_tx_path, "rb") as fp:
            tx = fp.read()

        path = Bip32Path.build(DEFAULT_PATH)
        payload = path + tx
        self._send_payload(client, payload)
