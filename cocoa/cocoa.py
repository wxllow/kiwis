import os
import shutil

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .utils import import_mod_from_path, out_name, special_file


class Site:
    def __init__(self, path: os.PathLike = "") -> None:
        self.path = path
        self.src_path = os.path.join(self.path, "src")
        self.jenv = Environment(loader=FileSystemLoader(self.src_path), autoescape=True)

        with open(os.path.join(path, "site.toml"), "r") as f:
            self.config = Config(f.read())

    def build(self, output: os.PathLike = "") -> None:
        """Build the site."""
        # Make temp output directory
        tmp_output = f"{output}.tmp"

        if os.path.exists(tmp_output):
            shutil.rmtree(tmp_output)

        # Copy static files
        shutil.copytree(os.path.join(self.path, "static"), os.path.join(tmp_output))

        # Generate pages
        for file in [
            os.path.relpath(os.path.join(path, name), start=self.src_path)
            for path, _, files in os.walk(self.src_path)
            for name in files
        ]:
            # Ignore special files (e.g. _base.jinja)
            if special_file(file):
                continue

            out_loc = os.path.join(tmp_output, out_name(file))

            # Make directory if it doesn't exist
            os.makedirs(os.path.dirname(out_loc), exist_ok=True)

            generated_page = self.generate_page(file)

            with open(out_loc, "w") as f:
                f.write(generated_page)

        # Finish up and move to output
        if os.path.exists(output):
            shutil.rmtree(output)

        shutil.move(tmp_output, output)

    def generate_page(self, loc: str) -> str:
        """Generate a page."""
        if loc.endswith(".jinja") or loc.endswith(".html"):
            # Get props from Python file, if exists
            py_loc = os.path.join(self.src_path, f"{'.'.join(loc.split('.')[:-1])}.py")

            props = None

            if os.path.exists(py_loc):
                mod = import_mod_from_path(py_loc)

                if "props" in dir(mod):
                    props = mod.props

            # Render template
            return self.jenv.get_template(loc).render(
                site={
                    "name": self.config.name,
                    "slogan": self.config.slogan,
                },
                page={
                    "location": loc,
                    "params": {},
                },
                props=props,
            )
        else:
            with open(os.path.join(self.src_path, loc), "r") as f:
                return f.read()
