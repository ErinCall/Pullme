pullme
======

pullme is a command-line script for making pull requests.
It's smart about choosing a base branch for the pull request--it examines git-log to make a good guess as to what the base branch should be.

Installation
------------
Installation is simple::

::
    curl https://raw.github.com/AndrewLorente/Pullme/master/scripts/pullme > ~/bin/pullme && chmod u+x ~/bin/pullme

If you'd like to develop pullme (possibly USING pullme!?) do the following:

::
    fork on github
    clone your fork
    python setup.py develop

Remotes
-------
First off we need to talk about remotes for a moment. Here's how pullme assumes your remotes are set up:

::
    origin -> github.com/CANONICAL_FORK.git
    $USER -> github.com/YOUR_FORK.git

If you're using a different setup, that's fine, we can work with that. You'll need to specify how your remotes are set up in ~/.pullmeconfig or WORKDIR/.pullmeconfig or command-line flags.

What it does
------------

* Check if there are outstanding changes
* push the current branch to your fork
* create pull request from your fork to the canonical fork.
* open $EDITOR to get the pull request title and body (taking the first line as the title, like git commit)
* submit a pull request through the github api

.pullmeconfig
-------------
~/.pullmeconfig and WORKDIR/.pullmeconfig are yaml files that tell pullme about your config. If ~/.pullmeconfig does not exist, pullme will help you create it--at a minimum, a password is necessary.
The other values you can put in .pullmeconfig are *upstream*, *personal*, and *assume*.
You can use the *upstream* and *personal* settings if you don't have your remotes structured the way pullme assumes. For example, if you use 'upstream' to refer to the canonical version and 'origin' for your own fork, you'd do this
::
    'upstream': 'upstream'
    'personal': 'origin'

The *assume* setting means pullme will trust its own heuristics, rather than prompting to confirm them. It will also trust *you*, and won't check to see if there are any outstanding changes.
