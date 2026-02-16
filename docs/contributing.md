# Contributing

Contributions are always welcome, no matter how large or small. Before contributing, please read the [Code of Conduct](./CODE_OF_CONDUCT.md) and follow the directions below:

## Communication Style

- Always leave a detailed description in the pull request. Leave nothing ambiguous for the reviewer.
- Always review your code first. Run the project locally and test it before requesting a review.
- Always leave screenshots for visual changes.
- If you are addressing an open issue, make sure to link it to your pull request.
- Communicate in the GitHub repository. Whether in the issue or the pull request, keeping the lines of communication open and visible to everyone on the team helps everyone around you.

## 🚀 Getting Started

### Cloning the Repository

For all the components of the project [CLI](./cli.md), [Library](./library.md), and [Dashboard](./dashboard.md) you will need to follow the next steps:

1. [Fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) the [nsdf-slac](https://github.com/nsdf-fabric/nsdf-slac) repository.
2. Clone the forked repository to your local machine.

### Python

!!! info "Virtual Environment"

    To begin, make sure you have **Python>=3.10** or higher installed on your machine. You can download it from the official website: [Install Python](https://www.python.org/downloads/).
    All of the components of the project use [uv](https://docs.astral.sh/uv/) as the Python package and project manager. Therefore, in order to develop effectively, it is recommended to install uv
    by following this [installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### Creating a Branch

From your forked repository, you must create a new branch from the default `main`. Use the naming convention **type/description-of-work** when naming a branch, i.e, `docs/adding-gif-to-cli` or `feat/adding-detector-method-to-library`.
The following are common type of pull requests:

- `feat`: New feature/functionality added.
- `fix`: Fixes to a particular code defect/bug.
- `docs`: Adds or fixes the documentation content.
- `test`: Adds tests to the code.
- `ci`: Adds new components/actions to the continuous integration pipeline, i.e, automatic artifact uploads.
- `revert`: Removes code previously merged.

### Developing

Read the following guides to learn about how you can contribute to Nexus-DM software stack:

- [Contributing to the CLI](./cli_contrib.md)
- [Contributing to the Library](./library_contrib.md)
- [Contributing to the documentation](./documentation_contrib.md)

## License

By contributing to the NSDF Dark Matter project, you agree that your contributions will be licensed by a specific License. You can find this information in the [LICENSE](https://github.com/nsdf-fabric/nsdf-slac/blob/main/LICENSE) file of the nsdf-slac repository.
