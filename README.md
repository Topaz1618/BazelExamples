# BazelExamples

[中文README](/Docs/README_CN.md)

BazelExamples provides clear examples of using Bazel to build Python projects, showcasing BUILD and WORKSPACE definitions in different scenarios.


## Tech Stack
BazelExamples utilizes the following technology stack and tools:

- Python
- JavaScript
- Tornado
- gpt-3.5 model: The core model for text generation
- Redis: Used as a dependency for the GPTBot to provide caching and data storage functionality.
- HTML/CSS
- MongoDB
- MYSQL

## Examples
### Stage1
- BUILD:
    - Python Build: Demonstrates basic usage of the py_binary rule.

-  WORKSPACE:
    - Remote Repository Download: Uses rules_python for remote repository download.
    - Loads Python-related rules and repositories.

### Stage3
- BUILD:
    - Python Build: Illustrates basic usage of the py_binary rule.
    - Template and Static File Configuration: Utilizes the filegroup() rule to configure template and static files.

- WORKSPACE:
    - Remote Repository Download: Employs rules_python for remote repository download.
    - Loads Python-related rules and repositories.

### Stage4
- BUILD:
    - Python Build: Demonstrates basic usage of the py_binary rule.
    - Template and Static File Configuration: Utilizes the filegroup() rule to configure template and static files.
    - Packaging and Archiving: Uses the pkg_tar() rule to package the project into a tar file.

- WORKSPACE:
    - Remote Repository Download Support: Implements support for remote repository download through rules_python.
    - Remote Repository Download Support: Introduces the pkg_tar remote repository, providing support for the pkg_tar() rule.
    - Loads Python-related rules and repositories.


## Usage

### Build
```
bazel build //:apps
```

### Run

Executes the build steps and runs the final generated binary file based on the dependencies and build rules.

```
bazel run apps
```

or run the generated binary file directly
```
./bazel-bin/apps
```


### Clean Build Directory and Cache
```
bazel clean --expunge
```

### Build Specific Target
This command builds the target :test_tar instead of all parts of the project.
```
bazel build -s --symlink_prefix= :test_tar
```

Parameters:
```
-s option is used to output detailed build information


--symlink_prefix= option specifies the prefix; if empty, the build result is placed in the bazel-bin/ directory by default
```


# Copyright and License
BazelExamples is licensed under the [MIT License](LICENSE) License. Refer to the LICENSE file for more information.

Please feel free to ask any questions or provide suggestions. Thank you for using and contributing to BazelExamples!