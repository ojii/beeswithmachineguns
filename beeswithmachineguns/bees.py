#!/bin/env python

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
import copy

from multiprocessing import Pool
import os
import socket
import time

import boto.ec2
import paramiko

EC2_INSTANCE_TYPE = 't1.micro'

# Utilities

def _get_pem_path(key):
    return os.path.expanduser('~/.ssh/%s.pem' % key)

def _get_region(zone):
    region_name = zone[:-1]
    region = boto.ec2.get_region(region_name)
    if not region:
        valid_regions = ', '.join((r.name for r in boto.ec2.regions()))
        print '%s does not appear to be a valid region.' % region_name
        print 'Valid regions are: %s' % valid_regions
        return False
    else:
        return region

# Methods

def up(count, group, zone, image_id, username, key_name):
    """
    Startup the load testing server.
    """
    count = int(count)

    pem_path = _get_pem_path(key_name)

    if not os.path.isfile(pem_path):
        print 'No key file found at %s' % pem_path
        return False

    region = _get_region(zone)
    if not region:
        return False
    print 'Connecting to the hive.'
    ec2_connection = region.connect()

    print 'Attempting to call up %i bees.' % count

    reservation = ec2_connection.run_instances(
        image_id=image_id,
        min_count=count,
        max_count=count,
        key_name=key_name,
        security_groups=[group],
        instance_type=EC2_INSTANCE_TYPE,
        placement=zone)

    print 'Waiting for bees to load their machine guns...'

    instance_ids = []

    for instance in reservation.instances:
        instance.update()
        while instance.state != 'running':
            print '.'
            time.sleep(5)
            instance.update()

        instance_ids.append(instance.id)

        print 'Bee %s is ready for the attack.' % instance.id

    ec2_connection.create_tags(instance_ids, { "Name": "a bee!" })

    print 'The swarm has assembled %i bees.' % len(reservation.instances)

    return {
        'username': str(username),
        'key-name': str(key_name),
        'zone': str(zone),
        'instances': [str(instance.id) for instance in reservation.instances],
    }

def down(username, key_name, zone, instance_ids):
    """
    Shutdown the load testing server.
    """
    if not instance_ids:
        print 'No bees have been mobilized.'
        return

    region = _get_region(zone)
    if not region:
        return
    print 'Connecting to the hive.'
    ec2_connection = region.connect()

    print 'Calling off the swarm.'

    terminated_instance_ids = ec2_connection.terminate_instances(
        instance_ids=instance_ids)

    print 'Stood down %i bees.' % len(terminated_instance_ids)

def _attack(params):
    """
    Test the target URL with requests.

    Intended for use with multiprocessing.
    """
    print 'Bee %i is joining the swarm.' % params['i']
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            params['instance_name'],
            username=params['username'],
            key_filename=_get_pem_path(params['key_name']))

        print 'Bee %i is mounting his machine gun!' % params['i']

        sftp = client.open_sftp()
        sftp.put(params['battleplan']['script'], 'attack.py')
        sftp.put(params['battleplan']['requirements'], 'requirements.txt')
        sftp.close()

        print 'Bee %i is firing his machine gun. Bang bang!' % params['i']

        stdin, stdout, stderr = client.exec_command('virtualenv env')
        print stdout.read()
        print stderr.read()
        stdin, stdout, stderr = client.exec_command('env/bin/python `which pip` install -r requirements.txt')
        print stdout.read()
        print stderr.read()
        stdin, stdout, stderr = client.exec_command('env/bin/python attack.py %(users)s %(ssl-ratio)s %(messages)s %(min-pause)s %(max-pause)s %(min-length)s %(max-length)s %(target-host)s %(target-port)s %(target-ssl-port)s %(target-channel)s %(password)s %(beenum)s' % params['battleplan'])
        print stdout.read()
        print stderr.read()

        print 'Bee %i is out of ammo.' % params['i']

        client.close()

        return None
    except socket.error, e:
        print "SOMETHING FAILED!"
        import traceback; traceback.print_exc()
        return e

def attack(username, key_name, zone, instance_ids, battleplan):
    """
    Test the root url of this site.
    """
    if not instance_ids:
        print 'No bees are ready to attack.'
        return

    region = _get_region(zone)
    if not region:
        return
    print 'Connecting to the hive.'
    ec2_connection = region.connect()

    print 'Assembling bees.'

    reservations = ec2_connection.get_all_instances(instance_ids=instance_ids)

    instances = []

    for reservation in reservations:
        instances.extend(reservation.instances)

    instance_count = len(instances)
    requests_per_instance = int(float(battleplan['messages']) / instance_count)
    connections_per_instance = int(float(battleplan['users']) / instance_count)

    print 'Each of %i bees will fire %s rounds, %s at a time.' % (instance_count, requests_per_instance, connections_per_instance)
    print '%d%% of the bees will connect via SSL' % (battleplan['ssl-ratio'] * 100)

    params = []

    for i, instance in enumerate(instances):
        plan = copy.deepcopy(battleplan)
        plan['users'] = connections_per_instance
        plan['messages'] = requests_per_instance
        plan['beenum'] = i
        params.append({
            'i': i,
            'instance_id': instance.id,
            'instance_name': instance.public_dns_name,
            'username': username,
            'key_name': key_name,
            'battleplan': plan,
        })

    print 'Organizing the swarm.'

    # Spin up processes for connecting to EC2 instances
    pool = Pool(len(params))
    pool.map(_attack, params)

    print 'Offensive complete.'

    print 'The swarm is awaiting new orders.'
