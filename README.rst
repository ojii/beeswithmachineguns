################################
Bees with Machine Guns (on IRC)!
################################

The caveat! (PLEASE READ!)
**************************

If you decide to use the Bees, please keep in mind the following important caveat:
they are, more-or-less a distributed denial-of-service attack in a fancy package and, therefore,
if you point them at any server you don’t own you will behaving **unethically**, have your Amazon Web
Services account **locked-out**, and be **liable** in a court of law for any downtime you cause.

You have been warned.

Config
******

Create a config file ``bees.yaml`` with the following key/values:

* ``key-name``: Your key pair name for EC2 (required!)
* ``servers``: How many servers you want (default: 5)
* ``group``: EC2 security group (default: public)
* ``zone``: EC2 zone (default: us-east-1d)
* ``image-id``: EC2 image id (default: ami-ff17fb96)
* ``username``: (default: newsapp, don't change this...)

Battleplan
**********

Create a battleplan (``<planname>.yaml``) file with the following key/values:

* ``script``: (Local) path to script to use for attack
* ``requirements``: A pip requirements file for the environment.
* ``users``: Amount of users (total)
* ``ssl-ratio``: Ratio of users that connect via SSL (float)
* ``messages``: How many messages to send (total)
* ``min-pause``: Minimum pause (in seconds) between messages
* ``max-pause``: Maximum pause (in seconds) between messages
* ``min-length``: Minimum length of messages
* ``max-length``: Maximum length of messages
* ``target-host``: Hostname of the target server
* ``target-port``: Port of the target server
* ``target-ssl-port``: SSL port of the target server
* ``target-channel``: Channel to connect to on the target server
* ``password``: Password for users to auth


Attack script
*************

The attack script is called with the following arguments (in order):

* Amount of connections this bee should open
* Ratio of users that should connect via SSL (float)
* Amount of messages this bee should send
* Minimum pause between messages (in seconds, float)
* Maximum pause between messages (in seconds, float)
* Minimum length of messages
* Maximum length of messages
* Host name of the IRC server
* Port on the IRC server
* SSL port on the IRC server
* Target channel
* Password
* Bee ID (number)
