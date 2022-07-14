from typing import Optional
import os
import importlib.util


def import_mod_from_path(loc: os.PathLike) -> object:
    """Loads a module from a path and returns it."""
    spec = importlib.util.spec_from_file_location(
        f"crouton.__dyn__.{'.'.join(os.path.split(loc)[-1].split('.')[:-1])}", loc
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def merge_dict(a: dict, b: dict) -> dict:
    """Merge two dictionaries together. If any keys conflict, the value in b takes precedence."""
    a.update(b)
    return a


def special_file(name: os.PathLike) -> bool:
    """Check if file is a special file."""
    for part in os.path.split(name):
        if part.startswith("_"):
            return True

    return False


def out_name(name: os.PathLike) -> os.PathLike:
    """Output name for page."""
    sname = list(os.path.split(name))
    sname[-1] = sname[-1].replace(".jinja", ".html").replace(".md", ".html")
    return os.path.join(*sname)


def find_template(
    src_path, loc: os.PathLike, markdown: bool = False
) -> Optional[os.PathLike]:
    """Find the template for a page."""
    possible_names = ["_base.jinja", "_base.html"]
    markdown_names = ["_markdown.jinja", "_markdown.html"]

    for folder in [os.path.dirname(loc), src_path]:
        for f in os.listdir(folder):
            if markdown:
                if f in markdown_names:
                    return os.path.join(folder, f)

            if f in possible_names:
                return os.path.join(folder, f)
