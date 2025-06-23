from dataclasses import dataclass

@dataclass(slots=True, kw_only=True)
class UserData:
    receptor: str
    sender: str
    token: str
