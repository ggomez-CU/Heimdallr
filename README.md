<h1 align="center">
<img src="https://github.com/Grant-Giesbrecht/heimdallr/blob/main/docs/images/heimdallr_banner.png?raw=True" width="800">
</h1><br>

Heimdallr offers a better way of implementing instrument control and scripting. It does this through a series of core features:

- In addition to providing a **base set of instrument drivers**, it enforces a convention such that drivers for different instrument models of the same 'type' (eg. two different models of 2-channel oscilloscope) are **guaranteed to use the same API**. This greatly simplifies script writing, and prevents your scripts from becoming bound to one specific instrument model. 
- **Networking:** Heimdallr includes an optional networking system which allows multiple computers to connect to a single AES-encrypted network. This allows you to monitor the state of your instruments remotely, start new measurements without being co-located with your instruments, or control instruments that are not physically close to each other. There is a wide range of applications for networked instrument control!
- **(WIP) GUIs:** Although still a work in progress, GUI widgets added for instrument categories allow you to make visual apps to control or monitor your instruments. Due to the inheritance and category strucutrue, these widgets are instrument model agnostic, and will work for any instrument of the appropriate category.
- **Easy to add new drivers:** Due to the category system used, writing new drivers is very straight forward. Only simple SCPI commands need to be added to the new driver, and the parent class will automatically enable networking and integration with GUI widgets.
- (Mention ecosystem of networks, common drivers, GUIs, and scripting helpers like interpret_range.)
- **Rich Logging:** Because Heimdallr's core use case concerns scientific experiments, robust and complete logging is key. Heimdallr automates logging via the [pylogfile](https://pypi.org/project/pylogfile/) library, recording every command sent to instruments, and saving logs in a dense binary open-source format, which can easily be analyzed and searched using the included command line tool, `lumberjack`.

## Installation

Heimdallr can be installed via pip using 

```
pip install heimdallr-py
```

## Instrument Control

### Technical detail: Category system and Drivers

- How the categories work, with 0-n
- How they use ABCs to force correct usage
- They inherit RemoteInstrument so without the end user paying attention, they can be used across a network!

Include graphic of cateogry system, including remote access, drivers and GUIs.

### Instrument Control Example

TODO = basic example

## Networking

### Technical Detail: Networking

- Mention TCPIP, AES, passwords, automatically setup database and server.
- Mention PyFrost (WIP)

### Networking Example

TODO = Networking example

[Read The Docs](https://heimdallr-py.readthedocs.io/en/latest/)

[PyPI](https://pypi.org/project/heimdallr-py/)
