from dataclasses import dataclass


@dataclass
class Invoice:
    invoice_number: str = ""
    client: str = ""
    amount: float = 0.0
    due_date: str = ""
    status: str = "draft"  # draft, sent, paid, overdue
    email: str = ""

    @classmethod
    def from_dict(cls, d):
        fields = {}
        for k in cls.__dataclass_fields__:
            val = d.get(k, "")
            if k == "amount":
                try:
                    val = float(val) if val != "" else 0.0
                except (ValueError, TypeError):
                    val = 0.0
            fields[k] = val
        return cls(**fields)

    def to_dict(self):
        return {k: getattr(self, k) for k in self.__dataclass_fields__}
