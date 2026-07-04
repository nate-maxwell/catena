# Texture Helpers

The texture helpers wrap Catena's internal array and image conversion logic so
plugins can work with image data without importing internal modules directly.

## `api.ndarray_to_qimage`

```python
ndarray_to_qimage(image: numpy.ndarray) -> QtGui.QImage
```

Converts a `numpy` array into a Qt image object.

Use this when a plugin has generated image data in array form and needs to
display it in a Qt-based preview or widget.

## `api.create_texture_from_array`

```python
create_texture_from_array(
    image: numpy.ndarray,
    srgb: bool,
    invert_green_after_flip: bool = False,
) -> int
```

Creates a Catena texture object from a `numpy` array.

This is the normal handoff point when plugin code already has processed image
data and needs to pass it into Catena's texture pipeline.

## `api.resize_like`

```python
resize_like(source: numpy.ndarray, reference: numpy.ndarray) -> numpy.ndarray
```

Resizes one array to match another array's height and width.

This is useful in node code when two inputs need to be aligned before a
per-pixel operation. The helper preserves a trailing singleton channel on
1-channel arrays so scalar-like data still broadcasts cleanly against vector
images.

## `api.bgr_to_rgb`

```python
bgr_to_rgb(image: numpy.ndarray) -> numpy.ndarray
```

Converts channel order from BGR to RGB.

## `api.rgb_to_bgr`

```python
rgb_to_bgr(image: numpy.ndarray) -> numpy.ndarray
```

Converts channel order from RGB to BGR.

## `api.bgra_to_rgba`

```python
bgra_to_rgba(image: numpy.ndarray) -> numpy.ndarray
```

Converts channel order from BGRA to RGBA.

## `api.rgba_to_bgra`

```python
rgba_to_bgra(image: numpy.ndarray) -> numpy.ndarray
```

Converts channel order from RGBA to BGRA.

## `api.TextureType`

```python
TextureType
```

Re-exports the texture type enum used by Catena's internal texture code.

## Behavior notes

OpenCV uses BGR/BGRA ordering by default, while Qt and much of Catena's UI
expect RGB/RGBA ordering. These helpers keep those conversions in one place.
