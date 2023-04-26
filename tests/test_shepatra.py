import hashlib

from blake3 import blake3

from src.scripts.utils import json_to_translation_systems, \
    translation_systems_to_json

algorithms = {
    "sha3-512": hashlib.sha3_512,
    "blake2b": hashlib.blake2b,
    "blake3": blake3}
algorithms_reversed = dict(zip(algorithms.values(), algorithms.keys()))


def test_json_to_translation_systems():
    trans_systems = {}
    json_dict = {"testname": ["sha3-512", "blake2b", "blake3"],
                 "testname_two": ["sha3-512", "blake2b"]}
    trans_systems = json_to_translation_systems(json_dict, algorithms)
    assert trans_systems == {
        "testname": [hashlib.sha3_512, hashlib.blake2b, blake3],
        "testname_two": [hashlib.sha3_512, hashlib.blake2b]}


def test_translation_systems_to_json():
    trans_systems = {
        "testname": [hashlib.sha3_512, hashlib.blake2b, blake3],
        "testname_two": [hashlib.sha3_512, hashlib.blake2b]}
    json_dict = translation_systems_to_json(trans_systems, algorithms_reversed)
    assert json_dict == {
        "testname": ["sha3-512", "blake2b", "blake3"],
        "testname_two": ["sha3-512", "blake2b"]}
