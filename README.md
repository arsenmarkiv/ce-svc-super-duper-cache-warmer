# Python Service Template

This service is a template for creating python microservices that will be built
and deployed according to the standards established for deployed applications in
BNY Mellon Data & Analytics Solutions.

This template is intended to be forked and adapted for individual projects.

For more tips on developing using python, check out the ENGOPS wiki page on the topic:
https://eagleinvsys.atlassian.net/wiki/spaces/ENGOPS/pages/1294730070/HOWTO+D+A+Python+Tips#SonarQube-Scanning

## Conventions

* Python packages should be placed under the `src/` directory in the repository
  root. This is a matter of some debate in the python community, but is starting
  to be regarded as best practice (see
  https://hynek.me/articles/testing-packaging/#src). Nevertheless, DNA has
  adopted this layout. Per python packaging requirements, all packages must
  contain `__init__.py` in order to be built correctly. Directories which are not
  python packages (such as those containing static files), must be specifically
  included using the `package_data` parameter in setup.py (see below).
* To improve consistency across projects, and to reduce the maintenance burden
  on project owners, setuptools has been replaced with a EngOps-maintained
  wrapper, dnasetuptools. This dramatically reduces the boilerplate needed for
  `setup.py`. Further information may be found here:
  https://github.com/eagleinvsys/ce-component-dnasetuptools/blob/develop/README.md
* In an effort to maintain consistency across languages, DNA has made the
  decision to use gradle for building python packages. This replaces some of the
  standard tooling. While it is not strictly necessary to use gradle for local
  development, because gradle will be used in the CICD pipes it is considered
  best practice to use it locally.
* Linting uses Flake8 to comply with pep8 style guidelines, with some
  exceptions. For instance, line length is not stricly enforced.
* Tests are run with pytest, and should generally be in the `tests/` directory,
  and organized by package where possible. The tests directory and any
  subdirectories beneath it must be valid python packages (contain
  `__init__.py`) per pytest requirements.

## Getting Started

After forking this repo, there are a number of changes to be made. This section
will walk through updating this template for your project.


### Files To Update

#### Jenkinsfile

* `projectName` - Should match the repository name omiting the `ce`
  prefix.
* `repoName` - Should match the git repository name.
* `slackChannel` - Should refer to a channel is DNA's slack instance where
  build-related notifications will be posted.
* `teamEmail` - Should refer to an email address that reaches all team members.

The other parameters should generally be left at their initial values unless
deemed necessary.

#### gradle.properties

* `rootProjectName` - Should match the value of `projectName` in the
  Jenkinsfile.
* `version` - DNA uses [semantic versioning](https://semver.org/). Only the
  Major.Minor version should be specified in gradle.properties. The patch is
  determined at build-time automatically.
* `mainModule` - This should point to the module containing the `main()`
  function used to start your app. All module paths are relative to `src/`.
* `mainFunction` - The name of the function inside `mainModule` that starts your
  app. See `src/dnahelloworld/app.py` for an example.

The other parameters should generally be left at their initial values unless
deemed necessary.

#### setup.py

There should be very little in the way of updates required here unless you need
to specify a parameter to setup(). One such example is if you need to include
non-python files (such as static assets, jinja templates, etc.) in your package,
in which case you may update the `package_data` parameter. e.g:
```
setup(
    package_data={
        'infonator': ['templates/*.html', 'templates/**/*.html', 'static/*', 'static/**/*']
    }
)
```
A more exhaustive list of setup parameters may be found in setuptools's
[documentation](https://setuptools.readthedocs.io/en/latest/). You should also
review the
[documentation](https://github.com/eagleinvsys/ce-component-dnasetuptools/blob/develop/README.md)
for dnasetuptools.

#### requirements.txt

This file should contain the list of dependencies for your project. You may
manually keep this file up to date, or you may use `pip freeze` or another
helper utility to keep this file current. Though always be sure to review your
requirements by hand if you use a tool to generate this file. You do not need to
include your dependencies in setup.py as dnasetuptools will automatically pass
the contents of requirements.txt when your distribution is built.

#### README.md
It goes without saying that you should replace this README with one relevant to
your project.

#### Other files
Any other files in the root directory should generally be left alone unless
otherwise deemed necessary. You may, for instance, find cause to update
`.gitignore` beyond what is already included.

### Development Environment Setup

#### Prerequisites

This template is designed to be used with python 3.7+. We strongly encourage the
use of pyenv (https://github.com/pyenv/pyenv) for installing and managing your
local python installation as OS-packages are known to be outdated and fraught.
Installation is trivial on Mac with homebrew. If using pyenv, it is adviable to
additionally install the `pyenv-virtualenv` plugin (linked in pyenv's
README.md). If you chose to use other installation methods (such as binaries
from https://www.python.org/) for setting up your python environment, be sure to
use python 3.7, and also ensure that the `virtualenv` package is installed.

If you have chosen to install pyenv, you need only install and select an
appropriate version of python:

```
$ pyenv install 3.7.7
$ pyenv global 3.7.7
$ pyenv local 3.7.7
```

You will also want to ensure that your system is configured to use the DNA
artifactory as a package source as packages built by DNA CICD pipes are not
published to public pypi repositories. On Mac, the simplest way to do this is by
editing the file `~/.config/pip/pip.conf`. The same file may be in other
locations depending on platforms, refer to the
[pip documentation](https://pip.pypa.io/en/stable/user_guide/#config-file) for
the config file location for your platform.

The content of the file is simple:

```
[global]
index-url = https://artifactory.engops.az.eagleinvsys.com/artifactory/api/pypi/pypi-virtual/simple
```

Note these steps need only be performed once per development workstation; it
does not need to be repeated per project, unless you are changing the base
version of python.

#### Using Gradle (recommended)

EngOps has built a gradle plugin that helps to manage the environment for
building & testing python apps. Gradle and this plugin is used by the CICD
pipelines, so it is advisable to use it locally to help head-off any potential
problems you might encounter once your code is pushed. The only additional
prerequisite for using gradle is that JDK 11+ be installed in your development
environment. From there, the commands to stand up and activate your development
environment are simple:

```
$ python --version 
Python 3.7.7
$ ./gradlew initializeVenv
...
$ source ./build/.venv/bin/activate
$ ./gradlew installDependencies
```

##### Gradle tasks

While on the topic of gradle, here is a partial list of the tasks commands that
you may use. These wrap underlying python tools, but with some boilerplate
removed:

* `./gradlew initializeVenv` Initializes a new virtualenv with the base packages
  (pytest, flake8, dnasetuptools, and dependencies) in `build/.venv`.
* `./gradlew installDependencies` Installs all dependencies from
  `requirements.txt` into the current virtualenv.
* `./gradlew lint` Wraps flake8. An HTML linting report is automatically
  generated in `build/lint/index.html` and can be used for tracking down issues.
* `./gradlew test` Wraps pytest. An HTML report is automatically generated in
  `build/test-results/html/index.html`.
* `./gradlew createBdistWheel` generates a binary distribution. This replicates
  the functionaliy of the CICD pipe and can be used to check that all expected
  files (including `package_data` from setup.py) is being included in the
  package.
* `./gradlew buildDocker` (requires docker) will locally build the docker image
  and can be used for testing.
* `./gradlew sonarqube` Performs a sonarqube analysis. See the 
[wiki](https://eagleinvsys.atlassian.net/wiki/spaces/ENGOPS/pages/1294730070/HOWTO+D+A+Python+Tips#SonarQube-Scanning)
for details.

Gradle tasks may be chained, as well. So if you want to lint and test in a
single command, you may execute `./gradlew list test`. You may also use the
low-level python commands (`flake8`, `pytest`, etc.) provided you activated the
virualenv by performing the `source` command above, though you will not benefit
from the added features the gradle wrapper provides.

#### Using native tools (not recommended)
It is also possible to set up your development using native python tools,
although this is not directly supported by EngOps. You will still need an
appropriate version of python installed and active (see above). Here are the
basic commands for setting up a local environment without using gradle:

```
$ python --version
Python 3.7.7
$ python -m venv venv
$ source ./venv/bin/activate
$ pip install --upgrade pip
...
$ pip install -r requirements.devel.txt 
...
$ pip install -e .
```

With this completed, you should be able to use native python tools:
* `$ flake8 src/`
* `$ pytest`
* etc.

Again, these tools will not be run the same way they are executed in the CICD
pipeline, therefore it is recommended to use gradle where possible.

Happy Pythoning!

##### Troubleshooting
./gradlew initializeVenv
...
        from _ctypes import Union, Structure, Array
    ModuleNotFoundError: No module named '_ctypes'

solution -> install yum install libffi-devel; then re-install/recompile python via pyenv

