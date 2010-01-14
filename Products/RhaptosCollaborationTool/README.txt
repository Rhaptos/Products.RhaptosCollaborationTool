RhaptosCollaborationTool

  This Zope Product is part of the Rhaptos system
  (http://software.cnx.rice.edu)

  RhaptosCollaborationTool provides a tool for a member to invite
  other memebers to join him/her in some role on a particular piece
  content of content.  Role changes are only made if the other person
  accepts the invitation.


Future plans

  - Use DCWorkflow.

  - Don't use mixin if we can avoid it

  - Move required skin files here

  - The optional roles information that is stored on the
    CollaborationTool should really be available to be modified via
    ZMI pages.  There needs to be an add/delete/modify page that can
    alter them.  This should also push changes to the database when
    saved, because some information about roles is saved there as well.


NOTES:

Two-phase role changes

  - Adding (or removing?) anyone as author/maintainer/licensor of a
    module requires that persons agreement, and in the case of
    author/licensor a click-through license agreement

  - Upon login, users should get notified that they have pending
    requests or that pending requests have been acceptd/rejected

Data flow

  - User A edits module m0 in workgroup w1, requesting that User B be
    added an Author.

  - The request information (m0, w1, User A, User B, 'Author') is
    stored in a collaboration tool (only one in the site) and given a
    request ID r0

  - When User B next logs in, he/she receives notification that User A
    has requested him/her be listed as an 'Author' on m0

  - User B accepts/declines the role, possibly sending a comment to
    User A

  - The status of the request r0 (and optional comment) is stored in
    the collaboration tool

  - If accepted, User B is given the 'Author' role on module m0 in
    workgroup w1

  - When User A next logs in, he/she receives notification that User A
    has accepted/declined the 'Author' role

