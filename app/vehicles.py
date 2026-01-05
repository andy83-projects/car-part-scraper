"""Vehicle configurations for searching"""
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class VehicleConfig:
    """Vehicle configuration"""
    name: str
    year: int
    make: str
    model: str
    engine: str
    part_type: str = "Cylinder Head"
    
    
# 4G63 DOHC configurations
VEHICLE_4G63 = [
    VehicleConfig(
        name="4G63 Early (90-94)",
        year=1992,
        make="Mitsubishi",
        model="Eclipse",
        engine="2.0L"
    ),
    VehicleConfig(
        name="4G63 Late (95-99)",
        year=1997,
        make="Mitsubishi",
        model="Eclipse",
        engine="2.0L"
    ),
    VehicleConfig(
        name="4G63 EVO (97-06)",
        year=2003,
        make="Mitsubishi",
        model="Lancer",
        engine="2.0L"
    ),
]

# G4JS DOHC configurations
VEHICLE_G4JS = [
    VehicleConfig(
        name="G4JS Tiburon (01-05)",
        year=2003,
        make="Hyundai",
        model="Tiburon",
        engine="2.0L"
    ),
    VehicleConfig(
        name="G4JS Elantra GT (02-06)",
        year=2004,
        make="Hyundai",
        model="Elantra",
        engine="2.0L"
    ),
    VehicleConfig(
        name="G4JS Tiburon SE (03-08)",
        year=2006,
        make="Hyundai",
        model="Tiburon",
        engine="2.0L"
    ),
    VehicleConfig(
        name="G4JS Spectra5 (05-10)",
        year=2007,
        make="Kia",
        model="Spectra5",
        engine="2.0L"
    ),
]

# Hyundai 2.0L DOHC configurations
VEHICLE_HYUNDAI_2L = [
    VehicleConfig(
        name="Hyundai Sonata 2.0L (92-98)",
        year=1995,
        make="Hyundai",
        model="Sonata",
        engine="2.0L"
    ),
    VehicleConfig(
        name="Hyundai Grandeur 2.0L (88-92)",
        year=1990,
        make="Hyundai",
        model="Grandeur",
        engine="2.0L"
    ),
    VehicleConfig(
        name="Hyundai Santamo 2.0L (97-02)",
        year=1999,
        make="Hyundai",
        model="Santamo",
        engine="2.0L"
    ),
    VehicleConfig(
        name="Hyundai Scoupe 2.0L (91-95)",
        year=1993,
        make="Hyundai",
        model="Scoupe",
        engine="2.0L"
    ),
]

# All vehicles
ALL_VEHICLES = VEHICLE_4G63 + VEHICLE_G4JS + VEHICLE_HYUNDAI_2L


def get_vehicles_by_group(group: str) -> List[VehicleConfig]:
    """Get vehicles by group name"""
    groups = {
        "4g63": VEHICLE_4G63,
        "g4js": VEHICLE_G4JS,
        "hyundai2l": VEHICLE_HYUNDAI_2L,
        "all": ALL_VEHICLES,
    }
    return groups.get(group.lower(), [])


def get_all_groups() -> Dict[str, List[VehicleConfig]]:
    """Get all vehicle groups"""
    return {
        "4g63": VEHICLE_4G63,
        "g4js": VEHICLE_G4JS,
        "hyundai2l": VEHICLE_HYUNDAI_2L,
    }
