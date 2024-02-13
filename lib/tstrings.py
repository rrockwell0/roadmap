import re
import os


def bracket(instring):
    """replaces double brackets [[ ]] with single curly brackets { }"""
    return instring.replace('[[', '{').replace(']]', '}')


class Tstr(str):
    def __init__(self, template):
        if os.path.exists(template):
            template = open(template, 'r').read()
        str.__init__(template)
        self.template = template
        self.output = template

    def __str__(self):
        return self.output

    def eval(self, locals, include_bracket=False):
        self.output = self.template
        targets = set(re.findall(r"\{([^{]*?)\}", self.template.replace('{{', '').replace('}}', '')))
        for target in targets:
            if target in locals:
                self.output = self.output.replace("{"+str(target)+"}", str(locals[target]))
        if include_bracket:
            self.output = bracket(self.output)


if __name__ == '__main__':
    example = Tstr("See John {verb}.")
    verb = "run"
    example.eval(locals())
    print(example)
    print(type(example))
