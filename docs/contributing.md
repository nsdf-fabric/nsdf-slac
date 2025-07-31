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

## Contributing

### 🖥️ CLI

These steps will help you get started with contributing to the [NSDF Dark Matter CLI](./cli.md)

#### Working Directory

All the code for the NSDF Dark Matter CLI is located in the `nsdf_dark_matter_cli` directory in the root of the project, you will need to move into it with the following command:

```bash
cd nsdf_dark_matter_cli
```

#### Installing Dependencies

To install all the dependencies of the project, you can run the following command:

```bash
uv sync
```

#### Activating the Environment

Lastly, you will need to activate the environment with the following command:

```bash
source .venv/bin/activate
```

#### Developing Code

Now that you have the environment activated, you are ready to contribute code to the CLI. A typical development workflow might look like this.

1. Follow the steps outlined in [Creating a Branch](#creating-a-branch).
2. Install the CLI in editable mode with the following `uv pip install -e .`.
3. Implement your coding changes following the structure of the project. For a new command add it to `src/nsdf_dark_matter_cli/cli.py`.
4. Test your changes with the corresponding calls to `nsdf-cli`.
5. Follow all the other steps starting from [Opening a Pull Request](#opening-a-pull-request).

### 📚 Library

These steps will help you get started with contributing to the [NSDF Dark Matter Library](./library.md)

#### Working Directory

All the code for the NSDF Dark Matter Library is located in the `nsdf_dark_matter` directory in the root of the project, you will need to move into it with the following command:

```bash
cd nsdf_dark_matter
```

#### Installing Dependencies

To install all the dependencies of the project, you can run the following command:

```bash
uv sync
```

#### Activating the Environment

Lastly, you will need to activate the environment with the following command:

```bash
source .venv/bin/activate
```

#### Developing Code

Now that you have the environment activated, you are ready to contribute code to the library. A typical development workflow might look like this.

1. Follow the steps outlined in [Creating a Branch](#creating-a-branch).
2. Implement your coding changes following the structure of the project. For a new module add it under `src/nsdf_dark_matter`, or add code an existing module. Then add corresponding tests under `tests`.
3. Make sure you do not introduce breaking changes by passing all the tests.
4. Follow all the other steps starting from [Opening a Pull Request](#opening-a-pull-request).

### 📄 Documentation

These steps will help you get started with contributing to the [NSDF Dark Matter documentation](https://nsdf-fabric.github.io/nsdf-slac/)

#### Virtual Environment

At the root of the project, you can create a new virtual environment with the following command:

```bash
uv venv docs_env --python 3.10
```

#### Activating the Environment

Activate the environment with the following command:

```bash
source docs_env/bin/activate
```

#### Installing Dependencies

You will need to install the following dependencies to develop locally:

```bash
uv pip install mkdocs mkdocs-material
```

#### Developing Code

Now that you have the environment activated, you are ready to contribute code to the documentation. A typical development workflow might look like this.

1. Follow the steps outlined in [Creating a Branch](#creating-a-branch).
2. Spin up the documentation page locally by running `mkdocs serve`.
3. Implement your documentation changes following the structure of the project. All of the project documentation is under the `docs` directory. Make sure to put assets in the respective directory under `docs/assets`. For adding gifs see [creating gifs](#creating-gifs).
4. Follow all the other steps starting from [Opening a Pull Request](#opening-a-pull-request).

#### Creating gifs

Gifs in the documentation are generated by the fantastic [vhs library](https://github.com/charmbracelet/vhs) from [Charm Bracelet](https://github.com/charmbracelet). To add a new gif document the **.tape** script in the `docs/assets/tapes` folder
and then add the **gif** artifact to the appropriate folder.

## Pull Requests (PR)

### Creating a Branch

From your forked repository, you must create a new branch from the default `main`. Use the naming convention **type/description-of-work** when naming a branch, i.e, `docs/adding-gif-to-cli` or `feat/adding-detector-method-to-library`.
The following are common type of pull requests:

- `feat`: New feature/functionality added.
- `fix`: Fixes to a particular code defect/bug.
- `docs`: Adds or fixes the documentation content.
- `test`: Adds tests to the code.
- `ci`: Adds new components/actions to the continuous integration pipeline, i.e, automatic artifact uploads.
- `revert`: Removes code previously merged.

### Opening a Pull Request

Once you are done implementing the changes, go ahead and open a pull request in the [nsdf-slac repository](https://github.com/nsdf-fabric/nsdf-slac/pulls).

[Open a PR](https://github.com/nsdf-fabric/nsdf-slac/pulls){ .md-button}

You will need to set the **compare** branch to new branch you created in your forked branch, and the **base** branch should be **main**.

### CI/CD Pipeline

When you open a pull requests, a CI pipeline will be triggered, for different purposes **testing**, **artifact building**, etc. If your change causes the CI to fail you must make sure that you are not introducing breaking changes
to the codebase. If you are unsure why your change is failing in the CI pipeline, you can mention one of the maintainers [here](https://github.com/nsdf-fabric/nsdf-slac/blob/main/.github/CODEOWNERS).

### Merging Changes

After opening a pull request, a maintainer of the project will review the changes and determine if additional modifications are needed before merging your code.
Once the maintainer has no further feedback, your code will be approved and merged into the project 🎉.

## License

By contributing to the NSDF Dark Matter project, you agree that your contributions will be licensed by a specific License. You can find this information in the [LICENSE](https://github.com/nsdf-fabric/nsdf-slac/blob/main/LICENSE) file of the nsdf-slac repository.
