# OpenShift SRE IRC Helper Function

## On-Call and Shift Lead Rotation

***

Provides the following commands:

* `.track`
  * Begins tracking on-call and shift lead rotations from PagerDuty
  * Becomes a [monitored](#channel-monitoring) channel
* `.untrack`
  * Stops tracking on-call and shift lead rotations for channel
  * Is no longer a [monitored](#channel-monitoring) channel
* `.shift-announce`
  * Will resume shift change announcements if previous stopped in the given channel
* `.shift-unannounce`
  * Will stop shift change announcements in the given channel
  * Still allows for benefits like `.shift` and topic changing (assuming proper privs)
* `.shift`
  * Lists the current on-call and shift leads for this rotation period
* `.monitored-channels`
  * Sends PRIVMSG of all channels currently monitored for on-call and shift lead rotations
  * Will only respond to bot admins
* `.snow`
  * Responds with the SNOW OpenShift SRE Service Request Form
  * https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form

## SNOW Ticket parsing

Any SNOW tickets detected in a message will reply with an automatic link to the SNOW ticket

    https://redhat.service-now.com/surl.do?n=<SNOW_ticket>


## CE&E Case parsing

Any SalesForce cases detected in a message will reply with an automatic message and link to the CE&E case

    https://access.redhat.com/support/cases/#/case/<cee_case>

## Karma

Specifying <nick>++ will increase a nick's karma, and <nick>-- will decrease a nick's karma.

    NOTE: Karma can only be increased or decreased every 10 seconds to prevent spamming

* `.karma`
  * Provides your own karma
* `.karma <nick>`
  * Provides karma of <nick>

## .all Announcements

* `.all <message>`
  * Will announce <message> to all nicks within the channel

## .msg Announcements

* `.msg <message>`
  * Will announce <message> to all nicks within .msg list
* `.msg-add <nick>`
  * Adds <nick> to .msg list
  * Will only respond to bot admins
* `.msg-delete <nick>`
  * Removes <nick> from .msg list
  * Will only respond to bot admins
* `.msg-deleteall [confirm]`
  * Removes *all* nicks from .msg list
  * If only acts if `confirm` is added in the command
  * Will only respond to bot admins
* `.msg-list`
  * Lists all nicks in .msg list


# Testing

## Google Sheets on-call integration

```
.shift-announce
    I'm not currently tracking this channel. Check out .help track

.track
    Not currently tracking an SRE on-call rotation.

.track https://docs.google.com/spreadsheets/d/1tm6Sx5sJvsPXHAhxoPdSs2ODCHwBquKJzn-ObgTeVRw/edit#gid=1539275069
    I can't seem to access that spreadsheet (https://docs.google.com/spreadsheets/d/1tm6Sx5sJvsPXHAhxoPdSs2ODCHwBquKJzn-ObgTeVRw/edit#gid=1539275069). Are you sure that the URl is correct and that <service_account_email> has been invited to that doc?

<Add service account email>

.track
    #wgordon is now tracking SRE on-call rotation

wgordon  <- Matches whatever channel name is being tracked
    <something similar to>
        Please reach out to the shift lead or on-call SRE
        ###
            Shift Lead: stobin
            Shift Secondary: Gábor Bürgés
            On-Call: Gábor Bürgés

.shift
    <something similar to>
    ###
        Shift Lead: stobin
        Shift Secondary: Gábor Bürgés
        On-Call: Gábor Bürgés

.monitored-channels
    <privmsg>
        <channel>

.shift-announce
    I'm already announcing in this channel.

.shift-unannounce
    I will no longer announce shift changes in this channel.
    Topic updates will still occur if I have the proper permissions.

.shift-announce
    I will resume announcements in this channel.

.untrack
    <channel> is no longer tracking SRE on-call rotations.

.untrack
    <channel> is not currently tracking SRE on-call rotations.

.monitored-channels
    <privmsg>
        No monitored channels.
```

## .all Announcing

```
.all test
    I don't have any users to send to. Try having an admin use `.all-add <nick>` to add someone.
```

## .msg Announcing

```
.msg-add test-nick
    The .msg list has been initialized, and test-nick has been added.

.msg test
    test-nick: test

.msg-list
    <privmsg>
        .all list users:
        test-nick

.msg-delete test-nick
    test-nick has been removed from the .msg list.

.msg test
    I don't have any users to send to. Try having an admin use `.msg-add <nick>` to add someone.

.msg-deleteall
    There are no users to delete.

.msg-add test-nick2
    test-nick2 has been added to the .msg list.

.msg-deleteall
    This is a destructive command that will remove 1 users from the .msg list.
    <nick>: If you still want to do this, please run: .amsg-deleteall confirm

.msg-deleteall confirm
    I've removed all users from the .msg list.

.msg-list
    There are no users in .msg list.
```

## Karma

```
.karma
    wgordon does not have any karma.

wgordon++
    You can't change your own karma.

sre-bot++
    sre-bot now has 1 karma.

sre-bot-- better-bot++
    sre-bot now has 0 karma.
    better-bot now has 1 karma.

.karma better-bot
    better-bot has 1 karma.
```

## Misc functionality

```
.snow
    https://url.corp.redhat.com/OpenShift-SRE-Service-Request-Form

.admins
    <privmsg>
        Current bot owner: wgordon
        No configured admins
        New admins can be added by creating a PR against https://github.com/openshift/openshift-ansible-ops/tree/prod/playbooks/adhoc/ircbot

RITM0220268
    https://redhat.service-now.com/surl.do?n=RITM0220268

01974620
    https://access.redhat.com/support/cases/#/case/01974620
```
