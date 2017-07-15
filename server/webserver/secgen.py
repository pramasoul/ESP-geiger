"""Secrets Generator.

Usage:
  secgen [options] create-sgs [-f <file>]
  secgen [options] create [-n <number>] (--sgs=<sgs> | --sgs-file=<filename>) [-f <file>]
  secgen [options] validate (--sgs=<sgs> | --sgs-file=<filename>) [-f <file>]
  secgen -h | --help
  secgen --version

Options:
  -h, --help                    Show this screen.
  -f <file>, --file=<file>      file to use instead of STDOUT / STDIN.
  -n <number>                   How many to create [default: 1]
  -v, --verbose                 Be verbose in describing what's happening
"""
# WARNING: Avoid tabs in the docstring, they distress the docopt parser

__version__ = '0.1'

import hashlib
import json
import os
import sys
from binascii import hexlify, unhexlify
from docopt import docopt


def hashit(*args):
    m = hashlib.sha256()
    for v in args:
        if isinstance(v, str):
            v = v.encode('UTF8')
        m.update(v)
    return m.digest()

class SecretAgent:
    def __init__(self, sgs=None):
        self.sgs = sgs

    def load_secret_generating_secret(self, f):
        d = json.load(f)
        self.sgs = unhexlify(d['secret'])

    def save_secret_generating_secret(self, f):
        json.dump({ 'secret': hexlify(self.sgs).decode('ASCII') }, f)
        f.write('\n')

    def hint_secret(self):
        # Generate a random (hint, shared_secret) pair
        hint = os.urandom(32)
        return hint, hashit(self.sgs, 'to produce a secret from a hint', hint)

    def validate_hint_secret(self, hint, secret):
        return secret == hashit(self.sgs, 'to produce a secret from a hint', hint)

    def json_ready_hint_secret(self):
        return tuple(hexlify(v).decode('ASCII') for v in self.hint_secret())

def main():
    args = docopt(__doc__, version=__version__)
    if args['--verbose']:
        print(args)

    if args['--sgs']:
        sa = SecretAgent(unhexlify(args['--sgs']))
    if args['--sgs-file']:
        sa.load_secret_generating_secret(open(args['--sgs-file']))

    if args['create-sgs'] or args['create']:
        outf = args['--file'] and open(args['--file'], 'w') or sys.stdout
        if args['create-sgs']:
            sa.sgs = os.urandom(32)
            sa.save_secret_generating_secret(outf)
        elif args['create']:
            hinted_secrets = list(sa.json_ready_hint_secret() for i in range(int(args['-n'])))
            json.dump(hinted_secrets, outf, indent=2)
            outf.write('\n')
        outf.flush()

    elif args['validate']:
        inf = args['--file'] and open(args['--file'], 'r') or sys.stdin
        hinted_secrets = [map(unhexlify, t) for t in json.load(inf)]
        n_good = sum(1 for h,s in hinted_secrets if sa.validate_hint_secret(h, s))
        n_hs = len(hinted_secrets)
        if n_good == n_hs:
            print("All %d (hint,secret) pairs are good" % n_hs)
        else:
            print("%d of %d (hint,secret) pairs are bad" % (n_hs - n_good, n_hs))
            sys.exit(1)

if __name__ == '__main__':
    main()

    
