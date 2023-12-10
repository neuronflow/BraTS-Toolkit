from rich.console import Console


def citation_reminder(func):
    def wrapper(*args, **kwargs):
        console = Console()
        console.rule("[bold red]Friendly citation reminder[/bold red]")
        console.print(
            "If you use this software in your research, please [bold cyan]cite[/bold cyan] BraTS Toolkit and the original authors of the algorithms who make this repository and tool possible.",
            justify="center",
        )
        console.print(
            "Details can be found at https://github.com/neuronflow/BraTS-Toolkit#citation",
            justify="center",
        )
        console.print("Thank you!", justify="center")
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
            "You can already beta test the new BrainLes preprocessing pipeline which allows for arbitrary sequences and implements multiple backends for registration and brain extration and. Furthermore it does not require docker",
            justify="center",
        )
        console.print(
            "visit https://github.com/BrainLesion/preprocessing to learn more",
            justify="center",
        )
        console.rule()
        console.line()
        func(*args, **kwargs)

    return wrapper
