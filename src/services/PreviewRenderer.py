"""
Preview rendering service for the GBA Tile Quantizer.
"""
from __future__ import annotations
from PIL import Image

from domain.Palette import Palette
from domain.PaletteSet import PaletteSet
from domain.Tile import Tile
from domain.TileMap import TileMap
from domain.TileSet import TileSet


class PreviewRenderer:
    """
    Service responsible for rendering preview images from tileset and tilemap data.
    """

    def render_tileset(
        self,
        tileset: TileSet,
        palette_set: PaletteSet,
        tilemap: TileMap | None = None,
        tiles_per_row: int = 16,
        tile_width: int = 8,
        tile_height: int = 8,
    ) -> Image.Image:
        """
        Render a TileSet into a tilesheet preview image.

        Args:
            tileset: TileSet to render.
            palette_set: Palette banks used to convert indices into RGB values.
            tilemap: Optional tilemap used to infer a representative bank per tile.
            tiles_per_row: Number of tiles per row in the preview sheet.
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Returns:
            A Pillow RGB image containing the rendered tileset.

        Raises:
            ValueError: If inputs are invalid.
        """
        if tileset is None:
            raise ValueError("tileset cannot be None.")

        if palette_set is None:
            raise ValueError("palette_set cannot be None.")

        if tiles_per_row <= 0:
            raise ValueError("tiles_per_row must be greater than 0.")

        if tile_width <= 0:
            raise ValueError("tile_width must be greater than 0.")

        if tile_height <= 0:
            raise ValueError("tile_height must be greater than 0.")

        tile_count = tileset.size()

        if tile_count == 0:
            return Image.new("RGB", (tile_width, tile_height), (0, 0, 0))

        row_count = (tile_count + tiles_per_row - 1) // tiles_per_row
        image_width = tiles_per_row * tile_width
        image_height = row_count * tile_height

        image = Image.new("RGB", (image_width, image_height), (0, 0, 0))
        pixel_access = image.load()
        tileset_palette_bank_map = self._build_tileset_palette_bank_map(
            tilemap=tilemap,
            tileset_size=tileset.size(),
        )

        for tile_index, tile in enumerate(tileset.tiles):
            tile_x = tile_index % tiles_per_row
            tile_y = tile_index // tiles_per_row

            destination_x = tile_x * tile_width
            destination_y = tile_y * tile_height

            self._draw_tile(
                pixel_access=pixel_access,
                tile=tile,
                palette=palette_set.get_palette(tileset_palette_bank_map[tile_index]),
                destination_x=destination_x,
                destination_y=destination_y,
            )

        return image

    def render_tilemap(
        self,
        tilemap: TileMap,
        tileset: TileSet,
        palette_set: PaletteSet,
        tile_width: int = 8,
        tile_height: int = 8,
    ) -> Image.Image:
        """
        Render a TileMap using the supplied TileSet and Palette.

        Args:
            tilemap: TileMap to render.
            tileset: TileSet referenced by the map.
            palette_set: Palette banks used to convert indices into RGB values.
            tile_width: Tile width in pixels.
            tile_height: Tile height in pixels.

        Returns:
            A Pillow RGB image representing the reconstructed tilemap.

        Raises:
            ValueError: If inputs are invalid.
        """
        if tilemap is None:
            raise ValueError("tilemap cannot be None.")

        if tileset is None:
            raise ValueError("tileset cannot be None.")

        if palette_set is None:
            raise ValueError("palette_set cannot be None.")

        image_width = tilemap.width * tile_width
        image_height = tilemap.height * tile_height

        image = Image.new("RGB", (image_width, image_height), (0, 0, 0))
        pixel_access = image.load()

        for map_y in range(tilemap.height):
            for map_x in range(tilemap.width):
                entry = tilemap.get_entry(map_x, map_y)
                tile = tileset.get_tile(entry.tile_index)

                if entry.horizontal_flip and entry.vertical_flip:
                    tile = tile.flipped_horizontal_vertical()
                elif entry.horizontal_flip:
                    tile = tile.flipped_horizontal()
                elif entry.vertical_flip:
                    tile = tile.flipped_vertical()

                destination_x = map_x * tile_width
                destination_y = map_y * tile_height

                self._draw_tile(
                    pixel_access=pixel_access,
                    tile=tile,
                    palette=palette_set.get_palette(entry.palette_bank),
                    destination_x=destination_x,
                    destination_y=destination_y,
                )

        return image

    def render_tileset_to_png_bytes(
        self,
        tileset: TileSet,
        palette_set: PaletteSet,
        tilemap: TileMap | None = None,
        tiles_per_row: int = 16,
    ) -> bytes:
        """
        Render a TileSet preview and encode it as PNG bytes.

        Args:
            tileset: TileSet to render.
            palette_set: Palette banks used for RGB conversion.
            tilemap: Optional tilemap used to infer a representative bank per tile.
            tiles_per_row: Number of tiles per row.

        Returns:
            PNG-encoded bytes.
        """
        image = self.render_tileset(
            tileset=tileset,
            palette_set=palette_set,
            tilemap=tilemap,
            tiles_per_row=tiles_per_row,
        )
        return self._image_to_png_bytes(image)

    def render_tilemap_to_png_bytes(
        self,
        tilemap: TileMap,
        tileset: TileSet,
        palette_set: PaletteSet,
    ) -> bytes:
        """
        Render a TileMap preview and encode it as PNG bytes.

        Args:
            tilemap: TileMap to render.
            tileset: TileSet referenced by the map.
            palette_set: Palette banks used for RGB conversion.

        Returns:
            PNG-encoded bytes.
        """
        image = self.render_tilemap(
            tilemap=tilemap,
            tileset=tileset,
            palette_set=palette_set,
        )
        return self._image_to_png_bytes(image)

    def _draw_tile(
        self,
        pixel_access,
        tile: Tile,
        palette: Palette,
        destination_x: int,
        destination_y: int,
    ) -> None:
        """
        Draw a tile into a destination image.

        Args:
            pixel_access: Pillow pixel access object.
            tile: Tile to draw.
            palette: Palette used to convert indices into RGB values.
            destination_x: Destination X position in pixels.
            destination_y: Destination Y position in pixels.
        """
        for local_y in range(8):
            for local_x in range(8):
                palette_index = tile.get_pixel(local_x, local_y)
                rgb_color = palette.get_color(palette_index)
                pixel_access[destination_x + local_x, destination_y + local_y] = rgb_color

    def _build_tileset_palette_bank_map(
        self,
        tilemap: TileMap | None,
        tileset_size: int,
    ) -> dict[int, int]:
        """
        Build a representative palette bank lookup for each tile in the tileset.
        """
        palette_bank_map = {tile_index: 0 for tile_index in range(tileset_size)}

        if tilemap is None:
            return palette_bank_map

        for entry in tilemap.entries:
            palette_bank_map.setdefault(entry.tile_index, entry.palette_bank)

        return palette_bank_map

    def _image_to_png_bytes(self, image: Image.Image) -> bytes:
        """
        Encode a Pillow image into PNG bytes.

        Args:
            image: Image to encode.

        Returns:
            PNG-encoded bytes.
        """
        from io import BytesIO

        output_stream = BytesIO()
        image.save(output_stream, format="PNG")
        return output_stream.getvalue()
