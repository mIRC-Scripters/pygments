"""
    pygments.lexers.mirc
    ~~~~~~~~~~~~~~~~~~~~~~

    Lexer for mIRC Scripting Language.

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
    	'state-code-content-01': [
    		(r'(?:([ \t]+)?(\{)(?:([ \t]+)(\n))?)', bygroups(Whitespace, Punctuation, Whitespace, Text), ('#pop', 'state-code-block')),
    		(r'([ \t]+|)', Whitespace, ('#pop', 'state-code-block-line')),
    	],
    	'state-code-block': [	
    		(r'^([ ]{2})', Whitespace, 'state-code-block-line'),
    		(r'[ \t]+', Whitespace, ('#pop', 'state-code-block-line')),
    		(r'\}', Punctuation, '#pop'),
    		(r'\n', Text),
    	],
        'state-code-block-line': [            
            (r'\n', Text, '#pop'),
            (r'([ ]{2})+', Whitespace),
            include('comments'),
            (r'(?:((?:else)?if|while)([ \t]+)(\())', bygroups(Keyword, Whitespace, Keyword), 'state-conditional-outer'),
            (r'(?:(else)([ \t]+))', bygroups(Keyword, Whitespace)),
          	(r'\{', Punctuation, '#push'),
          	(r'(?:(\})([ \t])*)', bygroups(Punctuation, Whitespace), '#pop'),
            include('variables'),
            include('identifiers'),
            (r'\[', Punctuation, 'state-eval-bracket'),
            include('goto-statements'),
            (r'(\S+)(?=([ \t]+)??)?', bygroups(Name.Function, Whitespace), ('#pop', 'state-command')),
            (r'.', Text),
        ],
        'state-eval-bracket': [
        	include('identifiers'),
        	include('variables'),
        	(r'\]', Punctuation, '#pop'),
        	(r'\[', Punctuation, '#push'),
        	(r'.', Text)
        ],
        'state-command': [
        	include('identifiers'),
        	include('variables'),
        	(r'\n|\}', Text, '#pop'),
        	(r'(?:([ \t]+)(\|)([ \t]+))', bygroups(Whitespace, Keyword, Whitespace), ('#pop', 'state-code-block-line')),
        	(r'.', Text),
        ],
        'state-conditional-outer': [
            (r'\(', Punctuation, 'state-conditional-inner'),
            include('operators'),
            (r'!', Punctuation),
            include('identifiers'),
            include('variables'),

            (r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
            (r'(?:(\))([ \t]+)?)', bygroups(Keyword, Whitespace), '#pop'),
            (r'.', String),
        ],
        'state-conditional-inner': [
            include('operators'),
            (r'!', Punctuation),
            include('identifiers'),
            include('variables'),
            (r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
            (r'\)', Punctuation, '#pop'),
            (r'\(', Punctuation, '#push'),
            (r'.', String),
        ],
        'state-conditional-iif-outer': [
            (r'\(', Punctuation, 'state-conditional-iif-inner'),
            include('operators'),
            (r'!|,', Punctuation),
            include('identifiers'),
            include('variables'),

            (r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
            (r'(?:(\))([ \t]+)?)', bygroups(Keyword, Whitespace), '#pop'),
            (r'.', String),
        ],
        'state-conditional-iif-inner': [
            include('operators'),
            (r'!', Punctuation),
            include('identifiers'),
            include('variables'),
            (r'(?:([ \t]+)(&&|\|\|)([ \t]+))', bygroups(Whitespace, Operator, Whitespace)),
            (r'\)', Punctuation, '#pop'),
            (r'\(', Punctuation, '#push'),
            (r'.', String),
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
        'variables': [
            (r'(?<![^( ,!])((?:%|&)[^\s),]+)', Name.Variable),
            (r'(?:([ \t]+)(=)([ \t]+))', Operator, ('#pop', 'state-var-assignment')),
        ],
        'identifiers': [
        	(r'(?:(?<![^( ,!])(\$iif)(\())', bygroups(Keyword, Keyword), 'state-conditional-iif-outer'),
            (r'(?:(?<![^( ,!])(\$[^\s(),]+)(\())', bygroups(Name.Function, Name.Function), 'state-identifier-content'),
            (r'(?:(?<![^( ,!])(\$[^\s(),]+))', Name.Function),
        ],
        'goto-statements': [
        	(r':\S+', Name.Label),
        	(r'(?:([ \t]+)(\|)([ \t]+))', Keyword, ('#pop', 'state-code-block-line')),
        ],
        'state-identifier-content': [
            include('identifiers'),
            include('variables'),

            (r',', Punctuation),
            (r'\)', Name.Function, '#pop'),
            (r'.', String),
        ],
        'state-var-assignment': [
        	include('variables'),
        	include('identifiers'),
        	(r'\[', Punctuation, 'state-eval-bracket'),
        	(r'\n', Text, '#pop'),
        	(r'[^\n]', Text),
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
        'root': [
        	# Comments below
            include('comments'),
            # Events below
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(agent|appactive|connect(fail)?|disconnect|dns|exit|(un)?load|(midi|mp3|play|song|wave)end|nick|nosound|u?notify|ping|pong|quit|start|usermode|options|resume|song|suspend):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:action|notice|(?:client)?text):(?:(%[^:]+)|[^:]+):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(active|input|tabcomp|mscroll):(\*|#[^:]*|\?|=|!|@[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(close|open):(\*|\?|=|!|@[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):dialog:[^:]+:(?:init|close|edit|sclick|dclick|menu|scroll|mouse|rclick|drop|\*|(%[^:]+)):(?:(%[^:]+)|[\d\-,\*]+):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):((un)?ban|(de)?help|(de|server)?op|(de)?owner|(de)?voice|invite|join|kick|(server|raw)?mode|part|topic|(de)?admin):(\*|#[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:chat|ctcpreply|error|file(?:rcvd|sent)|(?:get|send)fail|logon|serv|signal|snotice|sock(?:close|listen|open|read|write)|udp(?:read|write)|vcmd|wallops|download|(?:un)?zip):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):dccserver:(?:chat|send|fserve):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):hotlink:[^:]+:(?:\\*|#[^:]*|\?|=|!|@[^:]*|(%[^:]+)):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):(?:key(?:down|up)|char):(?:\\*|@[^:]*|(%[^:]+)):(?:\*|\d+(?:,\d+)*|(%[^:]+)):)', Name.Builtin, 'state-code-content-01'),
            (r'(?i)^(on(?:[ \t]+)(?:me:)?(?:[^ \t:]+):parseline:(?:\\*|in|out|(%[^:]+)):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content-01'),
            # RAW below
            (r'(?i)^(raw(?:[ \t]+)(?:[^ \t:]+):(?:(%[^:]+)|[^:]+):)', Name.Builtin, 'state-code-content-01'),
            # Aliases below
            (r'(?i)^(alias)([ \t]+)(-l[ \t]+)?(\S+)', bygroups(Name.Builtin, Whitespace, Generic.Strong, Name.Function), 'state-code-content-01'),
            # Groups below
            (r'^#(\S+[ \t]+(?:on|off|end))', Name.Label),

            # Catch all
			(r'.', Text),
        ],
    }