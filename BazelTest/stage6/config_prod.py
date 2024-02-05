"""
Author: Hang Yan
Date created: 2023/8/13
Email: topaz1668@gmail.com

This code is licensed under the GNU General Public License v3.0.
"""

from enum import Enum

HISTORY_SIZE = 30


class PromptEnum(Enum):
    ChatGPT = "ChatGPT"
    Dating = "Dating"
    Language = "Language"
    Kids = "Kids"
    Interview = "Interview"
    Prompt = "Prompt"
    PostHelper = "PostHelper"


prompt_settings = {
     PromptEnum.ChatGPT.value: {
        "prompt": "You are a helpful assistant.",
        "desc": ""
    },
     PromptEnum.Language.value: {
        "prompt": "You are a helpful assistant.",
        "desc": ""
    },
    PromptEnum.Kids.value: {
        "prompt": "You are a helpful assistant.",
        "desc": ""
    },
    PromptEnum.Dating.value: {
        "v1": {
            "prompt": "You are a helpful assistant.",
            "desc": ""
        },
        "v2": {
            "prompt": "You are a helpful assistant.",
            "desc": ""
        },
        "v3": {
            "prompt": "You are a helpful assistant.",
            "desc": ""
        }
    },
    PromptEnum.Interview.value: {
        "prompt": "You are a helpful assistant.",
        "desc": ""
    },
    PromptEnum.Prompt.value: {
        "v1":{
            "prompt": "You are a helpful assistant.",
            "desc": ""
        },
        "v2":{
            "prompt": "You are a helpful assistant.",
            "desc": ""
        }
    },
    PromptEnum.PostHelper.value: {
        "prompt": "You are a helpful assistant.",
        "desc": ""
    },
}

if __name__ == "__main__":
    enum_value = PromptEnum.Basic.value
    config = prompt_settings[enum_value]
    print(config)

