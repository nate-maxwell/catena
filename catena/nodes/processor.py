from typing import Optional

import numpy


class ProcessorNode(object):
    """A headless node that can be connected to other ProcessorNodes."""

    def __init__(self) -> None:
        self._inputs: dict[str, Optional["ProcessorNode"]] = {}
        self._output_port: str = "Output"

    def connect(self, input_port: str, source: "ProcessorNode") -> None:
        """
        Connect another processor's output to one of this node's inputs.

        Args:
            input_port (str): The name of the input port on this node.
            source (ProcessorNode): The upstream processor node.
        """
        self._inputs[input_port] = source

    def disconnect(self, input_port: str) -> None:
        """
        Disconnect a specific input port.

        Args:
            input_port (str): The name of the input port to disconnect.
        """
        self._inputs.pop(input_port, None)

    def evaluate(self) -> Optional[numpy.ndarray]:
        """
        Recursively evaluate this node and all upstream nodes.

        Returns:
            numpy.ndarray | None: The processed output of this node.
        """
        inputs = {
            name: node.evaluate() if node is not None else None
            for name, node in self._inputs.items()
        }
        return self.process(inputs)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray]:
        """
        Override in subclasses to implement processing logic.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Evaluated images keyed
                by input port name.
        Returns:
            numpy.ndarray | None: The processed output.
        """
        raise NotImplementedError
