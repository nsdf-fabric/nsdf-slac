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

1. Install the CLI in editable mode with the following `uv pip install -e .`.
2. Implement your coding changes following the structure of the project. For a new command add it to `src/nsdf_dark_matter_cli/cli.py`.
3. Implement corresponding tests under `tests`.
4. Make sure you do not introduce breaking changes by passing all the tests.
5. Follow all the other steps starting from [Opening a Pull Request](./pullrequests.md).
