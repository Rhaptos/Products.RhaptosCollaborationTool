from Products.CMFCore.utils import getToolByName

def migrateCollabRequestsToDictionaries(self):
    """Change every collaboration request from a list to a dictionary"""
    
    portal = getToolByName(self, 'portal_url').getPortalObject()
    
    for wg in portal.GroupWorkspaces.objectValues() + portal.Members.objectValues(['Plone Folder']):
        for o in wg.objectValues(['Collection','Module Editor']):
            if not o.state == 'published':
                collab = []
                collabs = o.getPendingCollaborations()
                new_collabs = {}
               
                for p in ['Author','Licensor','Maintainer']:
                    role_name = p.lower()+'s'
                    role = list(getattr(o, role_name, ()))
                    pub_rn = 'pub_' + role_name
                    
                    setattr(o, pub_rn, tuple(role))
                    for c in collabs:
                        if c not in new_collabs:
                            new_collabs[c] = {}
                            
                        if p in collabs[c].roles:
                            if c not in role:
                                role.append(c)
                                new_collabs[c][p]='add'
                        else:
                            if c in role:
                                role.remove(c)
                                new_collabs[c][p]='del' 
                    setattr(o, role_name, tuple(role))
                    
                for u in list(o.authors) + list(o.maintainers) + list(o.licensors):
                    o.addCollaborator(u)
                    
                for x in collabs:
                    if type(collabs[x].roles) != type({}):
                        collabs[x].roles= new_collabs[x]

    for cr in portal.portal_collaboration.searchCollaborations()[:]:
        req = cr.getObject()
        if (req.status == 'accepted') or (req.status == 'rejected'):
            par = req.aq_parent
            
            par.manage_delObjects(req.id)

    portal.portal_collaboration.catalog.refreshCatalog()
    
