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
        assert isinstance(figure, Figure), "figure must be an instance of Figure"
        assert figure.id, "figure.id must not be empty"
        if figure.unit == "INR":
            assert float(figure.value).is_integer(), f"INR figure {figure.id} must be whole rupees, got {figure.value}"

        if figure.id in self._figures:
            raise ValueError(f"Figure id {figure.id!r} is already registered")

        self._figures[figure.id] = figure
        return figure

    def as_dict(self) -> dict[str, Figure]:
        """Return the registry keyed by id, for EngineResult.figures.

        V2 must add at least one assert check.
        """
        assert isinstance(self._figures, dict)
        return dict(self._figures)

