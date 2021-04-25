"""
	pygments.lexers.mirc
	~~~~~~~~~~~~~~~~~~~~~~

	Lexer for mIRC Scripting Language.

"""

"""
	Note: definitions in state-menu-block-* refer to 
	state-code-block-*; problems?
"""

import re

from pygments.lexer import Lexer, RegexLexer, bygroups, default, words, \
	do_insertions, include
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
	Number, Punctuation, Generic, Whitespace

__all__ = ['MircLexer']

class MircLexer(RegexLexer):

	name = 'mIRC'
	aliases = ['mirc']
	filenames = ['*.mrc']

	tokens = {
		'state-code-content': [
			(r'\n', Text, '#pop'),

			(r'(?:(\{)(?:([ \t]+)?(\n)))', bygroups(Punctuation, Whitespace, Text), 'state-code-block'),
			
			include('standard-code'),

			(r'(?:([ \t]+)(\|)([ \t]+))', bygroups(Whitespace, Punctuation, Whitespace), 'state-code-singleline'),

			(r'(\S+)', Name.Function, 'state-function'),
		],
		'state-code-block': [
			(r'^([ ]{2})+', Whitespace, 'state-code-singleline'),

			(r'^\}', Punctuation, '#pop'),
			
			(r'\n', Text),
		],
		'state-code-singleline': [
			(r'^([ ]{2})+', Whitespace),

			include('comments'),

			include('standard-code'),

			(r'(?:([ \t]+)(\|)([ \t]+))', bygroups(Whitespace, Punctuation, Whitespace), ('#pop', 'state-code-singleline')),

			(r'(\S+)', Name.Function, ('#pop', 'state-function')),

			(r'\n', Text, '#pop'),
		],
		'standard-code': [
			(r'(?:((?:else)?if|while)([ \t]+)(\())', bygroups(Keyword, Whitespace, Keyword), 'state-conditional-outer'),
			(r'(?:(else)([ \t]+))', bygroups(Keyword, Whitespace)),
			
			(r'(?:(\{)([ \t]+)?)', bygroups(Punctuation, Whitespace), '#push'),
			(r'(?:(?<!^)([ \t]+)?(\}))', Punctuation, '#pop'),

			include('variables'),
			include('identifiers'),
			include('goto-statements'),
		],
		'state-function': [
			include('variables'),
			include('identifiers'),

			(r'(?:([ \t]+)(\|)([ \t]+))', bygroups(Whitespace, Punctuation, Whitespace), ('#pop', 'state-code-singleline')),
			(r'(?=([ \t]+)\})', Whitespace, '#pop'),
			(r'$', Text, '#pop'),

			(r'.', Text),
		],
		'whitespace': [

			(r'[ \t]', Whitespace),
		],
		'goto-statements': [
			(r':\S+', Name.Label),
		],
		'comments':[
			(r';.*$', Comment.Singleline),  
			(r'/\*.*', Comment.Multiline, 'state-comments-multiline'),
		],
		'state-comments-multiline': [
			(r'[^*]', Comment.Multiline),
			(r'\*/\s*', Comment.Multiline, '#pop'),
			(r'[*]', Comment.Multiline),
		],
		'state-conditional-outer': [
			(r'\(', Punctuation, 'state-conditional-inner'),
			include('operators'),
			(r'!(?:(?=[%$&]))', Punctuation),
			include('identifiers'),
			include('variables'),

			(r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
			(r'(?:(\))([ \t]+))', bygroups(Keyword, Whitespace), '#pop'),
			(r'.', String),
		],
		'state-conditional-inner': [
			include('operators'),
			(r'!(?:(?=[%$&]))', Punctuation),
			include('identifiers'),
			include('variables'),
			(r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
			(r'\)', Punctuation, '#pop'),
			(r'\(', Punctuation, '#push'),
			(r'.', String),
		],
		'variables': [
			(r'(?:(?<![^(\s,!])((?:%|&)[^)\s,]+)(?:([ \t]+)(=)([ \t]+)))', bygroups(Name.Variable, Whitespace, Operator, Whitespace), 'state-variable'),
			(r'(?:(?<![^(\s,!])((?:%|&)[^)\s,]+))', Name.Variable),
		],
		'state-variable': [
			(r',', Punctuation, '#pop'),
			(r'(?:([ \t]+)(\|)([ \t]+))', bygroups(Whitespace, Punctuation, Whitespace), '#pop'),
			(r'(?=([ \t]+)\})', Whitespace, '#pop'),
			(r'$', Text, '#pop'),

			include('identifiers'),
			include('variables'),

			(r'.', Text),
		],
		'state-eval-bracket': [
			include('identifiers'),
			include('variables'),
			(r'\]', Punctuation, '#pop'),
			(r'\[', Punctuation, '#push'),
			(r'.', Text)
		],
		'identifiers': [
			(r'(?:(?<![^( ,!])(\$iif)(\())', bygroups(Keyword, Keyword), 'state-conditional-iif-outer'),
			(r'(?:(?<![^( ,!])(\$[^\s(),]+)(\())', bygroups(Name.Function, Name.Function), 'state-identifier-content'),
			(r'(?:(?<![^( ,!])(\$[^\s(),]+))', Name.Function),
		],
		'state-identifier-content': [
			include('identifiers'),
			include('variables'),
			(r',', Punctuation),
			(r'\)', Name.Function, '#pop'),
			(r'[^,)]', String),
		],
		'operators': [
			(words(('==', '!=', '<', '>', '<=', '>=', '//', '\\\\', '&', '!&',
				'===', '!==', '!==='), 
				prefix=r'[ \t]+', suffix=r'[ \t]+'), 
				Operator),
			(words(('isin', 'isincs', 'iswm', 'iswmcs'),
				prefix=r'[ \t]+!?', suffix=r'[ \t]+'),
				Operator.Word),
			(words(('isnum', 'isletter', 'isalnum', 'isalpha', 'islower', 'isupper'),
				prefix=r'[ \t]+!?', suffix=r'[ \t]*?'),
				Operator.Word),
			(words(('ison', 'isop', 'ishop', 'isvoice', 'isreg', 'ischan', 'isban', 'isquiet', 
				'isaop', 'isavoice', 'isignore', 'isprotected', 'isnotify', 'isadmin', 
				'isowner', 'isquiet', 'isurl', ),
				prefix=r'[ \t]+!?', suffix=r'[ \t]*?'),
				Operator.Word),
		],
		'state-conditional-iif-outer': [
			(r'\(', Punctuation, 'state-conditional-iif-inner'),
			include('operators'),
			(r'!(?=[%$&])|,', Punctuation),
			include('identifiers'),
			include('variables'),

			(r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
			(r'(?:(\))([ \t]+)?)', bygroups(Keyword, Whitespace), '#pop'),
			(r'.', String),
		],
		'state-conditional-iif-inner': [
			include('operators'),
			(r'!(?:(?=[%$&]))', Punctuation),
			include('identifiers'),
			include('variables'),
			(r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
			(r'\)', Punctuation, '#pop'),
			(r'\(', Punctuation, '#push'),
			(r'.', String),
		],
		'state-dialog-content': [
			(r'(?i)^(?:([ \t]+)(title|icon|size|option|text|edit|button|check|radio|box|scroll|list|combo|icon|link|tab|menu|item)([ \t]+))', bygroups(Whitespace, Name.Other, Whitespace)),
			include('comments'),
			include('variables'),
			include('identifiers'),
			(r'"[^\n"]*"', String.Double),
			(r'\d+', Number.Integer),
			(r'[ \t]+', Whitespace),
			(r',', Punctuation),
			(r'\}', Punctuation, '#pop'),
			(r'\n', Text),
			(r'.', Text),
		],
		'root': [
			# Comments below
			include('comments'),
			# Events below
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(agent|appactive|connect(fail)?|disconnect|dns|exit|(un)?load|(midi|mp3|play|song|wave)end|nick|nosound|u?notify|ping|pong|quit|start|usermode|options|resume|song|suspend):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:action|notice|(?:client)?text):(?:(%[^:]+)|[^:]+):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(active|input|tabcomp|mscroll):(\*|#[^:]*|\?|=|!|@[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(close|open):(\*|\?|=|!|@[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):dialog:[^:]+:(?:init|close|edit|sclick|dclick|menu|scroll|mouse|rclick|drop|\*|(%[^:]+)):(?:(%[^:]+)|[\d\-,\*]+):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):((un)?ban|(de)?help|(de|server)?op|(de)?owner|(de)?voice|invite|join|kick|(server|raw)?mode|part|topic|(de)?admin):(\*|#[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:chat|ctcpreply|error|file(?:rcvd|sent)|(?:get|send)fail|logon|serv|signal|snotice|sock(?:close|listen|open|read|write)|udp(?:read|write)|vcmd|wallops|download|(?:un)?zip):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):dccserver:(?:chat|send|fserve):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):hotlink:[^:]+:(?:\\*|#[^:]*|\?|=|!|@[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:key(?:down|up)|char):(?:\\*|@[^:]*|(%[^:]+)):(?:\*|\d+(?:,\d+)*|(%[^:]+)):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):parseline:(?:\\*|in|out|(%[^:]+)):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content'),
			(r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:chat|ctcpreply|error|file(?:rcvd|sent)|(?:get|send)fail|logon|serv|signal|snotice|sock(?:close|listen|open|read|write)|udp(?:read|write)|vcmd|wallops|download|(?:un)?zip):(?:(%[^:]+)|[^:]+):),', bygroups(Name.Builtin, Name.Variable), 'state-code-content'),
			# CTCP below
			(r'(?i)^(ctcp(?:[ \t]+)(?:[^ \t:]+)+:(?:(%[^:]+)|[^:]+):(?:\*|#.*|\?|(%[^:]+)):)', bygroups(Name.Builtin, Name.Variable, Name.Variable), 'state-code-content'),
			# RAW below
			(r'(?i)^(raw(?:[ \t]+)(?:[^ \t:]+):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content'),
			# Aliases below
			(r'(?i)^(?:(alias)([ \t]+)(?:(-l)([ \t]+))?(\S+)([ \t]+))', bygroups(Name.Builtin, Whitespace, Generic.Strong, Whitespace, Name.Function, Whitespace), 'state-code-content'),
			# Groups below
			(r'^#(\S+[ \t]+(?:on|off|end))', Name.Label),
			# DIALOGS below
			(r'(?i)^(?:(dialog)([ \t]+)(?:(-l)([ \t]+))?(\S+)([ \t]+)(\{))', bygroups(Name.Builtin, Whitespace, Generic.Strong, Whitespace, Name.Function, Whitespace, Punctuation), 'state-dialog-content'),
			# MENUS
			# (r'(?i)^(?:(menu)([ \t]+)((?:status|channel|query|nicklist|menubar|(?:channel)?link|@[^ \t,]+|\*)(?:,(?:status|channel|query|nicklist|menubar|(?:channel)?link|@[^\t,]+))*|\*)([ \t]+)(\{))', bygroups(Name.Builtin, Whitespace, Generic.Strong, Whitespace, Punctuation), 'state-menu-block-outer'),
			# Catch all
			# (r'.', Text),
		],
	}