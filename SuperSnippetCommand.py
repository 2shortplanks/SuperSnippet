import sublime, sublime_plugin, os, re

a_to_z = re.compile("^[A-Za-z_-]*$")

class SuperSnippetCommand(sublime_plugin.TextCommand):


	# the delimiters
	def start_cmd(self):    return "${`"
	def end_cmd(self):      return "`}"
	def start_python(self): return "${!"
	def end_python(self):   return "!}"

	# TODO: Handle \ to esxape input.  This probably will mean we
	# need to recode to do a character by character scan
	def process_template_with(self,template,start,end,callback):
		a = 0
		b = 0;
		while True:
			try:
				a = template[a:].index(start) + a
				a += len(start);
			except ValueError:
				break;
			try:
				b = template[a:].index(end) + a
			except ValueError:
				sublime.error_message("SuperSnippet Error: Can't find end marker '%s' after character %d as expected" % (self.start_cmd(), a))
				raise;

			command = template[a:b];
			result = callback(command);
			template = template[:a - len(start)] + result + template[b+len(end):]
			b = b - len(command) + len(result)
		return template

	def convert_template_into_snippet(self, template):
		# first we run all python blocks.  Note that this can return shell commands and snippet expansion
		template = self.process_template_with(template, self.start_cmd(), self.end_cmd(),lambda x:os.popen(x).read())

		# Then we run all shell commands.  Note that this can return snippet expansion
		template = self.process_template_with(template, self.start_python(), self.end_python(), lambda x: str(eval(x)))

		return template 

	# TODO: Make this more snippet like
	def current_word(self):
		return self.view.substr(self.view.word(self.view.sel()[0].end()));

	def insert_super_snippet(self, edit):
		# okay, what's the current word we're looking at?
		word = self.current_word()
		if (not word): return

		# is this in our settings file?  This should be in your User dir
		# and look like { "shorttext": "expanded texmplate", ... }
		settings = sublime.load_settings("SuperSnippet.sublime-settings")
		if (settings.has(word)):
			template = settings.get(word)
		else:
			# look for a file that is named after the snippet in the
			# User directory.  we will only do this if the snippet has an
			# ascii A-Za-z short form
			if (a_to_z.match(word)):
			    path = os.path.join(sublime.packages_path(),"User","%s.sublime-supersnippet" % word)
			    if not os.path.isfile(path):
			        return
			    try:
			    	template = open(path,"r").read()
			    except IOError as e:
			    	sublime.error_message("Problem reading file %s: %s" % (path, e))
			    	return
			else:
				return


		# remove the current word
		self.view.erase(edit,self.view.word(self.view.sel()[0]))

		# insert the replacement snippet
		snippet = self.convert_template_into_snippet( template )
		self.view.run_command("insert_snippet", {'contents': snippet})

		return True;

	def run(self, edit):
		print "Super Snippet triggered!"
		if (not self.insert_super_snippet(edit)):
			# no snippet?  Run normal completion
			print "falling back"
			self.view.run_command("insert_best_completion", {"default": "	", "exact": False})
