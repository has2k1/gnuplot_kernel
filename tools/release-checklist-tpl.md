# Release Issue Checklist

Copy the template below the line, substitute (`s/<VERSION>/1.2.3/`) the correct
version and create an [issue](https://github.com/has2k1/gnuplot_kernel/issues/new).

The first line is the title of the issue

------------------------------------------------------------------------------
Release: gnuplot_kernel-<VERSION>

- [ ] Upgrade key dependencies if necessary

  - [ ] [metakernel](https://github.com/Calysto/metakernel)
  - [ ] [jupyter](https://github.com/jupyter/jupyter)


- [ ] Upgrade code quality checkers

  - [ ] pre-commit

    ```
    pre-commit autoupdate
    ```

  - [ ] ruff

    ```
    pip install --upgrade ruff
    ```

  - [ ] pyright

    ```sh
    pip install --upgrade pyright
    PYRIGHT_VERSION=$(pyright --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    python -c "
    import pathlib, re
    f = pathlib.Path('pyproject.toml')
    f.write_text(re.sub(r'pyright==[0-9]+\.[0-9]+\.[0-9]+', 'pyright==$PYRIGHT_VERSION', f.read_text()))
    "
    ```

- [ ] Run tests and coverage locally

  ```sh
  git switch main
  git pull origin/main
  make typecheck
  make test
  make coverage
  ```
  - [ ] The tests pass
  - [ ] The coverage is acceptable


- [ ] Create a release branch

  ```sh
  git switch -c release-v<VERSION>
  ```

- [ ] Tag a pre-release version. These are automatically deployed on `testpypi`

  ```sh
  git tag -as v<VERSION>rc1 -m "Version <VERSION>rc1"  # e.g. <VERSION>a1, <VERSION>b1, <VERSION>rc1
  git push -u origin release-v<VERSION>
  ```
  - [ ] GHA [release job](https://github.com/has2k1/gnuplot_kernel/actions/workflows/release.yml) passes
  - [ ] gnuplot_kernel test release is on [TestPyPi](https://test.pypi.org/project/gnuplot_kernel/#history)

- [ ] Update changelog

  ```sh
  nvim doc/changelog.qmd
  git commit -am "Update changelog for release"
  git push
  ```
  - [ ] Update / confirm the version to be released
  - [ ] Add a release date
  - [ ] The [GHA tests](https://github.com/has2k1/gnuplot_kernel/actions/workflows/testing.yml) pass

- [ ] Tag final version and release

  ```sh
  git tag -as v<VERSION> -m "Version <VERSION>"
  git push
  ```

  - [ ] The [GHA Release](https://github.com/has2k1/gnuplot_kernel/actions/workflows/release.yml) job passes
  - [ ] [PyPi](https://pypi.org/project/gnuplot_kernel) shows the new release

- [ ] Update `main` branch

  ```sh
  git switch main
  git merge --ff-only release-v<VERSION>
  git push
  ```
