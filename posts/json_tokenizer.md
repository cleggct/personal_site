# Parsing JSON to HTML on the Fly

I wrote this code for tokenizing and parsing JSON to HTML on the fly.
It was meant as part of a system which would stream data from a backend
and render that data on a webpage in realtime. It didn't end up getting
used for its intended purpose so I decided to leave it up here. It was
a fun bit of code to write. I basically went about it by just looking at 
<a href="https://ecma-international.org/publications-and-standards/standards/ecma-404/">the ECMA specification for the JSON format</a>. I knew the tokenizer needed to be able to process
each symbol listed in there, so I designed it to do just that. The
tokenizer works by reading input one character at a time and basically
either categorizes the current character as one of the token types, or
otherwise modifies the state of the tokenizer to indicate that it is
reading some sort of continuous value like a string or int literal.
In this fashion, as characters of JSON data stream in, they
are mapped to one of a set of basic tokens which can then be
read by your parser to generate whatever kind of output you want in
response to each token. This saves the user from having to write
their own code to handle cases like checking when the same symbol is 
used for multiple distinct operations, reading a literal value
from stream data, etc. Of course, a project like this is useless
without unit tests. I have included those as well.

<a href="/src/json_tokenizer.py">json_tokenizer.py</a>

<a href="/src/json_tokenizer_test.py">json_tokenizer_test.py</a>