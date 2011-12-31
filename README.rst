pullme
======

pullme is a command-line script for making pull requests.
It's smart about choosing a base branch for the pull request--it examines git-log to make a good guess as to what the base branch should be.

Installation
------------
Installation is simple::

    curl https://raw.github.com/AndrewLorente/Pullme/master/scripts/pullme > ~/bin/pullme && chmod u+x ~/bin/pullme

If you'd like an easier way to stay up-to-date, or you'd like to develop pullme (possibly USING pullme!?) do the following::

    fork on github
    clone your fork
    python setup.py develop

What it does
------------

* Check if there are outstanding changes
* push the current branch to your fork
* create pull request from your fork to the canonical fork.
* open $EDITOR to get the pull request title and body (taking the first line as the title, like git commit)
* submit a pull request through the github api

Remotes
-------
It behooves us to talk about remotes for a moment. Here's how pullme assumes your remotes are set up::

    origin -> github.com/CANONICAL_FORK.git
    $USER -> github.com/YOUR_FORK.git

If you're using a different setup, that's fine, we can work with that. You'll need to specify how your remotes are set up, either using git config or command-line flags.

pullme configuration
--------------------
The settings you can configure for pullme are ``upstream``, ``personal``, ``assume``, ``file``, ``issue``, and ``open``.

You can use the ``upstream`` and ``personal`` settings if you don't have your remotes structured the way pullme assumes. These should be set to the remote name as configured using ``git remote``.

The ``assume`` setting means pullme will trust its own heuristics, rather than prompting to confirm them. It will also trust *you*, and won't check to see if there are any outstanding changes. ``Assume`` is a very trusting setting.

The ``file`` setting reads the pull request title and body from the given file. If there's a problem with the file, it'll be opened in $EDITOR.

The ``issue`` setting skips the title and body entirely; instead, your pull request will use the given github issue number.

the ``open`` setting will open the newly-created pull request in your browser after creating it. Currently this only works on OSX.

pullme and .gitconfig
---------------------
pullme can also look up any of the above settings in your git config. To configure pullme, run::

    git config [--global] pullme.SETTING VALUE

For example, if you typically use 'upstream' to refer to the canonical version and 'origin' for your own fork, you'd do this::

    git config --global pullme.upstream upstream
    git config --global pullme.personal origin

You can also use the non-global git config, if one of your repositories doesn't conform to your usual conventions::

    git config pullme.upstream canonical

Every single one of pullme's command-line flags can also be put in your git config, even the ones that seem to make very little sense::

    git config --global pullme.issue 17

As with all things in life, the final judgment of what is wisdom and what is foolishness is left to you.
