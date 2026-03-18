"""
Palette quantization service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from PIL import Image

from config.QuantizationConfig import QuantizationConfig
from domain.IndexedImage import IndexedImage
from domain.Palette import Palette


class PaletteQuantizer:
    """
    Service responsible for converting an RGB image into an indexed image
    using a single global palette.
    """

    def quantize(self, image: Image.Image, config: QuantizationConfig) -> IndexedImage:
        """
        Quantize an RGB image into an indexed image with a global palette.

        Args:
            image: Source Pillow image.
            config: Quantization configuration.

        Returns:
            An IndexedImage containing palette indices and a Palette.

        Raises:
            ValueError: If the image or configuration is invalid.
        """
        if image is None:
            raise ValueError("image cannot be None.")

        config.validate()

        rgb_image = self._ensure_rgb(image)
        indexed_pillow_image = self._quantize_image(rgb_image, config)

        palette, remapped_pixels = self._extract_palette_and_remap_pixels(
            indexed_pillow_image,
            config.max_colors,
        )

        return IndexedImage(
            width=indexed_pillow_image.width,
            height=indexed_pillow_image.height,
            palette=palette,
            pixels=remapped_pixels,
        )

    def _ensure_rgb(self, image: Image.Image) -> Image.Image:
        """
        Ensure the image is in RGB mode.

        Args:
            image: Source Pillow image.

        Returns:
            An RGB Pillow image.
        """
        if image.mode == "RGB":
            return image

        return image.convert("RGB")

    def _quantize_image(self, image: Image.Image, config: QuantizationConfig) -> Image.Image:
        """
        Quantize an RGB image using Pillow.

        Args:
            image: RGB Pillow image.
            config: Quantization configuration.

        Returns:
            A Pillow image in indexed ('P') mode.

        Raises:
            ValueError: If the quantization method is unsupported.
        """
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
            colors=config.max_colors,
            method=method,
            dither=dither_mode,
        )

    def _extract_palette_and_remap_pixels(self, indexed_image: Image.Image, max_colors: int, ) -> tuple[Palette, list[int]]:
        """
        Extract the used palette entries and remap pixel indices into a compact range.

        Args:
            indexed_image: Pillow image in indexed ('P') mode.
            max_colors: Maximum number of colors expected.

        Returns:
            A tuple containing:
            - Palette: the compacted palette
            - list[int]: remapped pixel indices

        Raises:
            ValueError: If the image does not contain a valid palette.
        """
        raw_palette = indexed_image.getpalette()

        if raw_palette is None:
            raise ValueError("Indexed image does not contain a palette.")

        original_pixels = list(indexed_image.getdata())
        used_indices = sorted(set(original_pixels))

        colors: list[tuple[int, int, int]] = []
        index_remap: dict[int, int] = {}

        for new_index, old_index in enumerate(used_indices):
            base_offset = old_index * 3

            red = raw_palette[base_offset]
            green = raw_palette[base_offset + 1]
            blue = raw_palette[base_offset + 2]

            colors.append((red, green, blue))
            index_remap[old_index] = new_index

        if len(colors) > max_colors:
            raise ValueError(
                f"Extracted palette contains {len(colors)} colors, "
                f"which exceeds the maximum of {max_colors}."
            )

        remapped_pixels = [index_remap[pixel] for pixel in original_pixels]

        return Palette(colors), remapped_pixels
