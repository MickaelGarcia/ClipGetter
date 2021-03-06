import os
import re

CLIP_PATTERNS = [r"^https:\/\/(clips|www).twitch.tv\/([0-z\-]+)$"]


def get_logs(path, date = ""):

    clip_list = []
    with open(path, "r", encoding='utf-8') as f:
        logs = f.readlines()

    for line in logs:
        for pattern in CLIP_PATTERNS:
            match = re.match(pattern, line)
            if match:
                if line not in clip_list:
                    line.replace("\n","")
                    clip_list.append(line.replace("\n",""))

    clip_list = list(set(clip_list))
    return  clip_list