"""
Author: Hang Yan
Date created: 2023/8/13
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""

from enum import Enum


class MessageType(Enum):
    COMMAND = 1
    DATA = 2


if __name__ == "__main__":
    data = {
        "command_type": MessageType.COMMAND.value,
        "payload": "START"
    }