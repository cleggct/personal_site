# Rebuilding My Personal Site With 11ty
I recently redesigned my personal site again, this time switching
to using <a href="https://www.11ty.dev">11ty</a> to build my site.
I really like 11ty for the reason that it does a very good job of
getting out of the way and letting you focus on designing your site
without having to worry about wrangling with your build tools. For
a site that's mostly just pure HTML/CSS, 11ty is ideal
because it allows me to write powerful templates consisting of pretty
much just raw HTML/CSS, while also giving me lots of control over how
those templates are applied to the site content. This way, I never
have to rewrite the same HTML code anywhere and I can write templates
to generate pretty much any kind of content I want.

I also really like the way 11ty makes use of the directory structure of
a project to encapsulate relationships between different pieces of content.
I can have the content of all my posts as markdown files in a directory
called "posts," along with a JSON object tagging all files in that directory as
"posts" and telling 11ty to apply a particular template to them, while also
having a template in the base folder for generating an index page with links
to each of the pages tagged with "posts". Then when the site gets built, html
files are generated for each of the files from "posts" according to whatever
template we specified and placed in "output_dir/posts."
Additionally, an index.html file is generated in the base directory as an entry
point that neatly links to all the site content. Simple, and with our templates
and directory structure all set up, all we have to do is populate the site with
content in the form of markdown files. Everything else is handled by
11ty!

To summarize, 11ty is great because it represents a nice middle ground
between the power and flexibility that comes with using a really big and fancy
web development framework like react, and the simplicity of just working in
HTML/CSS.