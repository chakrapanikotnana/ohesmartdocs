import json
import os
from datetime import datetime

from numpy import record

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "submissions.json")


def ensure_data_file():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump([], f)


def read_records():
    ensure_data_file()

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_record(record: dict):

    ensure_data_file()

    records = read_records()

    record["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if "download_flag" not in record:
        record["download_flag"] = False

    if "downloaded_at" not in record:
        record["downloaded_at"] = ""

    records.append(record)

    with open(DATA_FILE, "w") as f:
        json.dump(records, f, indent=4)
def mark_all_downloaded():

    records = read_records()
    downloaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for r in records:
        r["download_flag"] = True
        r["downloaded_at"] = downloaded_at

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)

def get_all_records():
    return read_records()
def get_unexported_records():

    records = read_records()

    return [
        r for r in records
        if not r.get("download_flag", False)
    ]


def mark_records_downloaded(exported_records, downloaded_at=None):

    records = read_records()
    downloaded_at = downloaded_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    exported_keys = {
        (
            r.get("username"),
            r.get("created_at"),
            r.get("FileName")
        )
        for r in exported_records
    }

    for r in records:

        key = (
            r.get("username"),
            r.get("created_at"),
            r.get("FileName")
        )

        if key in exported_keys:
            r["download_flag"] = True
            r["downloaded_at"] = downloaded_at

    for r in exported_records:
        r["download_flag"] = True
        r["downloaded_at"] = downloaded_at

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4)
def get_downloaded_records(username=None):

    records = read_records()

    filtered = records

    if username:
        filtered = [
            r for r in filtered
            if r.get("username") == username
        ]

    return filtered


def get_records_by_created_at(created_at_list):

    records = read_records()

    return [
        r for r in records
        if r.get("created_at") in created_at_list
    ]
