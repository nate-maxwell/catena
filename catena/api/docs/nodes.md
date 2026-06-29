# Node API

This page describes the core building blocks re-exported by `catena.api` for
authoring custom nodes.

## `api.CatenaNode`

`CatenaNode` is the base class for all graph nodes.

Subclass it to define your node title, ports, field behavior, and evaluation
logic. The base class handles:

- port layout and resizing
- field promotion into input ports
- input collection from upstream nodes
- cached evaluation
- preview updates and node selection events

Numpy and cv2 are first class in Catena. Many variable types and function
signatures support numpy arrays.
Override `CatenaNode.process()` in your node class to produce the node output.
The full signature is:

`process(self, inputs: dict[str, Optional[numpy.ndarray]]) -> Optional[numpy.ndarray]`.

The keys in `inputs` match the names of the node's input ports.

## `api.Port`

`Port` is a connection point on a node.

Use ports to connect nodes together in the graph. Ports are created through
`CatenaNode.add_port(...)` and are positioned automatically on the left or
right side of the node depending on their direction.

## `api.PortType`

`PortType` identifies whether a port is an input or an output.

The node API uses:

- `PortType.INPUT`
- `PortType.OUTPUT`

## `api.PortDataType`

`PortDataType` defines the logical data carried by a port.

The available values are:

- `FLOAT`
- `BOOL`
- `INT`
- `VECTOR1`
- `VECTOR2`
- `VECTOR3`
- `VECTOR4`
- `NORMAL`
- `FLOOD_FILL`

These values are used for port compatibility, port coloring, and mapping fields
to ports.

## `api.FieldDefinition`

`FieldDefinition` describes a field exposed by a node.

It provides the metadata used by the properties pane and by field promotion in
`CatenaNode`. Field definitions describe the field name, its type, and the
default/value constraints for that field.

## `api.FieldType`

`FieldType` identifies the kind of field a node exposes.

The node API uses the field types supported by the underlying node toolkit,
including:

- `INT`
- `FLOAT`
- `COLOR`
- `VEC2`
- `VEC3`
- `STR`
- `BOOL`
- `CHOICE`

## `api.DATA_TYPE_COLORS`

`DATA_TYPE_COLORS` maps each `PortDataType` to a display color.

The UI uses this to tint ports so compatible data types are easy to recognize
in the graph editor.

## `api.FIELD_PORT_DATA_TYPES`

`FIELD_PORT_DATA_TYPES` maps `FieldType` values to the port data type used when
a field is promoted into an input port.

This is what lets a field keep a sensible port representation when it accepts
upstream data instead of a fixed value.

## `api.TEXTURE_DATA_TYPES`

`TEXTURE_DATA_TYPES` maps texture semantic types to `PortDataType` values.

Use this when a node works with named texture slots and needs to declare the
data type associated with each slot.

## Example node

The example below defines a simple pass-through node with one input and one
output. It copies the upstream value from `Image In` to `Image Out`.

```python
import numpy
from catena import api


class PassThroughNode(api.CatenaNode):
    def __init__(self) -> None:
        super().__init__("Pass Through")
        self.add_port(api.PortType.INPUT, "Image In", api.PortDataType.VECTOR4)
        self.add_port(api.PortType.OUTPUT, "Image Out", api.PortDataType.VECTOR4)

    def process(
        self, inputs: dict[str, numpy.ndarray | None]
    ) -> numpy.ndarray | None:
        # "Image In" matches the input port name.
        return inputs["Image In"]


api.register_node("Utility", PassThroughNode)
```
