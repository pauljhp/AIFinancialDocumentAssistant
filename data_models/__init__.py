from pydantic import BaseModel
from typing import Optional, List, Sequence, Annotated, Collection


class CompanyInfo(BaseModel):
    """Container representation of a company"""
    figi: Annotated[str, "Bloomberg FIGI of the company"] = ""
    isin: Annotated[str, "ISIN of the company"] = ""
    sedol: Annotated[str, "SEDOL of the company"] = ""
    short_name: Annotated[str, "short name of the company"] = ""
    name: Annotated[str, "full name of the company"] = ""
    aliases: Optional[
        Annotated[
            Sequence[str], 
            "Collection of the aliases the company is known as"]
            ] = []

    def __eq__(self, other):
        if self.figi == other.figi or self.isin == other.isin or self.sedol == other.sedol:
            return True
        return False