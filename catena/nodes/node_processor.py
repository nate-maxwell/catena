from __future__ import annotations

from typing import Optional

import numpy


class ProcessorNode(object):
    """
    A headless node that can be connected to other ProcessorNodes to form
    a processing graph without any Qt or GUI dependency.

    Subclasses override ``process`` to implement their computation logic.
    Connections are tracked on the input side — each node knows its upstream
    sources, not its downstream consumers.

    Class Attributes:
        input_port_names (list[str]): Ordered list of input port names,
            matching the order ports are declared in the corresponding
            CatenaNode subclass's ``_build`` method. Used by
            ``ProcessorGraph`` to resolve serialized port indices to names.
        output_port_names (list[str]): Ordered list of output port names,
            matching the order output ports are declared in ``_build``.
    """

    input_port_names: list[str] = []
    output_port_names: list[str] = []

    def __init__(self) -> None:
        self._inputs: dict[str, tuple[ProcessorNode, str]] = {}

    def connect(
        self,
        input_port: str,
        source: ProcessorNode,
        source_port: str = "Output",
    ) -> None:
        """
        Connect an upstream processor's output to one of this node's inputs.

        Args:
            input_port (str): The name of the input port on this node.
            source (ProcessorNode): The upstream processor node.
            source_port (str): The name of the output port on the upstream
                node to read from. Defaults to "Output" for single-output
                nodes.
        """
        self._inputs[input_port] = (source, source_port)

    def disconnect(self, input_port: str) -> None:
        """
        Disconnect a specific input port.

        Args:
            input_port (str): The name of the input port to disconnect.
        """
        self._inputs.pop(input_port, None)

    def disconnect_all(self) -> None:
        """Disconnect all input ports on this node."""
        self._inputs.clear()

    def is_connected(self, input_port: str) -> bool:
        """
        Return whether a specific input port has a connected upstream node.

        Args:
            input_port (str): The name of the input port to check.
        Returns:
            bool: True if the port has an upstream connection.
        """
        return input_port in self._inputs

    def evaluate(self) -> Optional[numpy.ndarray] | dict[str, Optional[numpy.ndarray]]:
        """
        Recursively evaluate this node by pulling from all upstream inputs.

        For each connected input port, the upstream node is evaluated and
        its result is resolved by output port name. Multi-output nodes
        (those whose ``evaluate`` returns a dict) are keyed by the
        ``source_port`` name specified at connection time.

        Returns:
            numpy.ndarray | dict | None: The result of ``process``. Most
                nodes return a single float32 ndarray. Multi-output nodes
                (e.g. SplitProcessor) return a dict keyed by output port name.
        """
        inputs: dict[str, Optional[numpy.ndarray]] = {}

        for port_name, (source_node, source_port) in self._inputs.items():
            result = source_node.evaluate()
            if isinstance(result, dict):
                inputs[port_name] = result.get(source_port)
            else:
                inputs[port_name] = result

        return self.process(inputs)

    def process(
        self, inputs: dict[str, Optional[numpy.ndarray]]
    ) -> Optional[numpy.ndarray] | dict[str, Optional[numpy.ndarray]]:
        """
        Override in subclasses to implement processing logic.

        Called by ``evaluate`` with all upstream inputs already resolved.
        The base implementation returns None.

        Args:
            inputs (dict[str, numpy.ndarray | None]): Evaluated images keyed
                by input port name. Unconnected ports will not appear in this
                dict unless explicitly set to None by the caller.
        Returns:
            numpy.ndarray | dict | None: The processed output. Return a plain
                ndarray for single-output nodes, or a dict keyed by output
                port name for multi-output nodes (e.g. SplitProcessor).
        """
        return None

    def upstream_nodes(self) -> list[ProcessorNode]:
        """
        Return all directly connected upstream processor nodes.

        Returns:
            list[ProcessorNode]: The upstream nodes feeding into this node's
                input ports.
        """
        return [source for source, _ in self._inputs.values()]

    def __repr__(self) -> str:
        connected = list(self._inputs.keys())
        return f"{self.__class__.__name__}(inputs={connected})"
