import enum
from typing import NewType

VariantId = NewType('VariantId', str)

class Ploidy(enum.Enum):
    haploid = 1
    diploid = 2

class Phasing(enum.Enum):
    unphased = "/"
    phased = "|"

class Genotype():
    phasing: Phasing
    ploidy: Ploidy
    a1: str
    a2: str | None #if haploid, only a2 is None

    def __init__(self, genotype: str) -> None:
        """
        Get a genotype string. It could be haploid "ACTG", or diploid phased "AC|TG" or diploid unphased "AC/TG". Then, converts it into a Genotype object.
        """
        if Phasing.phased.value in genotype:
            self.phasing = Phasing.phased
            self.a1, self.a2 = genotype.split(Phasing.phased.value, maxsplit=1)
            self.ploidy = Ploidy.diploid
        elif Phasing.unphased.value in genotype:
            self.phasing = Phasing.unphased
            self.a1, self.a2 = genotype.split(Phasing.unphased.value, maxsplit=1)
            self.ploidy = Ploidy.diploid
        else:
            self.phasing = Phasing.unphased
            self.a1 = genotype
            self.a2 = None
            self.ploidy = Ploidy.haploid

    def __eq__(self, other):
        """
        Compare two Genotype objects for equality.
        Note: This implementation does not care for phasing during comparison.
        """
        if not isinstance(other, Genotype):
            return False
        return (
            (self.a1 == other.a1 and self.a2 == other.a2)
                or
            (self.a2 == other.a1 and self.a1 == other.a2)
            )

    def __repr__(self) -> str:
        """
        Return a string representation of the Genotype object.
        """
        if self.ploidy == Ploidy.haploid:
            return f"GT<{self.a1}>"
        elif self.ploidy == Ploidy.diploid:
            if self.phasing == Phasing.phased:
                return f"GT<{self.a1}{Phasing.phased.value}{self.a2}>"
            elif self.phasing == Phasing.unphased:
                return f"GT<{self.a1}{Phasing.unphased.value}{self.a2}>"
        return ""