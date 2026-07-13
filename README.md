# hucl

[![PyPI - Version](https://img.shields.io/pypi/v/hucl.svg)](https://pypi.org/project/hucl)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hucl.svg)](https://pypi.org/project/hucl)

-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install hucl
```

## Usage
```bash
hucl start https://my-hub.com/hub/api <TOKEN>
```

## License

`hucl` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Design

This CLI and library uses a [sansio](https://sans-io.readthedocs.io/) approach for splitting IO from logic. This makes it very easy to test and abstract out event-loop implementations (by implementing a smaller event loop!). 

I did this for fun — I've been telling people to do this for years without ever actually implementing such an approach in my own libraries.
