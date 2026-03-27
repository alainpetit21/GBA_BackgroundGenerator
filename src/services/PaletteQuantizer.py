"""
Palette quantization service for the GBA Tile Quantizer.
"""
from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from config.QuantizationConfig import QuantizationConfig
from domain.Palette import Palette
from domain.PaletteSet import PaletteSet
from domain.Tile import Tile
from domain.TileMap import TileMap


@dataclass
class QuantizedTileImage:
    """
    Tile-oriented quantization result using palette banks.
    """

    image_width: int
    image_height: int
    palette_set: PaletteSet
    tiles: list[Tile]
    tilemap: TileMap


class PaletteQuantizer:
    """
    Quantize an image into 4bpp tiles assigned to a limited set of palette banks.
    """

    def quantize(self, image: Image.Image, config: QuantizationConfig) -> QuantizedTileImage:
        """
        Quantize an RGB image into banked 4bpp tiles.
        """
        if image is None:
            raise ValueError("image cannot be None.")

        config.validate()

        rgb_image = self._ensure_rgb(image)

        if rgb_image.width % config.tile_width != 0:
            raise ValueError("Quantized image width must be tile-aligned.")

        if rgb_image.height % config.tile_height != 0:
            raise ValueError("Quantized image height must be tile-aligned.")

        map_width = rgb_image.width // config.tile_width
        map_height = rgb_image.height // config.tile_height
        palette_banks: list[Palette] = []
        tiles: list[Tile] = []
        tilemap = TileMap(width=map_width, height=map_height)

        tile_index = 0
        for tile_y in range(map_height):
            for tile_x in range(map_width):
                tile_image = rgb_image.crop(
                    (
                        tile_x * config.tile_width,
                        tile_y * config.tile_height,
                        (tile_x + 1) * config.tile_width,
                        (tile_y + 1) * config.tile_height,
                    )
                )
                indexed_tile_image = self._quantize_image(tile_image, config, 16)
                tile_palette, tile_pixels = self._extract_palette_and_remap_pixels(
                    indexed_tile_image,
                    16,
                )
                palette_bank, remapped_pixels = self._assign_palette_bank(
                    tile_palette,
                    tile_pixels,
                    palette_banks,
                    config.palette_bank_count,
                )

                tiles.append(Tile(tuple(remapped_pixels)))
                tilemap.set_tile_index(
                    tile_x,
                    tile_y,
                    tile_index,
                    palette_bank=palette_bank,
                )
                tile_index += 1

        return QuantizedTileImage(
            image_width=rgb_image.width,
            image_height=rgb_image.height,
            palette_set=PaletteSet(palettes=palette_banks),
            tiles=tiles,
            tilemap=tilemap,
        )

    def _ensure_rgb(self, image: Image.Image) -> Image.Image:
        if image.mode == "RGB":
            return image

        return image.convert("RGB")

    def _quantize_image(
        self,
        image: Image.Image,
        config: QuantizationConfig,
        color_count: int,
    ) -> Image.Image:
        dither_mode = Image.Dither.FLOYDSTEINBERG
        if not config.dithering_enabled:
            dither_mode = Image.Dither.NONE

        if config.quantization_method == "median_cut":
            method = Image.Quantize.MEDIANCUT
        elif config.quantization_method == "fast_octree":
            method = Image.Quantize.FASTOCTREE
        else:
            raise ValueError(
                f"Unsupported quantization method: {config.quantization_method}"
            )

        return image.quantize(
            colors=color_count,
            method=method,
            dither=dither_mode,
        )

    def _extract_palette_and_remap_pixels(
        self,
        indexed_image: Image.Image,
        max_colors: int,
    ) -> tuple[Palette, list[int]]:
        raw_palette = indexed_image.getpalette()

        if raw_palette is None:
            raise ValueError("Indexed image does not contain a palette.")

        original_pixels = list(indexed_image.getdata())
        used_indices = sorted(set(original_pixels))

        colors: list[tuple[int, int, int]] = []
        index_remap: dict[int, int] = {}

        for new_index, old_index in enumerate(used_indices):
            base_offset = old_index * 3
            colors.append(
                (
                    raw_palette[base_offset],
                    raw_palette[base_offset + 1],
                    raw_palette[base_offset + 2],
                )
            )
            index_remap[old_index] = new_index

        if len(colors) > max_colors:
            raise ValueError(
                f"Extracted palette contains {len(colors)} colors, "
                f"which exceeds the maximum of {max_colors}."
            )

        return Palette(colors), [index_remap[pixel] for pixel in original_pixels]

    def _assign_palette_bank(
        self,
        tile_palette: Palette,
        tile_pixels: list[int],
        palette_banks: list[Palette],
        max_palette_banks: int,
    ) -> tuple[int, list[int]]:
        merge_choice = self._find_mergeable_bank(tile_palette, palette_banks)
        if merge_choice is not None:
            bank_index, merged_palette = merge_choice
            palette_banks[bank_index] = merged_palette
            remapped_pixels = self._remap_tile_pixels_to_palette(
                tile_palette=tile_palette,
                tile_pixels=tile_pixels,
                target_palette=merged_palette,
            )
            return bank_index, remapped_pixels

        if len(palette_banks) < max_palette_banks:
            palette_banks.append(Palette(list(tile_palette.colors)))
            return len(palette_banks) - 1, list(tile_pixels)

        best_bank_index = self._find_best_matching_bank(tile_palette, palette_banks)
        best_palette = palette_banks[best_bank_index]
        remapped_pixels = self._remap_tile_pixels_to_palette(
            tile_palette=tile_palette,
            tile_pixels=tile_pixels,
            target_palette=best_palette,
        )
        return best_bank_index, remapped_pixels

    def _find_mergeable_bank(
        self,
        tile_palette: Palette,
        palette_banks: list[Palette],
    ) -> tuple[int, Palette] | None:
        best_bank_index: int | None = None
        best_palette: Palette | None = None
        best_growth: int | None = None

        for bank_index, palette_bank in enumerate(palette_banks):
            merged_colors = list(palette_bank.colors)

            for color in tile_palette.colors:
                if color not in merged_colors:
                    merged_colors.append(color)

            if len(merged_colors) > 16:
                continue

            growth = len(merged_colors) - palette_bank.size()
            if best_growth is None or growth < best_growth:
                best_bank_index = bank_index
                best_growth = growth
                best_palette = Palette(merged_colors)

        if best_bank_index is None or best_palette is None:
            return None

        return best_bank_index, best_palette

    def _find_best_matching_bank(
        self,
        tile_palette: Palette,
        palette_banks: list[Palette],
    ) -> int:
        if not palette_banks:
            raise ValueError("At least one palette bank is required.")

        best_bank_index = 0
        best_score = self._calculate_palette_mapping_score(
            tile_palette,
            palette_banks[0],
        )

        for bank_index in range(1, len(palette_banks)):
            score = self._calculate_palette_mapping_score(
                tile_palette,
                palette_banks[bank_index],
            )
            if score < best_score:
                best_bank_index = bank_index
                best_score = score

        return best_bank_index

    def _calculate_palette_mapping_score(
        self,
        source_palette: Palette,
        target_palette: Palette,
    ) -> int:
        score = 0
        for color in source_palette.colors:
            _, color_score = self._find_nearest_color_index(color, target_palette)
            score += color_score

        return score

    def _remap_tile_pixels_to_palette(
        self,
        tile_palette: Palette,
        tile_pixels: list[int],
        target_palette: Palette,
    ) -> list[int]:
        color_index_map: dict[tuple[int, int, int], int] = {}

        for color in tile_palette.colors:
            if color in color_index_map:
                continue

            if color in target_palette.colors:
                color_index_map[color] = target_palette.index_of(color)
            else:
                nearest_index, _ = self._find_nearest_color_index(color, target_palette)
                color_index_map[color] = nearest_index

        remapped_pixels: list[int] = []
        for palette_index in tile_pixels:
            color = tile_palette.get_color(palette_index)
            remapped_pixels.append(color_index_map[color])

        return remapped_pixels

    def _find_nearest_color_index(
        self,
        color: tuple[int, int, int],
        palette: Palette,
    ) -> tuple[int, int]:
        best_index = 0
        best_score = self._color_distance_squared(color, palette.get_color(0))

        for index in range(1, palette.size()):
            score = self._color_distance_squared(color, palette.get_color(index))
            if score < best_score:
                best_index = index
                best_score = score

        return best_index, best_score

    def _color_distance_squared(
        self,
        first_color: tuple[int, int, int],
        second_color: tuple[int, int, int],
    ) -> int:
        red_difference = first_color[0] - second_color[0]
        green_difference = first_color[1] - second_color[1]
        blue_difference = first_color[2] - second_color[2]

        return (
            (red_difference * red_difference)
            + (green_difference * green_difference)
            + (blue_difference * blue_difference)
        )
