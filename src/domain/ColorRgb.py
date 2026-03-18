"""
RGB color domain model for the GBA Tile Quantizer.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ColorRgb:
    """
    Represents a single RGB color using 8-bit channel values.
    """

    red: int
    green: int
    blue: int

    def __post_init__(self) -> None:
        """
        Validate channel values after initialization.
        """
        self._validate_channel("red", self.red)
        self._validate_channel("green", self.green)
        self._validate_channel("blue", self.blue)

    def to_tuple(self) -> tuple[int, int, int]:
        """
        Convert the color to a standard RGB tuple.

        Returns:
            A tuple of (red, green, blue).
        """
        return self.red, self.green, self.blue

    @staticmethod
    def from_tuple(value: tuple[int, int, int]) -> "ColorRgb":
        """
        Create a ColorRgb from an RGB tuple.

        Args:
            value: Tuple containing (red, green, blue).

        Returns:
            A ColorRgb instance.

        Raises:
            ValueError: If the tuple does not contain exactly 3 values.
        """
        if len(value) != 3:
            raise ValueError("RGB tuple must contain exactly 3 values.")

        return ColorRgb(
            red=value[0],
            green=value[1],
            blue=value[2],
        )

    def distance_squared(self, other: "ColorRgb") -> int:
        """
        Compute the squared Euclidean distance to another RGB color.

        Args:
            other: Color to compare against.

        Returns:
            The squared distance.

        Raises:
            TypeError: If other is not a ColorRgb instance.
        """
        if not isinstance(other, ColorRgb):
            raise TypeError("other must be a ColorRgb instance.")

        red_difference = self.red - other.red
        green_difference = self.green - other.green
        blue_difference = self.blue - other.blue

        return (
            (red_difference * red_difference)
            + (green_difference * green_difference)
            + (blue_difference * blue_difference)
        )

    def weighted_distance_squared(self, other: "ColorRgb") -> int:
        """
        Compute a weighted squared RGB distance to another color.

        Green is weighted more heavily because it is visually important
        in many image comparison contexts.

        Args:
            other: Color to compare against.

        Returns:
            The weighted squared distance.

        Raises:
            TypeError: If other is not a ColorRgb instance.
        """
        if not isinstance(other, ColorRgb):
            raise TypeError("other must be a ColorRgb instance.")

        red_difference = self.red - other.red
        green_difference = self.green - other.green
        blue_difference = self.blue - other.blue

        return (
            (2 * red_difference * red_difference)
            + (4 * green_difference * green_difference)
            + (3 * blue_difference * blue_difference)
        )

    @staticmethod
    def _validate_channel(channel_name: str, value: int) -> None:
        """
        Validate a single color channel value.

        Args:
            channel_name: Name of the channel being validated.
            value: Channel value.

        Raises:
            ValueError: If the channel value is invalid.
        """
        if not isinstance(value, int):
            raise ValueError(f"{channel_name} must be an integer.")

        if value < 0 or value > 255:
            raise ValueError(f"{channel_name} must be between 0 and 255.")
