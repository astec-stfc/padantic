from yaml.reader import Reader
from yaml.scanner import Scanner
from yaml.parser import Parser
from yaml.composer import Composer
from Importers.MySafeConstructor import MySafeConstructor
from yaml.resolver import Resolver


class MySafeLoader(Reader, Scanner, Parser, Composer, MySafeConstructor, Resolver):

    def __init__(self, stream):
        Reader.__init__(self, stream)
        Scanner.__init__(self)
        Parser.__init__(self)
        Composer.__init__(self)
        MySafeConstructor.__init__(self)
        Resolver.__init__(self)
