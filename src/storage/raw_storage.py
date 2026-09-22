import json
import os
import tempfile
from pathlib import Path


class RawWeatherStorage:
    def __init__(self, base_dir: str | Path = "data/raw"):
        self.base_dir = Path(base_dir)

    def save(
        self,
        data: dict,
        filename: str,
    ) -> Path:
        if (
            not isinstance(filename, str)
            or not filename
            or filename in {".", ".."}
            or "/" in filename
            or "\\" in filename
            or not filename.endswith(".json")
        ):
            raise ValueError(
                "Filename must be a single .json filename"
            )

        serialized_data = json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )

        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = self.base_dir / filename
        temp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.base_dir,
                prefix=".weather_",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_path = Path(temp_file.name)

                temp_file.write(serialized_data)
                temp_file.flush()
                os.fsync(temp_file.fileno())

            # Publish only after the temporary file is complete.
            # Unlike os.replace(), os.link() won't overwrite
            # an existing destination.
            os.link(temp_path, file_path)

        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

        return file_path