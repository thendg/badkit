# BADKit
> ***Blender Addon Development Kit**. A proper framework for addon development in Blender.*

BADKit is a framework for Blender addon framework development. That allows you to develop and test your custom Blender addons with ease.

## Usage
```
> badkit [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  build    Build an addon bundle from a specified source directory.
  install  Locally install a distribution package from PyPI.
  launch   Launch a Blender environment with a set of custom addons.
```

## Build
The `build` command builds a Blender-ready addon, doing all the hard work for you. All you provide is the path to your source directory and BADKit will figure out the rest.

## Install
The `install` command is a handy tool that locally installs Python distribution packages from the Python Package Index into a vendor directory in your project. This allows you to easily include external packages in your addons, without you needing to use strange workarounds, or your users having to set up extra dependencies to get your addon to work.

## Launch
The `launch` command will launch a Blender environment with your addons already setup and inside of it. This environment will have the most up to date versions of your addons, making the testing part of the developement lifecycle so much easier.