"""
The :class:`Module` class encapsulates a single Python
"""

import os
from pythonparser import source, diagnostic, parse_buffer
from . import prelude, types, transforms

class Module:
    def __init__(self, source_buffer, engine=diagnostic.Engine(all_errors_are_fatal=True)):
        asttyped_rewriter = transforms.ASTTypedRewriter(engine=engine)
        inferencer = transforms.Inferencer(engine=engine)
        int_monomorphizer = transforms.IntMonomorphizer(engine=engine)

        parsetree, comments = parse_buffer(source_buffer, engine=engine)
        typedtree = asttyped_rewriter.visit(parsetree)
        inferencer.visit(typedtree)
        int_monomorphizer.visit(typedtree)
        inferencer.visit(typedtree)

        self.name = os.path.basename(source_buffer.name)
        self.globals = asttyped_rewriter.globals

    @classmethod
    def from_string(klass, source_string, name="input.py", first_line=1):
        return klass(source.Buffer(source_string + "\n", name, first_line))

    @classmethod
    def from_filename(klass, filename):
        with open(filename) as f:
            return klass(source.Buffer(f.read(), filename, 1))

    def __repr__(self):
        printer = types.TypePrinter()
        globals = ["%s: %s" % (var, printer.name(self.globals[var])) for var in self.globals]
        return "<artiq.compiler.Module %s {\n  %s\n}>" % (repr(self.name), ",\n  ".join(globals))
