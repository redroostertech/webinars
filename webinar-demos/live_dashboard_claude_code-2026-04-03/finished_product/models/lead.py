from dataclasses import dataclass


@dataclass
class Lead:
    name: str = ""
    email: str = ""
    company: str = ""
    source: str = ""
    stage: str = "new"  # new, contacted, converted
    project: str = ""   # linked project name (filled by reconciliation)
    created_at: str = ""
    sheet_id: str = ""  # Google Sheet ID where this lead's data lives

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: d.get(k, "") for k in cls.__dataclass_fields__})

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}
