Super Snippet
-------------

This is Super Snippet, a plugin for [Sublime Text 2][subl] that gives
you an extended snippet syntax.  In particular in *addition* to the 
standard syntax you get:

   * Ability to use ${! ... !} to embed python code in your snippets
   * Ability to use ${\` ... \`} to embed shell commands

Note that these *chain*, so that each expansion can create syntax for the
following expansion.  In order the expansions go:

   * Embedded python code is evaluated and replaced with the output
   * Embedded shell commands are evalued and replaced with the output
   * Standard Sublime Text 2 snippet expansion occurs

Usage
-----

To add new snippets create a `SuperSnippet.sublime-settings` file in your 
`Packages/User` directory.  The format
of this file is a simple JSON object where the keys are the short text
to expand and the values are templates for the expansion.

In other words, on Mac OS X create `~/Library/Application Support/Sublime Text 2/Packages/User/SuperSnippet.sublime-settings` that looks something like this:

```javascript
{
	"uuid": "Our chosen unique string for now is: ${`uuidgen`}",
	"cc": "Character Count: ${! self.view.size() !}",
}
```

To use type the *exact* name of the snippet and hit tab.  If no match is found then Sublime Text 2 will
execute `insert_best_completion` as usual (meaning that the normal tab completion will occur.)

Installation
------------

Assuming you've got git installed (you don't?  shame on you!)

	cd ~/Library/Application Support/Sublime Text 2/Packages/User
	git co git://github.com/2shortplanks/SuperSnippet.git

Then create the `SuperSnippet.sublime-settings` file as described above.

To update

	cd ~/Library/Application Support/Sublime Text 2/Packages/User
	git pull

[subl]: http://www.sublimetext.com/2