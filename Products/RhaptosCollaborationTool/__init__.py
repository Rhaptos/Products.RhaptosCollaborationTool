"""
Initialize RhaptosCollaborationTool Product

Author: Brent Hendricks
(C) 2003-2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

from Products.CMFCore.utils import ToolInit
from CollaborationTool import CollaborationTool
import CollaborationFolder

def initialize(context):

    context.registerClass(CollaborationFolder.CollaborationFolder,
                          constructors=(CollaborationFolder.manage_addCollaborationFolderForm,
                                        CollaborationFolder.manage_addCollaborationFolder),
                          icon="www/collabfolder.gif")
                          
    context.registerClass(CollaborationFolder.CollabRequest,
                          permission="CollaborationFolder: Add Collaboration",
                          constructors=(CollaborationFolder.manage_addCollabRequestForm,
                                        CollaborationFolder.manage_addCollabRequest),
                          icon="www/collabrequest.gif")
    
    ToolInit( meta_type='Collaboration Tool'
              , tools=( CollaborationTool, )
              , icon="tool.gif"
              ).initialize( context )


