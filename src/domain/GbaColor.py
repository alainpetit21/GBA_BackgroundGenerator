"""
GBA color domain model (15-bit BGR format).
"""
from __future__ import annotations
from dataclasses import dataclass

from domain.ColorRgb import ColorRgb


@dataclass(frozen=True)
class GbaColor:
    """
    Represents a GBA color using 5 bits per channel (15-bit color).

    Format: 0BBBBBGGGGGRRRRR (little endian when stored as bytes)
    """

    red: int   # 0-31
    green: int # 0-31
    blue: int  # 0-31

    def __post_init__(self) -> None:
        """
        Validate channel values after initialization.
        """
        self._validate_channel("red", self.red)
        self._validate_channel("green", self.green)
        self._validate_channel("blue", self.blue)

    @staticmethod
    def from_rgb(rgb: ColorRgb) -> "GbaColor":
        """
        Convert a standard 8-bit RGB color to GBA 5-bit format.

        Args:
            rgb: ColorRgb instance.

        Returns:
            A GbaColor instance.
        """
        return GbaColor(
            red=rgb.red >> 3,
            green=rgb.green >> 3,
            blue=rgb.blue >> 3,
        )

    def to_rgb(self) -> ColorRgb:
        """
        Convert back to 8-bit RGB (approximate).

        Returns:
            A ColorRgb instance.
        """
        return ColorRgb(
            red=(self.red << 3) | (self.red >> 2),
            green=(self.green << 3) | (self.green >> 2),
            blue=(self.blue << 3) | (self.blue >> 2),
        )

    def to_15bit(self) -> int:
        """
        Convert to 15-bit integer representation.

        Format: 0BBBBBGGGGGRRRRR

        Returns:
            16-bit integer (upper bit unused).
        """
        return (
            (self.red & 0x1F)
            | ((self.green & 0x1F) << 5)
            | ((self.blue & 0x1F) << 10)
        )

    def to_bytes(self) -> bytes:
        """
        Convert to little-endian 2-byte representation for GBA.

        Returns:
            Bytes object of length 2.
        """
        value = self.to_15bit()
        return value.to_bytes(2, byteorder="little")

    @staticmethod
    def from_15bit(value: int) -> "GbaColor":
        """
        Create a GbaColor from a 15-bit integer.

        Args:
            value: 15-bit color value.

        Returns:
            GbaColor instance.
        """
        red = value & 0x1F
        green = (value >> 5) & 0x1F
        blue = (value >> 10) & 0x1F

        return GbaColor(red=red, green=green, blue=blue)

    @staticmethod
    def _validate_channel(channel_name: str, value: int) -> None:
        """
        Validate a single 5-bit channel.

        Args:
            channel_name: Name of the channel.
            value: Channel value.

        Raises:
            ValueError: If invalid.
        """
        if not isinstance(value, int):
            raise ValueError(f"{channel_name} must be an integer.")

        if value < 0 or value > 31:
            raise ValueError(f"{channel_name} must be between 0 and 31.")
