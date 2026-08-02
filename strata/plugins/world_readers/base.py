from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterator, Optional

from ...pipeline_state import Block


class WorldReader(ABC):
    """Every world-format plugin (anvil, litematica, ...) implements this."""

    @abstractmethod
    def read_blocks(
        self, world_path: str, y_min: Optional[int] = None, y_max: Optional[int] = None
    ) -> Iterator[Block]:
        """Yields (x, y, z, block_id) for every non-air block. No culling here
        -- that's Stage 4's job (strata/culling.py), so every reader's output
        is comparable regardless of format."""
        raise NotImplementedError
