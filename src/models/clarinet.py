
from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import json

@dataclass
class Hole:
    """
    Represents a tone hole on the instrument.
    """
    position: float  # Distance from the start of the instrument (m)
    radius: float    # Radius of the hole (m)
    chimney: float   # Height of the chimney (m)
    label: str = ""  # Human-readable label (e.g., "Register Key")

    def to_list(self) -> List[float]:
        """
        Returns list representation [pos, radius, chimney] for OpenWind.
        """
        return [self.position, self.radius, self.chimney]

@dataclass
class BoreSection:
    """
    Represents a point in the bore profile (radius at a specific position).
    """
    position: float
    radius: float

@dataclass
class Clarinet:
    """
    Main data model for the Clarinet geometry.
    Manages bore profile and tone holes.
    """
    name: str = "Prototype Clarinet"
    bore: List[BoreSection] = field(default_factory=list)
    holes: List[Hole] = field(default_factory=list)

    def add_bore_point(self, position: float, radius: float):
        """Adds a point to the bore profile and sorts by position."""
        if radius <= 0:
            raise ValueError("Bore radius must be positive.")
        self.bore.append(BoreSection(position, radius))
        self.bore.sort(key=lambda x: x.position)

    def add_hole(self, position: float, radius: float, chimney: float, label: str = ""):
        """Adds a tone hole and sorts by position."""
        if radius <= 0:
            raise ValueError("Hole radius must be positive.")
        self.holes.append(Hole(position, radius, chimney, label))
        self.holes.sort(key=lambda x: x.position)

    def get_bore_list(self) -> List[List[float]]:
        """Returns bore in format expected by OpenWind: [[x, r], ...]"""
        return [[b.position, b.radius] for b in self.bore]

    def get_holes_list(self) -> List[List[float]]:
        """Returns holes in format expected by OpenWind: [[x, r, chimney], ...]"""
        return [h.to_list() for h in self.holes]

    def save_to_file(self, filename: str):
        """Saves geometry to a JSON file."""
        data = {
            "name": self.name,
            "bore": [[b.position, b.radius] for b in self.bore],
            "holes": [[h.position, h.radius, h.chimney, h.label] for h in self.holes]
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    @classmethod
    def load_from_file(cls, filename: str):
        """Loads geometry from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        inst = cls(name=data.get("name", "Loaded Clarinet"))
        for b in data.get("bore", []):
            inst.add_bore_point(b[0], b[1])
        for h in data.get("holes", []):
            label = h[3] if len(h) > 3 else f"hole_{h[0]}"
            inst.add_hole(h[0], h[1], h[2], label)
        return inst

    @classmethod
    def default_clarinet(cls):
        """Creates a basic clarinet geometry for testing/starting."""
        inst = cls(name="Standard Bb Clarinet Prototype")
        # Simplified bore: Cylinder of length 0.6m, radius 7.5mm
        inst.add_bore_point(0.0, 0.0075)
        inst.add_bore_point(0.6, 0.0075)

        # Add some dummy tone holes
        inst.add_hole(0.5, 0.002, 0.005, "Tone Hole 1")
        inst.add_hole(0.55, 0.002, 0.005, "Tone Hole 2")
        return inst
