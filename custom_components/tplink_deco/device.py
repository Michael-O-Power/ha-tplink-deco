"""TP-Link Deco."""

from homeassistant.const import ATTR_VIA_DEVICE
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN
from .coordinator import TpLinkDeco


def _get_mac_offsets(mac: str) -> list[str]:
    """Calculate adjacent MAC addresses in the device's contiguous block."""
    offsets = []
    try:
        mac_int = int(mac.replace("-", "").replace(":", ""), 16)
        # TP-Link assigns a block of MACs for Wi-Fi radios and Ethernet ports.
        # Exposing +1, +2, and -1 ensures Home Assistant catches the physical interface.
        for offset in [-1, 1, 2]:
            offsets.append(":".join(f"{(mac_int + offset):012x}"[i:i+2] for i in range(0, 12, 2)))
    except Exception:
        pass
    return offsets


def create_device_info(deco: TpLinkDeco, master_deco: TpLinkDeco) -> DeviceInfo:
    """Return device info."""
    if deco is None:
        return None
        
    formatted_primary_mac = dr.format_mac(deco.mac)
    
    # Create a set containing the primary MAC
    device_connections = {
        (dr.CONNECTION_NETWORK_MAC, formatted_primary_mac)
    }
    
    # Add the adjacent MAC addresses to the set
    for offset_mac in _get_mac_offsets(deco.mac):
        formatted_offset = dr.format_mac(offset_mac)
        if formatted_offset:
            device_connections.add((dr.CONNECTION_NETWORK_MAC, formatted_offset))

    device_info = DeviceInfo(
        identifiers={(DOMAIN, deco.mac)},
        connections=device_connections,
        name=f"{deco.name} Deco",
        manufacturer="TP-Link Deco",
        model=deco.device_model,
        sw_version=deco.sw_version,
        hw_version=deco.hw_version,
    )
    
    if master_deco is not None and deco != master_deco:
        device_info[ATTR_VIA_DEVICE] = (DOMAIN, master_deco.mac)

    return device_info
    
