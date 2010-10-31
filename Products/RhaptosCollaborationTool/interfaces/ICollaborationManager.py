"""
Interface for RhaptosModuleEditor Product

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from zope.interface import Interface, Attribute

class CollaborationManager(Interface):
    """Interface for managing collaborations"""

    default_roles = Attribute('default_roles', 'Sequence of collaboration roles')

    def requestCollaboration(user, roles):
        """Set the roles for a user, if necessary making a collaboration request"""

    def getPendingCollaborations():
        """Return a mapping of usernames to pending collaboration requests for this object"""

    def getCollaborators():
        """Return the list of usernames who are collaborating on this object"""

    def getCollaborationRoles():
        """Return the sequence of collaboration roles"""

    def editCollaborationRequest(id, roles):
        """Change the roles of the collaboration request having the specified id"""

    def setCollaborationRoles(user, roles):
        """Set the collaboration roles for the specified user (does not affect other Zope roles)"""

    def clearCollaborations():
        """Remove all collaboration roles and cancel requests"""
        
    def deleteCollaborationRequests():
        """Remove all collaboration requests for this object"""
