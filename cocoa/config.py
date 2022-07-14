"""Processing of site.toml file."""
import toml

from .exceptions import InvalidConfigError


class Config:
    def __init__(self, data: str = "") -> None:
        self._config = toml.loads(data)

        try:
            self.name = self._config["name"]
            self.slogan = self._config.get("slogan", "A website!")
            self.preferences = self._config.get("preferences", {})
            self.plugins = self._config.get("plugins", [])
        except KeyError as e:
            raise InvalidConfigError(f"Missing item in config: {e.args[0]!r}")

    @property
    def raw(self) -> dict:
        """Return the raw config."""
        return self._config
