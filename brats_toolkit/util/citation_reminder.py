from rich.console import Console

CITATION_LINK = "https://github.com/neuronflow/BraTS-Toolkit#citation"
BRATS_LINK = "https://github.com/BrainLesion/BraTS/"


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
            "Deprecation Notice: Support for the BraTS Toolkit's preprocessor is now deprecated, although it is expected to remain functional.",
            justify="center",
        )
        console.print(
            "Please note that this deprecation does not impact the segmentor and fusion module, which will continue to receive maintenance and support.",
            justify="center",
        )
        console.print(
            "We recommend transitioning to the BrainLes preprocessing tool available at: https://github.com/BrainLesion/preprocessing for preprocessing tasks.",
            justify="center",
        )
        console.print(
            "In contrast to the original BraTS Toolkit preprocessing, the new BrainLes pipeline offers the flexibility of arbitrary sequences, incorporates multiple backends for registration and brain extraction, and eliminates the need for Docker.",
            justify="center",
        )

        console.rule()
        console.line()
        func(*args, **kwargs)

    return wrapper


def new_segmentor_note(func):
    def wrapper(*args, **kwargs):
        console = Console()
        console.rule("[bold cyan]New segmentor package[/bold cyan]")
        console.print(
            "We developed a new segmentation tool that provides the latest BraTS algorithms (2023 and later) along with various improvements and features.",
            justify="center",
        )
        console.print(
            f"While the BraTS Toolkit segementation module will remain functional for the old models we recommend transitioning to the new BraTS package available at: {BRATS_LINK} to get the latest models and features.",
            justify="center",
        )
        console.rule()
        console.line()
        func(*args, **kwargs)

    return wrapper
