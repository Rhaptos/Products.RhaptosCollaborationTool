"""
Collaboration Manager for Rhaptos content

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import Acquisition
from AccessControl import getSecurityManager, ClassSecurityInfo

from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from Products.CMFCore.tests.base.security import OmnipotentUser

from DateTime import DateTime

_marker = None

# We must inherit from Acquisition for the security declarations to work
class CollaborationManager(Acquisition.Implicit):
    """Zope class for managing collaboration roles on an object"""

    security = ClassSecurityInfo()
    default_roles = ['Author', 'Maintainer', 'Licensor']
    default_role_names = {'Author':'Authors', 'Maintainer':'Maintainers', 'Licensor':'Copyright Holders'}

    def requestCollaboration(self, user, roles=_marker):
        """Set the roles for a user, if necessary making a collaboration request"""
        cur_user = getSecurityManager().getUser().getUserName()

        # If no roles specifed, default to all
        if roles == _marker:
            roles = {}
            roles = roles.fromkeys(self.default_roles,'add')

        # If user is the current user, just return
        if user == cur_user:
            self.setCollaborationRoles(user, roles)
        else:
            # Changing someone else's roles requires agreement
            id = self._getNextId()
            self.manage_addProduct['RhaptosCollaborationTool'].manage_addCollabRequest(id, user, cur_user, roles)
            

    def getPendingCollaborations(self):
        """Return a dictionary of pending collaboration requests for this module, mapping user -> collab request"""
        pending = {}
        for c in [o for o in self.objectValues('Collaboration Request') if o.status == 'pending']:
            pending[c.user] = c
        return pending

    def getCollaborators(self):
        """Returns a list of users contributing on this module (author, maintainer, etc.)"""
        return list(self.collaborators)

    def getCollabRolesForUser(self, user):
        """Return a list of collaboration roles for the specified user"""
        optional_roles = [r.lower()+'s' for r in getattr(self, 'optional_roles', {}).keys()]
        return [r.capitalize()[:-1] for r in ['authors', 'maintainers', 'licensors'] + optional_roles if user in getattr(self, r, [])]

    def getCollaborationRoles(self):
        """Return the sequence of collaboration roles"""
        if hasattr(self, 'optional_roles'):
            return self.default_roles + self.optional_roles.keys()
        else:
            return self.default_roles

    def updateRoleMetadata(self):
        """Update the metadata with the new roles"""
        # since _writeMetadata changes the target module's contents, and the button is pushed
        # by someone who may not have any editing permission on the object (in a personal Workspace, say)
        # we have to increase permission level in order to allow this.
        # FIXME: We shouldn't be doing this. It would be better if no change on the target was needed...
        
        # store old security manager, create a new powerful one
        oldmgr = getSecurityManager()
        user = OmnipotentUser()  #.__of__(self.portal_url.getPortalObject())
        newSecurityManager(self.REQUEST, user)
        
        # change the metadata section of the CNXML to reflect current roles
        self._writeMetadata()
        
        # restore old, normal, security manager
        setSecurityManager(oldmgr)

    def editCollaborationRequest(self, id, roles):
        """Change the roles on a collaboration request"""

        collab = self[id]
        collab.manage_changeProperties(roles=roles)

        self.updateRoleMetadata()

    def reverseCollaborationRequest(self, id):
        """Delete any the pending collaboration request and
        make the appropriate changes to the roles"""

        #pending = self.getPendingCollaborations()
        collab = self[id]
        u_id = collab.user
        collabs = self.getCollaborators()
        
        for r in collab.roles:
            role_name = r.lower() + 's'
            role = list(self[role_name])
        
            if collab.roles[r] == 'add':
                role.remove(u_id)
            elif collab.roles[r] == 'del':
                found = False
                for p_u in collabs[collabs.index(u_id)::-1]:
                    if p_u in role:
                        role.insert(role.index(p_u)+1,u_id)
                        found = True
                        break
                if not found:
                    role.insert(0,u_id)
            setattr(self,role_name,tuple(role))
            #self[role_name]=tuple(role)
            
        all_roles = {}
        for rolename in self.default_roles + getattr(self, 'optional_roles', {}).keys():
            all_roles.update({}.fromkeys(list(getattr(self, rolename.lower()+'s', []))))
            all_roles.update({}.fromkeys(list(getattr(self, 'pub_'+rolename.lower()+'s', []))))
        for c in collabs:
            if c not in all_roles.keys():
                self.removeCollaborator(c)
             
        self.updateRoleMetadata()

        self._p_changed = 1

    def addCollaborator(self, memberId):
        """Add a new user to the collaborators and set their new local roles"""
        try:
            collabs = self.getCollaborators()
        except AttributeError:
            collabs = []
            
        if memberId not in collabs:
            collabs.append(memberId)
            setattr(self, 'collaborators', tuple(collabs))

        self._p_changed = 1

    def removeCollaborator(self, memberId):
        """Remove a collaborator and set their new local roles"""
        try:
            collabs = self.getCollaborators()
        except AttributeError:
            collabs = []
        collabs.remove(memberId)
        setattr(self, 'collaborators', tuple(collabs))

        self._p_changed = 1

    def generateCollaborationRequests(self, newUser=False, newRoles={}, deleteRoles=[]):
        """Generate a dictionary of roles to send to a collaboration request"""
        user_role_delta = {}

        for r in self.getCollaborationRoles():

            role_name = r.lower() + 's'
            if not hasattr(self.aq_base, role_name):
                setattr(self, role_name, [])
            old_role = list(self[role_name])
            try:
                new_role = list(newRoles[r][:])
            except KeyError:
                new_role = []

            collabs = self.getCollaborators()

            if newUser:
                for new in new_role[:]:
                    if new not in user_role_delta:
                        user_role_delta[new]={}
                    user_role_delta[new][r] = 'add'
                    if new in collabs:
                        new_role.remove(new)
                new_role = old_role + new_role 
                    
            else:
                for old in old_role:
                    # If they want to delete the user, set all their roles to del and remove it from the list of new roles
                    if old in deleteRoles:
                        if old not in user_role_delta:
                            user_role_delta[old]={}
                        user_role_delta[old][r] = 'del'
                        new_role.remove(old)
                    # Else, look for differences
                    elif old not in new_role:
                        # old has been deleted
                        if old not in user_role_delta:
                            user_role_delta[old]={}
                        user_role_delta[old][r] = 'del'
            
                for new in new_role:
                    if new not in old_role:
                        # new has been added
                        if new not in user_role_delta:
                            user_role_delta[new]={}
                        user_role_delta[new][r] = 'add' 

            setattr(self,role_name,tuple(new_role))
             
        self.updateRoleMetadata()
            
        return user_role_delta

    def setCollaborationRoles(self, user, roles):
        """Do actual role setting"""
        collabs = list(self.collaborators)
        #import pdb; pdb.set_trace()
        for r in roles:
            role_name = 'pub_' + r.lower() + 's'
            if not hasattr(self.aq_base, role_name):
                setattr(self, role_name, [])

            if roles[r] == 'del':
                users = list(getattr(self.aq_base, role_name, ()))
                users.remove(user)
                setattr(self, role_name, tuple(users))

            elif roles[r] == 'add':
                users = list(getattr(self.aq_base, role_name, ()))
                found = False
                for p_u in collabs[collabs.index(user)::-1]:
                    if p_u in users:
                        users.insert(users.index(p_u)+1,user)
                        found = True
                        break
                if not found:
                    users.insert(0,user)
                setattr(self, role_name, tuple(users))

        all_roles = {}
        for rolename in self.default_roles + getattr(self, 'optional_roles', {}).keys():
            all_roles.update({}.fromkeys(list(getattr(self, rolename.lower()+'s', []))))
            all_roles.update({}.fromkeys(list(getattr(self, 'pub_'+rolename.lower()+'s', []))))
        for c in collabs:
            if c not in all_roles.keys():
                self.removeCollaborator(c)

        self._p_changed = 1
             
        self.updateRoleMetadata()

    def deleteCollaborationRequests(self):
        """Remove all collaboration requests for this object"""
        self.manage_delObjects(self.objectIds('Collaboration Request'))

    security.declarePrivate('_getNextId')
    def _getNextId(self):
        now=DateTime()
        id = 'Collab.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')
        count = 0
        while hasattr(self.aq_base, id):
            id = 'Collab.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%M%S')+'.'+str(count)
            count = count + 1
        return id
