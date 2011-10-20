import sublime, sublime_plugin, os, re

a_to_z = re.compile("^[A-Za-z0-9_-]*$")

class ShowSuperSnippetCommand(sublime_plugin.WindowCommand):

	def open_snippet(self, word):
		# is this in our settings file?  This should be in your User dir
		# and look like { "shorttext": "expanded texmplate", ... }
		settings = sublime.load_settings("SuperSnippet.sublime-settings")
		if settings.has(word):
			path = os.path.join(sublime.packages_path(),"User","SuperSnippet.sublime-settings")
			self.window.open_file(path,sublime.TRANSIENT)
			return
			
		else:
			# look for a file that is named after the snippet in the
			# User directory.  we will only do this if the snippet has an
			# ascii A-Za-z short form
			if a_to_z.match(word):
				path = os.path.join(sublime.packages_path(),"User","%s.sublime-supersnippet" % word)
				self.window.open_file(path,sublime.TRANSIENT)
			else:
				return

	def run(self):
		self.window.show_input_panel("Show Super Snippet:", "", self.open_snippet, None, None)

