import re

'''
==========================
MARKDOWN TO HTML CONVERTER
==========================
My first attempt at building a Markdown --> HTML converter using Python's built-in string functions 
and the Python Regular Expression parser (the re module).

Built as part of CS50W - Project 1: Wiki

The instructions for Project 1 included: 
-------------------------------------------------------------------------------------------------------
Challenge for those more comfortable: If you’re feeling more comfortable, try implementing the Markdown 
to HTML conversion without using any external libraries, supporting headings, boldface text, unordered 
lists, links, and paragraphs. You may find using regular expressions in Python helpful.
-------------------------------------------------------------------------------------------------------

My converter works as follows:
There are two different types of Markdown tag (out of those in the list above): those that sit at the 
start of a line and affect the entire line (which I shall call "block" operations) and those that affect
a delineated section of text within a line (these I refer to as "inlne"). Block operations include 
Headings, List Items & Paragraphs; Inline operations include Emboldening & Hyperlinks.

There is a function to take care of the conversion for each separate operation.

There are also 2 controller functions: Block and Inline.

Control is passed first to the Block Controller, which takes each line from the Markdown text and passes
it to each block conversion function. Each of the functions returns either the converted string or False.
If Block Controller receives all False returns, that means it needs to be a HTML paragraph and the text 
is formatted accordingly.

It is also in the Block Controller where the <ul> tags are closed at the appropriate time by reference to
a global list_in_progress flag.

After each line has been passed through the block functions, and is therefore partially complete HTML,
(ie. complete at the "block level") the Inline Controller takes over and passes each line to each Inline 
function. These functions again return either the converted string or False. If Inline Controller receives 
all False returns then the text for that line is left unaltered.

Each of the converted lines, which now costitute properly formatted HTML, are built into a string that is
the HTML representation of the original Markdown text.

Matt Edwards
September 2020
'''

list_in_progress = False

def block_controller(text):
	''' The first controller that calls each of the block-level functions in turn to check 
	whether there is a Markdown tag that affects the whole line (ie. a header (h1 to h6) or
	a list item) or no Md tag, which means it's a paragraph. '''

	global list_in_progress # accessing the global variable to help with closing <ul> tags
	
	# if it's a blank line, leave it as such unless it follows a <li>, in which case </ul>
	if text.strip() == '':
		if list_in_progress:
			list_in_progress = False
			return '</ul>'
		return ''
	# check return values from headings and list item functions	
	heading = headings(text)
	list_item = ulli(text)

	if heading:
		# if it follows a <li> then close the <ul> before the heading
		if list_in_progress:
			list_in_progress = False
			return f"</ul>\n{heading}"
		else:
			return heading

	elif list_item:
		return list_item # <ul> is taken care of in the list item function
	
	# or else it's a paragraph
	else:
		# if it follows a <li> then close the <ul> before the heading
		if list_in_progress:
			list_in_progress = False
			return f"</ul>\n<p>{text.strip()}</p>"
		return f"<p>{text.strip()}</p>" # returns <p></p> structure


def inline_controller(text):
	''' Second controller called after every block element has been converted to HTML.
	This controls the inline matching / converting functions (ie. embolden and hyperlinks) '''
	# if it's a blank line, leave it as such
	if text.strip() == '':
		return ''

	# check return values from embolden and hyperlink functions
	bold = embolden(text)
	link = hyperlink(text)
	if bold:
		return bold
	elif link:
		return link
	# if neither, then return the text unaltered
	else:
		return text


def headings(text):
	''' Detects Markdown heading tags (ie, # to ###### at the start of a line for h1 to h6) 
	and converts to HTML equiv.'''
	if not text.startswith('#') or text.startswith('#######'):
		return False
	if text.startswith('######'):
		return f"<h6>{tidied(text, '#')}</h6>"
	if text.startswith('#####'):
		return f"<h5>{tidied(text, '#')}</h5>"
	if text.startswith('####'):
		return f"<h4>{tidied(text, '#')}</h4>"
	if text.startswith('###'):
		return f"<h3>{tidied(text, '#')}</h3>"
	if text.startswith('##'):
		return f"<h2>{tidied(text, '#')}</h2>"
	if text.startswith('#'):
		return f"<h1>{tidied(text, '#')}</h1>"
	return text


def ulli(text):
	''' Detects Markdown list tag (ie. * at the start of a line) and adds <li></li> tags. Uses
	a GLOBAL flag to indicate whether we are mid-list between rows to help manage the placement
	of the closing </ul> tag '''
	if not text.startswith('*'):
		return False

	# accessing the global variable to help with closing <ul> tags
	global list_in_progress
	if list_in_progress:
		return f"\t<li>{tidied(text, '*')}</li>" # no need for opening <ul>
	list_in_progress = True
	return f"<ul>\n\t<li>{tidied(text, '*')}</li>" # need to prefix with <ul>


def tidied(t, md_char):
	''' Utility function to remove Markdown tags and leading/trailing whitespace '''
	return t.replace(md_char, "").strip()


def embolden(text):
	''' Detects Markdown tag for embolden (ie. **text**) and adds <strong></strong> HTML
	tags in place of the two sets of double asterisks. '''
	matches = re.findall('(\*\*[a-zA-Z0-9.,!?\- ]+\*\*)', text)
	if not matches:
		return False

	# construct an array the same length as matches that will hold the <strong> tags
	# with the text in between - this whole construct referred to here as a slug
	slugs = [''] * len(matches)
	for i in range(len(matches)):
		slugs[i] = f"<strong>{matches[i].replace('**', '')}</strong>"

	# matched Md snippets within the whole line are then replaced with corresponding HTML slug
	for i in range(len(matches)):
		text = text.replace(matches[i], slugs[i])
	return text


def hyperlink(text):
	''' Detects Markdown structure for a hyperlink (ie. [Linktext](href text)) and converts
	it to fully formed HTML anchor tag <a></a> '''
	matches = re.findall('\[[a-zA-Z0-9-]+]\([a-zA-Z0-9\./_]+\)', text)
	if not matches:
		return False

	# construct an array the same length as matches that will hold the <a></a> tags with the
	# href and link text in the appropriate places - this whole construct referred to here as a slug
	slugs = [''] * len(matches)
	for i in range(len(matches)):
		# link text & href are extracted
		link_text = re.search('\[[a-zA-Z0-9-]+]', matches[i]).group()[1:-1]
		href = re.search('\([a-zA-Z0-9\./_]+\)', matches[i]).group()[1:-1]
		# and the slug is constructed
		slugs[i] = f"<a href='{href}'>{link_text}</a>"

	# matched Md snippets within the whole line are then replaced with corresponding HTML slug
	for i in range(len(matches)):
		text = text.replace(matches[i], slugs[i])
	return text	


path = './mdfiles/test.md'
with open(path, 'r') as f:
	entry = f.readlines()

block = []
for line in entry:
	block.append(block_controller(line))
inline = []
for line in block:
	inline.append(inline_controller(line))
html_output = ''
for line in inline:
	html_output += inline_controller(line)
	html_output += '\n'

print(html_output)

"""
===================================
Early attempts that were abandoned
===================================
def h1(text_in):
	pattern = '(^#[a-zA-Z0-9\. ]+)' # a pattern to match the Markdown string for Heading 1
	m = re.search(pattern, text_in)
	if not m:
		return text_in
	tidied = m.group(1).replace("#", "").strip()
	return f"<h1>{tidied}</h1>\n"

def h2(text_in):
	pattern = '(^##[a-zA-Z0-9\. ]+)' # a pattern to match the Markdwn string for Heading 2
	m = re.search(pattern, text_in)
	if not m:
		return text_in
	tidied = m.group(1).replace("#"*2, "").strip()
	return f"<h2>{tidied}</h2>\n"

def h3(text_in):
	pattern = '(^###[a-zA-Z0-9\. ]+)' # a pattern to match the Markdwn string for Heading 3
	m = re.search(pattern, text_in)
	if not m:
		return text_in
	tidied = m.group(1).replace("#"*3, "").strip()
	return f"<h3>{tidied}</h3>\n"

def h1_s(text_in):
	''' An arguably simpler way to achieve the same thing as the h1 function but using Python's
	native str functions. Also, probably quicker than a regular expression because it doesn't
	involve use of an extra parser
	**** BUT ****
	Checking for a single # at the start will also catch multiple #'s. Need functionality to 
	catch up to 6 # symbols and re-write accordingly. Any more than 6 should just be left alone.
	 '''
	if not text_in.startswith('#'):
		return text_in
	tidied = text_in.replace("#", "").strip()
	return f"<h1>{tidied}</h1>\n"

def ulli(text_in):
	global list_in_progress
	pattern = '(^\*[a-zA-Z0-9\. ]+)' # a pattern to match the Markdown string for a list item
	m = re.search(pattern, text_in)
	if not m:
		return False
	if not list_in_progress:
		list_in_progress = True
		return f"<ul>\n<li>{tidied(m.group(1), '*')}</li>"
	return f"<li>{tidied(m.group(1), '*')}</li>\n"
"""
