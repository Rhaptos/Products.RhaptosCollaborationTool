"""
Basic Collaboration Tool

Author: Brent Hendricks
(C) 2003-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

"""
$Id$
"""

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import View, ManagePortal
from Products.ZCatalog.ZCatalog import ZCatalog
from CollaborationFolder import CollaborationFolder

from interfaces.portal_collaboration import portal_collaboration as ICollaborationTool


class CollaborationTool (UniqueObject, CollaborationFolder):
    """ This tool provides a way to request a collaboration with another user and allows them to accept or decline
    """
    __implements__ = ICollaborationTool

    id = 'portal_collaboration'
    meta_type = 'Collaboration Tool'
    _actions = ()

    security = ClassSecurityInfo()

    manage_options=( ( { 'label' : 'Overview'
                         , 'action' : 'manage_overview'
                         },
                       { 'label' : 'Catalog',
                         'action' : 'manage_catalog'
                         },
                       ) + CollaborationFolder.manage_options)

    #Define all the information needed for optional roles here:
    #The dictionary is keyed by the attribute that stores the role
    #The value is a tuple of the role name, the role display
    #name, and the byline for giving attribution for that role.
    #Note: The attribute name (key) is defined as:
    #role_name.lower()+'s'
    optional_role_info = {'editors':('Editor','Editors','Edited By'),
                          'translators':('Translator','Translators', 'Translated By')}

    def __init__(self):

        # Create the ZCatalog instance
        self.catalog = ZCatalog('catalog')
        self.catalog.addIndex('requester', 'FieldIndex')
        self.catalog.addIndex('status', 'FieldIndex')
        self.catalog.addIndex('user', 'FieldIndex')

        self.catalog.addColumn('requester')
        self.catalog.addColumn('roles')        
        self.catalog.addColumn('status')
        self.catalog.addColumn('user')
        self._p_changed=1

    #
    #   ZMI methods
    #
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('zpt/explainCollaborationTool', globals())

    def manage_catalog(self, REQUEST=None):
        """Access to the ZCatalog of objects"""
	if REQUEST is not None:
            REQUEST['RESPONSE'].redirect(self.catalog.absolute_url()+'/manage_catalogView')

InitializeClass(CollaborationTool)
