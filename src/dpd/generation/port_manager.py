from typing import Dict, List
from dpd.enums import ServiceType

__CONF_PORT2SERVICE__ = {
    ServiceType.POSTGRESQL: list(range(5432, 6432)),
    ServiceType.MINIO: list(range(9000, 9010)),
    ServiceType.KAFKA_UI: list(range(8080, 8083)),
    ServiceType.CLICKHOUSE: list(range(1230, 1234)),
}


class PortManager:
    def __init__(self):
        self.__port2serivice = {}
        self.__conf: Dict[ServiceType, List[int]] = __CONF_PORT2SERVICE__

    def add_port(self, service_id: str, service_type: ServiceType) -> int:
        port = self.__conf[service_type].pop(0)
        self.__port2serivice[port] = service_id
        return port
    
port_manager= PortManager()
