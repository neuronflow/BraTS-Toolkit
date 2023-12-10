from rich.console import Console

CITATION_LINK = "https://github.com/neuronflow/BraTS-Toolkit#citation"


def citation_reminder(func):
    def wrapper(*args, **kwargs):
        console = Console()
        console.rule("Thank you for using [bold]BraTS Toolkit[/bold]")
        console.print(
            f"Please support our development by citing BraTS Toolkit and the papers of the segmentation algorithms you use:",
            justify="center",
        )
        console.print(
            f"{CITATION_LINK} -- Thank you!",
            justify="center",
        )
        console.rule()
        console.line()
        func(*args, **kwargs)

    return wrapper


def deprecated_preprocessor(func):
    def wrapper(*args, **kwargs):
        console = Console()
        console.rule("[bold red]Deprecation note[/bold red]")
        console.print(
            "Support for BraTS Toolkit's preprocessor will be deprecated soon, even though it should continue working.",
            justify="center",
        )
        console.print(
            "You can already beta test the new BrainLes preprocessing: https://github.com/BrainLesion/preprocessing",
            justify="center",
        )
        console.print(
            "Unlike the original preprocessing from BraTS Toolkit, the new pipeline allows for arbitrary sequences, implements multiple backends for registration and brain extration and does not require docker.",
            justify="center",
        )
        console.rule()
        console.line()
        func(*args, **kwargs)

    return wrapper
