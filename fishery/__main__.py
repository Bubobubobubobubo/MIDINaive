import click

from . import console
from .profiler import Profiler
from .server import Server
# traceback is used to print exceptions in the console
import traceback
import sys

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"],
}


@click.group(
    context_settings=CONTEXT_SETTINGS,
    help="Starts sardine in an asyncio REPL.",
    invoke_without_command=True,
)
@click.version_option(
    package_name="sardine",
    prog_name=__package__,
    message="%(prog)s for %(package)s v%(version)s",
)
@click.pass_context
def main(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        cons = console.Console()
        server = start_server(cons.console)
        cons.on_write(lambda data: print("data", data) or server.broadcast("logs", data))
        cons.start()


def start_server(console):
    from threading import Thread
    import logging
    import webbrowser
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    server = Server(console)
    print("hello")
    Thread(target=lambda: server.socketio.run( server.app,  port=3000, debug=False, use_reloader=False,)).start()
    print("[red]Opening embedded editor at: [yellow]http://127.0.0.1:3000[/yellow][/red]")
    webbrowser.open('http://localhost:3000')
    return server


@main.command(
    short_help="Run sardine with a background profiler (requires the yappi package)",
    help="""
        This command starts the deterministic profiler, yappi, and measures statistics
        for both sardine and any functions written in the console. Once the REPL
        is closed, a pstats file will be written containing the session's stats.
        You can inspect the file's contents with Python's built-in pstats module
        or a third-party package like snakeviz.
        """,
)
@click.option(
    "-c",
    "--clock",
    default="wall",
    help="The clock type to use. Wall time includes time spent waiting, "
    "while CPU time ignores it.",
    show_default=True,
    type=click.Choice(("cpu", "wall"), case_sensitive=False),
)
@click.option(
    "-o",
    "filepath",
    default="stats.prof",
    help="The path to use when outputting the pstats file",
    show_default=True,
    type=click.Path(dir_okay=False, writable=True),
)


def profile(clock: str, filepath: str):
    profiler = Profiler(clock=clock, filepath=filepath)
    with profiler:
        console.start()


if __name__ == "__main__":
    main()
