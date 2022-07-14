import os
import shutil
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

import markdown
import frontmatter
from jinja2 import Environment, FileSystemLoader
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config import Config
from .utils import (
    import_mod_from_path,
    out_name,
    special_file,
    find_template,
)


class DevFSHandler(FileSystemEventHandler):
    def __init__(self, app) -> None:
        super().__init__()
        self.app = app

    def on_any_event(self, event):
        self.app.build("dev.tmp")


class DevHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="dev.tmp", **kwargs)


class Site:
    def __init__(self, path: os.PathLike = "") -> None:
        self.path = path
        self.src_path = os.path.join(self.path, "src")
        self.jenv = Environment(loader=FileSystemLoader(self.src_path), autoescape=True)

        with open(os.path.join(path, "site.toml"), "r") as f:
            self.config = Config(f.read())

    def dev(self) -> None:
        self.build("dev.tmp")

        # Watch for changes
        observer = Observer()
        observer.schedule(DevFSHandler(self), self.path, recursive=True)
        observer.start()

        # Start HTTP server
        with TCPServer(("", 3000), DevHTTPHandler) as httpd:
            print("Serving at port", 3000)
            httpd.serve_forever()

        observer.join()

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

            if not generated_page:
                continue

            with open(out_loc, "w") as f:
                f.write(generated_page)

        # Finish up

        # For all html files not named index.html, make it's own folder
        for file in [
            os.path.join(path, name)
            for path, _, files in os.walk(tmp_output)
            for name in files
        ]:
            if (
                file.endswith(".html")
                and not os.path.split(file)[-1].strip() == "index.html"
            ):
                if os.path.exists(
                    os.path.join(file.replace(".html", ""), "index.html")
                ):
                    continue

                os.makedirs(os.path.join(file.replace(".html", "")), exist_ok=True)
                shutil.copy(
                    os.path.join(file),
                    os.path.join(file.replace(".html", ""), "index.html"),
                )

        # Move temp output to output dir
        if os.path.exists(output):
            shutil.rmtree(output)

        shutil.move(tmp_output, output)

    def generate_page(self, loc: str) -> str:
        """Generate a page."""
        default_vars = {
            "site": {
                "name": self.config.name,
                "slogan": self.config.slogan,
            },
            "page": {
                "location": loc,
                "params": {},
            },
        }

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
                **default_vars,
                props=props,
            )
        elif loc.endswith(".md"):
            # Get metadata and content from frontmatter
            with open(os.path.join(self.src_path, loc), "r") as f:
                data = frontmatter.loads(f.read())

            # Render markdown using template
            base_template_loc = os.path.relpath(
                find_template(
                    self.src_path, os.path.join(self.src_path, loc), markdown=True
                ),
                start=self.src_path,
            )

            template = """
            {% extends _md.base %}
            {% block content %}
                {{ _md.content|safe }}
            {% endblock %}
            """

            # Add markdown content to variables
            default_vars["page"].update(
                {"metadata": data.metadata, "content": data.content}
            )

            # Render markdown
            rendered = markdown.markdown(data.content)

            # Render template
            return self.jenv.from_string(template).render(
                **default_vars, _md={"base": base_template_loc, "content": rendered}
            )
        elif loc.endswith(".py"):
            return None
        else:
            with open(os.path.join(self.src_path, loc), "r") as f:
                return f.read()
