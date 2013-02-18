ddsc-socket
==========================================

Introduction

Usage, etc.


Post-nensskel setup TODO
------------------------

Here are some instructions on what to do after you've created the project with
nensskel.

- Check https://github.com/nens/ddsc-socket/settings/collaboration if the team
  "Nelen & Schuurmans" has access.

- Add a new jenkins job at
  http://buildbot.lizardsystem.nl/jenkins/view/djangoapps/newJob or
  http://buildbot.lizardsystem.nl/jenkins/view/libraries/newJob . Job name
  should be "ddsc-socket", make the project a copy of the existing "lizard-wms"
  project (for django apps) or "nensskel" (for libraries). On the next page,
  change the "github project" to ``https://github.com/nens/ddsc-socket/`` and
  "repository url" fields to ``git@github.com:nens/ddsc-socket.git`` (you might
  need to replace "nens" with "lizardsystem"). The rest of the settings should
  be OK.
