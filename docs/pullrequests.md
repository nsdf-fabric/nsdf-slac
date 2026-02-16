## Pull Requests (PR)

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
