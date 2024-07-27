# The What and Why of Heimdallr

## What is Heimdallr

Heimdallr is a Python package providing a high-level way of interacting with lab instruments (and
any other device you can control from your computer!) and a series of tools to provide advanced 
functionality such as networked access to your instruments.

Key features of Heimdallr:
* Instrument Control:
  * __Instrument Drivers:__ Heimdallr includes a selection of instrument driver classes. For example, a class is provided to interact with Rohde and Schwarz ZVA series vector network analyzers.
  * __Instrument Categories:__ All instrument drivers fall under some category definition. This allows users to know drivers meet some minimum standard. For example, you know all drivers meeting a hypothetical Oscilloscope category will implement a function to set the trigger level. This allows scripts to be designed instruments of a general category, then swapping out the actual physical hardware is relatively painless. Similarly, GUI widgets know exactly what they can expect from a corresponding driver.
* __Networking and Thread Management:__ (In Progress)
  * __TCP Server:__ Heimdallr makes it easy to setup a server accepting multiple client connections, with account configurable permissions, and AES encrypted communications. 
  * __Remote Access:__ Using a Heimdallr network, your instruments can be controlled and monitored from anywhere (with the right password!). 
  * __Thread Management:__ The _ToDo_ class automates the creation of new threads for each instrument, protecting your script or driver-node from freezing if a driver or instrument locks up. 
* __GUI Widgets:__ (ToDo)

## Why Not Just Use PyVisa

Heimdallr is not a replacement for PyVisa. As a matter of fact, Heimdallr relies on PyVisa 
and PyVisa-py for most of its drivers! Heimdallr doesn't repeat the great instrument communication
functionality provided by PyVisa, rather it provides a higher-level interface and set of tools for
interacting with lab instruments (that often uses PyVisa for communication under the hood).

If you're scripting or remotely controlling lab instruments, Heimdallr is likely faster and less
work in the medium term. If a driver isn't already provided, Heimdallr makes it easy to create new
drivers for your instrument that conform to the Heimdallr standard. Not only will this make your code
easier to reconfigure and understand in the future, but it will help your colleagues and the broader
scientific community who may need to use your instrument in the future!

## So What Does This Actually Look Like?

### Example 1: Scripting for an intrepid PhD student

Imagine you're trying to set up measurements of your amazing PhD project. However, the demands of your experiment change quickly and your pesky lab friends keep stealing your instruments because "they also need to graduate". How annoying! Well, lucky for you, you wrote your scripts with Heimdallr, so all you need to do when a friend "borrows" your precious oscilloscope is get ahold of a driver for a comparable oscilloscope! 

Need to change your measurement script's behavior on a whim (most likely, the whim of your advisor or beloved funding agency)? Fear not! No digging through manuals looking for SCPI commands for you! The Heimdallr driver you're already using has handy functions pre-defined for most common uses! You're a few function calls away from that well deserved coffee break!

### Example 2: The Diligent WFH Researcher

Suppose you want to set up a measurment of some sort, then get the hell out of dodge so you can go enjoy some fresh air. The trouble is, you don't know when your scripts are going to finish up and you should return to work. And god forbid the script crash and you need to head back into your lab just to hit "start" again! Lucky for you, Heimdallr's networking functionality allows you to remotely monitor your scripts and start new scripts using terminal-nodes! Setup a terminal node, intrepid researcher, start your measurement and get back outside!