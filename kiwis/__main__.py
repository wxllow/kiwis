import os
from time import time

import rich_click as click
from rich import print
from rich.prompt import Prompt, Confirm
import toml

from .kiwis import Site


@click.group()
def cli():
    pass


@cli.command()
def init():
    loc = Prompt.ask(
        "[bright_magenta]Where would you like to create your site?", default="."
    )

    if os.path.exists(loc):
        raise FileExistsError(f"{loc} already exists.")

    name = Prompt.ask(
        "[bright_blue]What is your site's name?",
        default=(
            loc if os.path.abspath(loc) != os.path.abspath(os.getcwd()) else "My Site"
        ),
    )

    print(f"[bright_magenta]Initializing {name}...")

    # Make site directory
    os.makedirs(loc)

    # Make site toml file
    with open(os.path.join(loc, "site.toml"), "w") as f:
        toml.dump({"name": name}, f)

    # Make directories
    os.mkdir(os.path.join(loc, "src"))
    os.mkdir(os.path.join(loc, "static"))

    print("[bright_green]Initialized!")


@cli.command()
@click.argument("path", type=click.Path(file_okay=False, exists=False))
def build(path):
    print(f"[bright_magenta]Building...")

    site = Site(path)
    start = time()
    site.build("./build")

    print(f"[bright_green]Built in {round((time()-start)*1000)}ms!")


@cli.command()
@click.argument("path", type=click.Path(file_okay=False, exists=False))
def dev(path):
    print("[bright_magenta]Starting development server...")

    site = Site(path)
    site.dev()


if __name__ == "__main__":
    cli()
