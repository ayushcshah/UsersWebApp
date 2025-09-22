from dataclasses import dataclass, asdict
from typing import List, Dict

@dataclass
class User:
    id: int
    email: str
    first_name: str
    last_name: str
    avatar: str

@dataclass
class Support:
    url: str
    text: str

@dataclass
class UserResponse:
    data: User
    support: Support

    def to_dict(self) -> Dict:
        return {
            "data": asdict(self.data),
            "support": asdict(self.support)
        }

@dataclass
class Users:
    page: int
    per_page: int
    total: int
    total_pages: int
    data: List[User]


    def to_dict(self) -> Dict:
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            "total_pages": self.total_pages,
            "data": [asdict(u) for u in self.data]
        }
