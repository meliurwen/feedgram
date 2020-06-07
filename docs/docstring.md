# Docstrings

## Useful resources
!!! info
    Before starting to contribute to documentation you should consult these resources first:

    + [mkdocstrings Documentation](https://pawamoy.github.io/mkdocstrings/)
      + [mkdocstrings Syntax Example #1](https://pawamoy.github.io/mkdocstrings/handlers/python/)
      + [mkdocstrings Syntax Example #2](https://github.com/pawamoy/mkdocstrings/blob/master/src/mkdocstrings/plugin.py)
    + [mkdocs-material Documentation](https://squidfunk.github.io/mkdocs-material/)
    + [mkdocs Documentation](https://www.mkdocs.org/)

## Generate the Documentation

### Prerequisites

+ `mkdocs-material`
+ `mkdocstrings`
+ `mkdocs-minify-plugin`
+ `mkdocs-git-revision-date-localized-plugin`

!!! tip
    These dependencies are listed in the `docs-requirements.txt` file, use the command below to install them in batch:

    ```sh
    pip install -r docs-requirements.txt
    ```

### Build Documentation

```sh
mkdocs build
```

### Automatically build and serve locally

```sh
mkdocs serve
```
