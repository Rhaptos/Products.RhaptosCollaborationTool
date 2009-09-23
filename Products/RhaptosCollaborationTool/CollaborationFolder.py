"""
CollaborationFolder.py - Zope Collaboration tool

Author: Brent Hendricks
(C) 2003-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Products.ZCatalog.CatalogPathAwareness import CatalogAware
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import getSecurityManager, ClassSecurityInfo
import zLOG

### Contructors for Collaboration Request objects
manage_addCollabRequestForm = PageTemplateFile('zpt/manage_addCollabRequestForm', globals())
                                               
                                               
def manage_addCollabRequest(self, id, user, requester, roles, REQUEST=None):
    """Creates a new CollabRequest object 'id' with the contents of 'file'"""

    id=str(id)
    if not id:
        raise "Bad Request", "Please specify an ID."

    self=self.this()
    self._setObject(id, CollabRequest(id, user, requester, roles))

    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect(self.absolute_url()+'/manage_main')


class CollabRequest(CatalogAware, SimpleItem, PropertyManager):
    """CollabRequest"""

    default_catalog = "portal_collaboration"
    meta_type = "Collaboration Request"
    security = ClassSecurityInfo()
    _properties=({'id':'user', 'type': 'string', 'mode': 'w'},
                 {'id':'requester', 'type': 'string', 'mode': 'w'},
                 {'id':'roles', 'type': 'lines', 'mode': 'w'},
                 {'id':'status', 'type': 'string', 'mode': 'w'},
                 )       
 
    manage_options=(
        PropertyManager.manage_options
        + SimpleItem.manage_options
        )

    def __init__(self, id, user, requester, roles):
        """CollabRequest constructor"""
        self.id = id
        self.user = user
        self.requester = requester
        self.roles = roles
        self.status = 'pending'

    def setStatus(self, status):
        """Set the status of a request"""
        self.status = status
        if status == 'accepted':
            self.performChanges()
        if status == 'rejected':
            self.aq_parent.reverseCollaborationRequest(self.id)
        self.reindex_object()
    
    def performChanges(self):
        """Perform the requested changes to the object.  This is only valid in the 'accepted' state"""
        self.aq_parent.setCollaborationRoles(self.user, self.roles)

    # Overload manage_changeProperties to do re-indexing
    def manage_editProperties(self, REQUEST):
        """Change properties from ZMI"""
        result = PropertyManager.manage_editProperties(self, REQUEST)
        self.reindex_object()
        return result

    def manage_changeProperties(self, REQUEST=None, **kw):
        result = PropertyManager.manage_changeProperties(self, REQUEST, **kw)
        self.reindex_object()
        return result


##     def reindex_object(self):
##         """ Suprisingly useful """
##         zLOG.LOG("CollabFolder", zLOG.INFO, "Eliminating request %s because %s is not %s" % (requestObj.id, requestObj.user, user))
##         self.unindex_object()
##         self.index_object()




### Contructors for Collaboration Folder Objects
manage_addCollaborationFolderForm = PageTemplateFile("zpt/manage_addCollaborationFolderForm", globals())
                                        
def manage_addCollaborationFolder(self, id, REQUEST=None):
    """Add a new CollaborationFolder object."""

    id = str(id)
    if not id:
        raise "Bad Request", "Please specify an ID."

    self = self.this()
    self._setObject(id, CollaborationFolder(id))

    if REQUEST is not None:
        REQUEST["RESPONSE"].redirect(self.absolute_url()+"/manage_main")


class CollaborationFolder(Folder):
    """Collaboration Folder"""
    
    meta_type = "Collaboration Folder"

    security = ClassSecurityInfo()

    def __init__(self, id):
        """CollaborationFolder Constructor"""
        self.id = id

    security.declarePublic('addCollabRequest')
    def searchCollaborations(self, **kw):
        """Find collaboration requests with the specified parameters"""
        return self.catalog.searchResults(**kw)
    
    security.declarePrivate('catalog_object')
    def catalog_object(self, object, id):
        self.catalog.catalog_object(object, id)

    security.declarePrivate('uncatalog_object')
    def uncatalog_object(self, id):
        self.catalog.uncatalog_object(id)


InitializeClass(CollabRequest)
InitializeClass(CollaborationFolder)
