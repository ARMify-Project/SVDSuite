from svdsuite.process import Process
from svdsuite.model.map import MapPeripheral, MapRegister
from svdsuite.model.process import Device, Peripheral, Cluster, Register, AddressBlock


class PeripheralRegisterMap:
    @classmethod
    def from_svd_file(cls, path: str, resolver_logging_file_path: None | str = None):
        return cls(Process.from_svd_file(path, resolver_logging_file_path).get_processed_device())

    @classmethod
    def from_xml_str(cls, xml_str: str, resolver_logging_file_path: None | str = None):
        return cls(Process.from_xml_content(xml_str.encode(), resolver_logging_file_path).get_processed_device())

    @classmethod
    def from_xml_content(cls, content: bytes, resolver_logging_file_path: None | str = None):
        return cls(Process.from_xml_content(content, resolver_logging_file_path).get_processed_device())

    def __init__(self, processed_device: Device) -> None:
        self.peripheral_map = self._build_map(processed_device)

    def _build_map(self, processed_device: Device) -> list[MapPeripheral]:
        peripheral_map_list: list[MapPeripheral] = []
        for peripheral in processed_device.peripherals:
            map_peripheral = self._build_map_peripheral(peripheral)
            peripheral_map_list.append(map_peripheral)

        peripheral_map_list.sort(key=lambda x: x.address)
        return peripheral_map_list

    def _build_map_peripheral(self, peripheral: Peripheral) -> MapPeripheral:
        registers: list[MapRegister] = []
        for register_cluster in peripheral.registers_clusters:
            if isinstance(register_cluster, Register):
                registers.append(self._build_map_register(peripheral.base_address, register_cluster))
            if isinstance(register_cluster, Cluster):
                registers.extend(self._build_map_cluster(peripheral.base_address, register_cluster))

        map_peripheral = MapPeripheral(
            name=peripheral.name,
            description=peripheral.description,
            address=peripheral.base_address,
            allocated_range=self._get_allocated_range(peripheral.base_address, peripheral.address_blocks),
            registers=registers,
            processed=peripheral,
        )
        return map_peripheral

    def _build_map_register(self, container_address: int, register: Register) -> MapRegister:
        address = container_address + register.address_offset

        map_register = MapRegister(
            size=register.size,
            access=register.access,
            protection=register.protection,
            reset_value=register.reset_value,
            reset_mask=register.reset_mask,
            name=register.name,
            display_name=register.display_name,
            description=register.description,
            address=address,
            fields=register.fields,
            processed=register,
        )

        return map_register

    def _build_map_cluster(self, container_address: int, cluster: Cluster) -> list[MapRegister]:
        address = container_address + cluster.address_offset

        registers: list[MapRegister] = []
        for register_cluster in cluster.registers_clusters:
            if isinstance(register_cluster, Register):
                registers.append(self._build_map_register(address, register_cluster))
            if isinstance(register_cluster, Cluster):
                registers.extend(self._build_map_cluster(address, register_cluster))

        return registers

    def _get_allocated_range(self, start_address: int, address_blocks: list[AddressBlock]) -> tuple[int, int]:
        address_blocks = sorted(address_blocks, key=lambda x: x.offset)

        if not address_blocks:
            raise ValueError("Address blocks are empty")

        begin = start_address + address_blocks[0].offset
        end = start_address + address_blocks[-1].offset + address_blocks[-1].size - 1

        return (begin, end)
