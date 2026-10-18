def normalize_location_name(name: str) -> str:
    return "_".join(name.strip().lower().split()).replace("-", "_")
