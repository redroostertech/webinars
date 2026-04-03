from dataclasses import dataclass


@dataclass
class Project:
    name: str = ""
    client: str = ""
    budget: float = 0.0
    total_billed: float = 0.0
    deadline: str = ""
    status: str = "active"  # active, completed, on_hold
    sheet_id: str = ""      # Google Sheet ID linked to this project

    @classmethod
    def from_dict(cls, d):
        fields = {}
        for k in cls.__dataclass_fields__:
            val = d.get(k, "")
            if k in ("budget", "total_billed"):
                try:
                    val = float(val) if val != "" else 0.0
                except (ValueError, TypeError):
                    val = 0.0
            fields[k] = val
        return cls(**fields)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}

    @property
    def sheet_url(self):
        if self.sheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"
        return ""
