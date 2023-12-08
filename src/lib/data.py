from dataclasses import dataclass


@dataclass
class Match:
    url: str
    title: str
    preview: str
