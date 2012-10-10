"""
The MIT License

Copyright (c) 2010 The Chicago Tribune & Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import os
import bees
from docopt import docopt
import sys
import yaml


doc = """
Bees with Machine Guns (on IRC)

A utility for arming (creating) many bees (small EC2 instances) to attack
(load test) targets (IRC servers).

Usage:
    bees up [--config=<config>] [--swarm=<swarm>]
    bees attack <battleplan> [--swarm=<swarm>]
    bees down [--swarm=<swarm>]

Options:
    -h, --help            show this help message and exit.
    --config=<config>     config file to use [default: bees.yaml].
    --swarm=<swarm>       swarm file to use [default: .swarm].
"""

DEFAULTS = {
    'servers': 5,
    'group': 'public',
    'zone': 'us-east-1d',
    'image-id': 'ami-ff17fb96',
    'username': 'newsapps',
}

def up(config, swarmpath):
    swarm = bees.up(config['servers'], config['group'], config['zone'], config['image-id'], config['username'], config['key-name'])
    if not swarm:
        sys.exit(1)
    with open(swarmpath, 'w') as fobj:
        yaml.dump(swarm, fobj)

def down(swarm, swarmpath):
    bees.down(swarm['username'], swarm['key-name'], swarm['zone'], swarm['instances'])
    os.remove(swarmpath)


def attack(swarm, battleplan):
    bees.attack(swarm['username'], swarm['key-name'], swarm['zone'], swarm['instances'], battleplan)

def main():
    arguments = docopt(doc)

    if arguments['attack']:
        if not os.path.exists(arguments['<battleplan>']):
            print "Battle plan %r not found!" % arguments['<battleplan>']
            sys.exit(1)
        if not os.path.exists(arguments['--swarm']):
            print "Swarm file %r not found!" % arguments['--swarm']
            sys.exit(1)
        with open(arguments['<battleplan>']) as fobj:
            battleplan = yaml.load(fobj)
        with open(arguments['--swarm']) as fobj:
            swarm = yaml.load(fobj)
        attack(swarm, battleplan)
    elif arguments['up']:
        if not os.path.exists(arguments['--config']):
            print "Config file %r not found!" % arguments['--config']
            sys.exit(1)
        config = {}
        config.update(DEFAULTS)
        with open(arguments['--config']) as fobj:
            config.update(yaml.load(fobj))
        if os.path.exists(arguments['--swarm']):
            print "Swarm already assembled!"
            sys.exit(1)
        up(config, arguments['--swarm'])
    elif arguments['down']:
        if not os.path.exists(arguments['--swarm']):
            print "Swarm file %r not found!" % arguments['--swarm']
            sys.exit(1)
        with open(arguments['--swarm']) as fobj:
            swarm = yaml.load(fobj)
        down(swarm, arguments['--swarm'])
