from typing import Union

from ..components.allocation_managers.allocation_manager import MemoryFlag
from .patch import Patch
from .raw_patches import ModifyRawBytesPatch


class ModifyDataPatch(ModifyRawBytesPatch):
    """
    Extends ModifyRawBytesPatch to only be used for memory addresses, used for modifying data in binary.
    """

    def __init__(self, addr: int, new_bytes: bytes) -> None:
        """
        Same as ModifyRawBytesPatch constructor, but address type of memory is assumed.
        """
        super().__init__(addr, new_bytes, addr_type="mem")


class InsertDataPatch(Patch):
    """
    Patch that inserts data into the binary.
    """

    def __init__(self, addr_or_name: Union[int, str], data: bytes) -> None:
        """
        Constructor.

        :param addr_or_name: If an integer, data is inserted at the address.
                             If a string, it is placed in a free spot in the binary and added as a symbol (with this as its name).
        :type addr_or_name: Union[int, str]
        :param data: New data to place in binary.
        :type data: bytes
        """
        self.addr = None
        self.name = None
        if isinstance(addr_or_name, int):
            self.addr = addr_or_name
        elif isinstance(addr_or_name, str):
            self.name = addr_or_name
        self.data = data

    def apply(self, p) -> None:
        """
        Applies the patch to the binary, intended to be called by a Patcherex instance.

        :param p: Patcherex instance.
        :type p: Patcherex
        """
        if self.addr:
            p.binfmt_tool.update_binary_content(self.addr, self.data)
        elif self.name:
            block = p.allocation_manager.allocate(
                len(self.data), flag=MemoryFlag.RWX
            )  # FIXME: why RW not work?
            p.symbols[self.name] = block.mem_addr
            p.binfmt_tool.update_binary_content(block.file_addr, self.data)


class RemoveDataPatch(ModifyRawBytesPatch):
    """
    Extends ModifyRawBytesPatch for removing data in the binary (fills it with null bytes starting at address given).
    Expects a memory address.
    """

    def __init__(self, addr: int, size: int) -> None:
        """
        Same as ModifyRawBytes Patch constructor, but adds size parameter and assumes memory address.

        :param size: The number of bytes to remove.
        :type size: int
        """
        super().__init__(addr, b"\x00" * size, addr_type="mem")
