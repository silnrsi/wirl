# -*- coding: utf-8 -*-

##################################################################################
#
#   Copyright (c) 2014 SIL International
#
#   The WIRL software is released under the MIT License
#   (http://opensource.org/licenses/MIT).
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#   
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#   
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
#   SOFTWARE.
#
##################################################################################



##  Top level pages  ##

def index() :
    redirect(URL('editor'))
    
    
def editor() :
    response.subtitle = T('Resource Editor')
    
    print "--------------- editor ------------------"
    
    #print session
    
    #resultDict = dict()
    
    print "get_vars=", request.get_vars
    print "post_vars=",request.post_vars
    
    idToEdit = request.get_vars.id
    prevId = request.get_vars.prevId
    print "idToEdit=",idToEdit
    #resultDict['idToEdit'] = idToEdit
    
    resultDict = _display_form(idToEdit,prevId)
    
    # Kludge: pull the form-key out of the generated SQLFORM
#    temp = resultDict['sqlForm']
#    temp = temp.__str__()
#    pos = temp.find("_formkey")
#    pos2 = temp.find("value=", pos)
#    pos3 = temp.find('"', pos2 + 8)
#    temp2 = temp[pos2+7:pos2+43]
#    resultDict['fkey'] = temp2

    sortBy = request.get_vars.sortby
    if sortBy == None :
        sortBy = "resourceId"
    rows = db().select(db.langResource.ALL, orderby=db.langResource[sortBy])
    
    #for row in rows :
    #    print row.id, row.resourceId
    resultDict['rows'] = rows
    resultDict['sortby'] = sortBy or ""
    
    print "resultDict=", resultDict
    
    return resultDict


# Generate and process the form that allows adding, editing, or deleting.
def _display_form(idToEdit, prevId) :
    
    print "display_form:",idToEdit
    
    langResourceKeys = db.langResource.fields()
    print langResourceKeys
    
    if idToEdit :
        record = db.langResource(idToEdit)
        sqlForm = SQLFORM(db.langResource, record)
    else :
        sqlForm = SQLFORM(db.langResource)
        
    pendingDict = dict()
    for key in langResourceKeys :
        pendingDict[key] = ""
    hasErrors = False
       
    fAccepted = sqlForm.process().accepted
    print "fAccepted=",fAccepted

    #if idToEdit :
    #    sessionKey = '_formkey[langResource/' + str(idToEdit) + ']'
    #else :
    #    sessionKey = '_formkey[langResource/created]'
    #keyList = session[sessionKey]
    #print "keyList["+sessionKey+"]", keyList
    
    if sqlForm.errors:
        print "errors: ",sqlForm.errors
        response.flash = 'Form has errors.'
        for key in langResourceKeys :
            pendingDict[key] = request.post_vars[key]
        hasErrors = True
        prevId = None
        hiPrev = False
        
    elif idToEdit and fAccepted :
        print "resource modified"
        response.flash = 'Resource modified.'
        # Re-create the Add controls.
        sqlForm = SQLFORM(db.langResource)
        prevId = idToEdit
        hiPrev = True
        idToEdit = None
        
    elif fAccepted :
        print "new resource added"
        response.flash = 'New resource added.'
        prevId = None
        # Figure out the ID of the new resource.
        rows = db().select(db.langResource.ALL, orderby=db.langResource.id)
        lastRow = rows[len(rows) - 1]
        prevId = lastRow.id
        hiPrev = True
        
    else :
        print "no processing yet"
        response.flash = 'Add a new resource.'
        # PrevId might possibly be a record that was canceled out of, so retain it.
        hiPrev = False
        
    #print "sqlForm=",sqlForm
    formkey = sqlForm.formkey if hasattr(sqlForm, "formkey") else None
    #print "formkey=",formkey
    
    if idToEdit == "" : idToEdit = None
    
    resultDict = dict()
    resultDict['sqlForm'] = sqlForm
    resultDict['fkey'] = formkey
    resultDict['idToEdit'] = idToEdit
    resultDict['hasErrors'] = hasErrors
    resultDict['pending'] = pendingDict
    resultDict['prevId'] = prevId
    resultDict['hiPrev'] = hiPrev
    
    return resultDict


# Ask for confirmation before deleting a resource.
def deleteOne() :
    response.subtitle = T('Resource Editor')
    
    idToDelete = request.vars.id
    rowsToDelete = db(db.langResource.id == idToDelete).select()

    return dict(row = rowsToDelete[0])
    
    
# Go ahead and delete the resource.
def deleteOneConfirmed() :
    idToDelete = request.vars.id
    # delete it
    db(db.langResource.id == idToDelete).delete()
    
    redirect(URL('editor'))

def td_errorMsg(string) :
    return '<td class=\"err\"><div>' + string + "</div></td>"
    
    
###############################################################

def user() :
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download() :
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call() :
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data() :
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
