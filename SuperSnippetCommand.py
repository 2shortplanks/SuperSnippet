import sublime, sublime_plugin, os, re, tempfile
from subprocess import Popen, PIPE

a_to_z = re.compile("^[A-Za-z0-9_-]*$")

class SuperSnippetCommand(sublime_plugin.TextCommand):

	# the delimiters
	def start_cmd(self):    return "${`"
	def end_cmd(self):      return "`}"
	def start_python(self): return "${!"
	def end_python(self):   return "!}"

	def run_shell_command(self, cmd):
		env = os.environ.copy();

		# textual content of the current line.
		env['TM_CURRENT_LINE'] = self.current_line()

		# the word in which the caret is located.
		env['TM_CURRENT_WORD'] = self.current_word()

		if (self.view.file_name()):
			# the folder of the current document (may not be set).
			env['TM_DIRECTORY'] = os.path.dirname(self.view.file_name())

			# path (including file name) for the current document (may not be set).
			env['TM_FILEPATH'] = self.view.file_name()

		# the index in the current line which marks the caret's location. This index is zero-based and takes
		# the utf-8 encoding of the line (e.g. read as TM_CURRENT_LINE) into account. So to split a line into
		# what is to the left and right of the caret you could do:
		# echo "Left:  ${TM_CURRENT_LINE:0:TM_LINE_INDEX}"
		# echo "Right: ${TM_CURRENT_LINE:TM_LINE_INDEX}"
		(row, col) = self.view.rowcol(self.view.sel()[0].end())
		env['TM_LINE_INDEX'] = str(col)

		# the carets line position (counting from 1). For example if you need to work
		# with the part of the document above the caret you can set the commands input to "Entire Document"
		# and use the following to cut off the part below and including the current line:
		#   head -n$((TM_LINE_NUMBER-1))
		env['TM_LINE_NUMBER'] = str(row + 1)

		# the scope that the caret is inside. See scope selectors for information about scopes.
		# TODO TM_SCOPE

		# this will have the value YES if the user has enabled soft tabs, otherwise it has the value NO.
		# This is useful when a shell command generates an indented result and wants to match the users
		# preferences with respect to tabs versus spaces for the indent.
		if (self.view.settings().get("translate_tabs_to_spaces")):
			env['TM_SOFT_TABS'] = "YES"
		else:
			env['TM_SOFT_TABS'] = "NO"

		# the tab size as shown in the status bar. This is useful when creating commands which need to present
		# the current document in another form (Tidy, convert to HTML or similar) or generate a result which needs
		# to match the tab size of the document. See also TM_SOFT_TABS.
		env['TM_TAB_SIZE'] = str(self.view.settings().get("tab_size"))

		# write the entire buffer out to a temp file
		buffer_file = tempfile.NamedTemporaryFile();
		env['TM_BUFFER_FILEPATH'] = buffer_file.name;
		size = self.view.size();
		chunk = 1024
		start_pos = 0

		while start_pos < size:
			text = self.view.substr( sublime.Region(start_pos, start_pos + chunk) )
			buffer_file.write(text)
			start_pos = start_pos + chunk
		buffer_file.flush()

		p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, env=env, close_fds=True)
		result = (p.stdout.read() + p.stderr.read()).rstrip("\n\r");

		return result;

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
		template = self.process_template_with(template, self.start_cmd(), self.end_cmd(),lambda x:self.run_shell_command(x))

		# Then we run all shell commands.  Note that this can return snippet expansion
		template = self.process_template_with(template, self.start_python(), self.end_python(), lambda x: str(eval(x)))

		return template 

	# TODO: Make this more snippet like
	def current_word(self):
		return self.view.substr(self.view.word(self.view.sel()[0].end()));

	def current_line(self):
		return self.view.substr(self.view.line(self.view.sel()[0].end()));

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
