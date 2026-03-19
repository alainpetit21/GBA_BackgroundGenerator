"""
GBA binary encoding service for the GBA Tile Quantizer.
"""
from __future__ import annotations

from domain.Palette import Palette
from domain.TileMap import TileMap
from domain.TileSet import TileSet


class GbaBinaryEncoder:
    """
    Service responsible for encoding domain objects into GBA binary formats.
    """

    def encode_palette_4bpp(self, palette: Palette, pad_to_16: bool = True) -> bytes:
        """
        Encode a palette into GBA little-endian 15-bit color data.

        Args:
            palette: Palette to encode.
            pad_to_16: Whether to pad the palette to exactly 16 colors.

        Returns:
            Palette binary data.

        Raises:
            ValueError: If palette is None.
        """
        if palette is None:
            raise ValueError("palette cannot be None.")

        if pad_to_16:
            return palette.padded_to_16_colors().to_binary()

        return palette.to_binary()

    def encode_tileset_4bpp(self, tileset: TileSet) -> bytes:
        """
        Encode a tileset into concatenated GBA 4bpp tile data.

        Args:
            tileset: TileSet to encode.

        Returns:
            Tile binary data.

        Raises:
            ValueError: If tileset is None.
        """
        if tileset is None:
            raise ValueError("tileset cannot be None.")

        return tileset.to_4bpp_binary()

    def encode_text_bg_map(
        self,
        tilemap: TileMap,
        palette_bank: int = 0,
    ) -> bytes:
        """
        Encode a TileMap into GBA text background map entries.

        Entry layout:
        - bits 0-9   = tile index
        - bit 10     = horizontal flip
        - bit 11     = vertical flip
        - bits 12-15 = palette bank

        Args:
            tilemap: TileMap to encode.
            palette_bank: Palette bank value in the range 0..15.

        Returns:
            Tile map binary data as little-endian 16-bit entries.

        Raises:
            ValueError: If tilemap is None or palette_bank is invalid.
        """
        if tilemap is None:
            raise ValueError("tilemap cannot be None.")

        if palette_bank < 0 or palette_bank > 15:
            raise ValueError("palette_bank must be between 0 and 15.")

        output = bytearray()

        for entry in tilemap.entries:
            map_value = self._encode_text_bg_map_entry(
                tile_index=entry.tile_index,
                horizontal_flip=entry.horizontal_flip,
                vertical_flip=entry.vertical_flip,
                palette_bank=palette_bank,
            )
            output.extend(map_value.to_bytes(2, byteorder="little", signed=False))

        return bytes(output)

    def _encode_text_bg_map_entry(
        self,
        tile_index: int,
        horizontal_flip: bool,
        vertical_flip: bool,
        palette_bank: int,
    ) -> int:
        """
        Encode a single GBA text background map entry.

        Args:
            tile_index: Tile index in the range 0..1023.
            horizontal_flip: Horizontal flip flag.
            vertical_flip: Vertical flip flag.
            palette_bank: Palette bank in the range 0..15.

        Returns:
            Encoded 16-bit map entry value.

        Raises:
            ValueError: If any field is out of range.
        """
        if tile_index < 0 or tile_index > 1023:
            raise ValueError("tile_index must be between 0 and 1023.")

        if palette_bank < 0 or palette_bank > 15:
            raise ValueError("palette_bank must be between 0 and 15.")

        encoded_value = tile_index

        if horizontal_flip:
            encoded_value |= 1 << 10

        if vertical_flip:
            encoded_value |= 1 << 11

        encoded_value |= palette_bank << 12

        return encoded_value
