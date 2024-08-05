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
            "Deprecation Notice: Support for the BraTS Toolkit's preprocessor is now deprecated, although it is expected to remain functional.",
            justify="center",
        )
        console.print(
            "Please note that this deprecation does not impact the fusion module, which will continue to receive maintenance and support.",
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


def deprecated_segmentor(func):
    def wrapper(*args, **kwargs):
        console = Console()
        console.rule("[bold red]Deprecation note[/bold red]")
        console.print(
            "Deprecation Notice: Support for the BraTS Toolkit's segmentor is now deprecated, although it is expected to remain functional.",
            justify="center",
        )
        console.print(
            "Please note that this deprecation does not impact the fusion module, which will continue to receive maintenance and support.",
            justify="center",
        )
        console.print(
            "We recommend transitioning to the BrainLes segmentor tool available at: https://github.com/BrainLesion/BraTS for segmentation tasks.",
            justify="center",
        )

        console.rule()
        console.line()
        func(*args, **kwargs)

    return wrapper
