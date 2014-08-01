# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index() :
    images = db().select(db.image.ALL, orderby=db.image.title)
    return dict(images=images)


@auth.requires_login()
def show():
    #image = db.image(request.args(0,cast=int)) or redirect(URL('index'))
    image = db.image(request.args(0,cast=int,otherwise=URL('error')))
    db.post.image_id.default = image.id
    form = SQLFORM(db.post)
    if form.process().accepted:
        response.flash = 'your comment is posted'
    comments_posted = db(db.post.image_id==image.id).select()
    return dict(image=image, comments=comments_posted, form=form)
    

def user():
    return dict(form=auth())
    

def download():
    return response.download(request, db)
    
#################################################
    
#def index_counter() :
#    if not session.counter:
#        session.counter = 1
#    else:
#        session.counter += 1
#    return dict(message="Hello from MyApp", counter=session.counter)

#################################################
 
def first():
    if request.vars.visitor_name :
        msg1 = "Welcome back, " + request.vars.visitor_name + "!"
    else :
        msg1 = "Welcome!"
        
    msg2 = ""
    
    aForm = SQLFORM.factory(
        Field('visitor_name', label='Your name', requires=IS_NOT_EMPTY()),
        Field('password_attempt', label='Password'))   
        
    if request.vars.password_attempt :
        if request.vars.password_attempt == "hello" :
            session.password_okay = True
        else :
            msg2 = "Incorrect password, please try again."
            session.password_okay = False
    else :
        session.password_okay = False

    if aForm.process().accepted and session.password_okay :
        session.visitor_name = request.vars.visitor_name
        redirect(URL('second'))   
    #else :
    return dict(form = aForm, message1 = msg1, message2 = msg2)


def second() :
    if not session.password_okay or session.password_okay != True :
        msg2 = "NO PASSWORD!"
    else :
        msg2 = "You entered the correct password, thanks."
    return dict(message2 = msg2)