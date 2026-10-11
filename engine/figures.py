"""Figure registry: every Figure built in one engine run (TRD §5.9)."""
from api.contracts import Figure


class FigureRegistry:
    """Collects Figures for EngineResult.figures. Ids must be unique within a run."""

    def __init__(self) -> None:
        self._figures: dict[str, Figure] = {}

    def add(self, figure: Figure) -> Figure:
        """Store `figure` and return it. Raise ValueError if its id is already registered.

        V2 must add at least one assert check.
        """
        raise NotImplementedError("engine.figures.FigureRegistry.add")

    def as_dict(self) -> dict[str, Figure]:
        """Return the registry keyed by id, for EngineResult.figures.

        V2 must add at least one assert check.
        """
        raise NotImplementedError("engine.figures.FigureRegistry.as_dict")
