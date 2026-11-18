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

## CLI Usage
```bash
hucl start https://my-hub.com/hub/api <TOKEN>
```

## API Usage
```python
from hucl.flows import create_server


await create_server.asyn(api_url=..., api_token=...)
# Or
create_server.sync(api_url=..., api_token=...)
```

## Design Principles

The `hucl` library consists of a series of "flows". Each flow is a state machine that handles something like creating a server, where response codes are used to map between e.g. pending start, and running. 

Within these flows, we use a [sansio](https://sans-io.readthedocs.io/) approach to hoist IO like network or filesystem reads to the boundaries of the flow. In simple terms, this means that a flow doesn't itself perform any IO; a flow emits events (via `yield from`) that are handled by an external driver (e.g. an asyncio-friendly driver) that can return the responses. This makes it very easy to test and abstract out event-loop implementations (by implementing a smaller event loop!). 

I chose this design for fun and to test the hypothesis that this is a good way to write a library — I've been telling people to do this for years without ever actually implementing such an approach in my own work.


## License

`hucl` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
