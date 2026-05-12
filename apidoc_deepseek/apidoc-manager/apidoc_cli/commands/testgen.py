"""Test generation command."""

import typer
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.progress import Progress

from apidoc_cli.utils import read_input

app = typer.Typer()
console = Console()


@app.callback()
def testgen_command(
    ctx: typer.Context,
    spec_file: Path = typer.Argument(..., help="OpenAPI specification file"),
    output_dir: Path = typer.Option(Path("./tests"), "--output", "-o", help="Output directory"),
    framework: str = typer.Option("pytest", "--framework", "-f", help="Test framework"),
    language: str = typer.Option("python", "--language", "-l", help="Language"),
) -> None:
    """Generate tests from OpenAPI specification."""
    
    try:
        from apidoc_cli.plugins import PluginManager

        spec = read_input(spec_file)
        console.print(f"[bold]Generating tests for:[/] {spec.get('info', {}).get('title', 'API')}")

        if language == "python" and framework == "pytest":
            from apidoc_cli.plugins.pytest_generator import PytestGeneratorPlugin
            generator = PytestGeneratorPlugin()
        else:
            plugin_manager = PluginManager()
            generator = plugin_manager.get_test_generator(f"{language}-{framework}")
            if not generator:
                console.print(f"[red]Error:[/] No generator found for {language}/{framework}")
                raise typer.Exit(1)

        with Progress() as progress:
            task = progress.add_task("Generating tests...", total=None)
            files = generator.generate(spec, output_dir)
            progress.update(task, description="[green]OK Tests generated[/]")

        console.print(f"\n[green]OK[/] Generated {len(files)} test files in [bold]{output_dir}[/]")
        console.print("\n[cyan]Run tests with:[/]")
        console.print(f"  pytest {output_dir} -v")
    except Exception as e:
        logger.error(f"Test generation failed: {e}")
        console.print(f"[red]Error:[/] {e}")
        if ctx.obj.get("debug"):
            console.print_exception()
        raise typer.Exit(1)