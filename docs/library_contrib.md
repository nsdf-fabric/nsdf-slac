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

1. Implement your coding changes following the structure of the project. For a new module add it under `src/nsdf_dark_matter`, or add code an existing module. Then add corresponding tests under `tests`.
2. Make sure you do not introduce breaking changes by passing all the tests.
3. Follow all the other steps starting from [Opening a Pull Request](./pullrequests.md).
