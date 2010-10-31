# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# initially written by J Cameron Cooper, 11 June 2003
# concept with Brent Hendricks, George Runyan

""" Groups tool interface

Goes along the lines of portal_membership, but for groups."""

from zope.interface import Attribute, Interface

class portal_collaboration(Interface):
    """Defines an interface for a tool that allows people to agree to collaborate"""

    id = Attribute('id','Must be set to "portal_collaboration"')

    def searchCollaborations(user=None, requester=None, status=None):
        """Find collaboration requests with the specified parameters"""


class ICollaborationRequest(Interface):
    """Defines an interface for a collaboration request object"""
    
    user = Attribute('user', 'The name requested user')
    requestor = Attribute('requested', 'The name of the user who made the request')    
    roles = Attribute('roles', 'A sequence of the roles being requested for the specified user')
    object = Attribute('object', 'The ID of the object of the collboration request')
    container = Attribute('container', "The ID of the object's container")
    status = Attribute('status', "The status the request: pending, accepted, rejected")

    def setStatus(status):
        """Set the status of a request"""
    
    def performChanges():
        """Perform the requested changes to the object.  This is only valid in the 'accepted' state"""
    
    
