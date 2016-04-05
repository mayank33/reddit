# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
import datetime

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
#  response.flash = T("Welcome to web2py!")
#   return dict(message=T('Hello World'))
    redirect(URL('first'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
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
def first():
    d=db(db.Item.id>0).select(db.Item.ALL,orderby=~db.Item.ranks)
#  all_likes=db(db.likes.liked_by==auth.user_id).select(db.likes.ALL)
    return dict(d=d)#,all_likes=all_likes)
#@auth.requires_login()
def post():
    temp=request.args(0,cast=int)
    db.comment_item.Item_id.default=temp
    form=SQLFORM(db.comment_item)
    if form.process().accepted:
    	p=db(db.Item.id==temp).select(db.Item.count_comment)
    	db(db.Item.id==temp).update(count_comment=p[0]['count_comment']+1)
    	response.flash='You commented on this item'
    all_comments=db(db.comment_item.Item_id==temp).select(db.comment_item.ALL)
    cret_by=db(db.Item.id==temp).select(db.Item.created_by)
    all_likes=db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).select(db.likes.ALL)
    return dict(form=form,temp=temp,all_comments=all_comments,cret_by=cret_by,all_likes=all_likes)
@auth.requires_login()
def link():
    form=SQLFORM(db.Item)
    if form.process().accepted:
	response.flash='A new item is added'
    return dict(form=form)
def like():
    session.flash="You have like this link"
    temp=request.args(0,cast=int)
    myset=db(db.Item.id==temp)
    row=db(db.Item.id==temp).select(db.Item.ALL)
    new_dislike=row[0]['count_dislike']
    lis=db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).select(db.likes.ALL)
    if len(lis)==0:
    	db.likes.insert(Item_id=temp,liked_by=auth.user_id,flag_likes=2)
	new_like=row[0]['count_like']+1
    elif lis[0]['flag_likes']==2:#if like already present
    	db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).delete()#update(flag_likes=2)
	new_like=row[0]['count_like']-1
    else:
    	db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).update(flag_likes=2)
    	new_dislike=row[0]['count_dislike']-1
	new_like=row[0]['count_like']+1
    new_rnk=(-1*(new_dislike*3))+(new_like*5)
    myset.update(ranks=100+new_rnk,count_like=new_like,count_dislike=new_dislike)
    redirect(URL('first'))
def dislike():
    session.flash='You have dislike this link'
    temp=request.args(0,cast=int)
    lis=db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).select(db.likes.ALL)
    myset=db(db.Item.id==temp)
    row=db(db.Item.id==temp).select(db.Item.ALL)
    new_like=row[0]['count_like']
    if len(lis)==0:
    	db.likes.insert(Item_id=temp,liked_by=auth.user_id,flag_likes=1)
    	new_dislike=row[0]['count_dislike']+1
    elif lis[0]['flag_likes']==1:
    	db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).delete()#.update(flag_likes=1)
    	new_dislike=row[0]['count_dislike']-1
    else:	
    	db((db.likes.Item_id==temp)&(db.likes.liked_by==auth.user_id)).update(flag_likes=1)
    	new_dislike=row[0]['count_dislike']+1
	new_like-=1
    new_rnk=(-1*(new_dislike*3))+(new_like*5)
    myset.update(ranks=100+new_rnk,count_dislike=new_dislike,count_like=new_like)
    redirect(URL('first'))
def heading():
    temp=request.args(0,cast=int)
    st=db(db.categories.id==temp).select(db.categories.category)
    dic=db(db.Item.category==temp).select(db.Item.ALL,orderby=~db.Item.ranks)
    return dict(temp=temp,dic=dic,st=st)
def delete():
    temp=request.args(0,cast=int)
    read=db(db.comment_item.id==temp).select(db.comment_item.Item_id);
    db(db.Item.id==read[0]['Item_id']).update(count_comment=(db(db.Item.id==read[0]['Item_id']).select(db.Item.count_comment))[0]['count_comment']-1)
    db(db.comment_item.id==temp).delete()
    redirect(URL(post,args=read[0]['Item_id']))
def edit():
    temp=request.args(0,cast=int)
    read=db(db.comment_item.id==temp).select(db.comment_item.ALL);
    form=SQLFORM.factory(Field('changed','text',default=read[0]['comments']))
    if form.process().accepted:
	response.flash="You have changed the comment"
	db(db.comment_item.id==temp).update(comments=form.vars.changed,post=datetime.datetime.now)
    	redirect(URL(post,args=read[0]['Item_id']))
    return dict(form=form)
def edit_item():
    temp=request.args(0,cast=int)
    lis=db(db.Item.id==temp).select(db.Item.ALL)
    form=SQLFORM.factory(Field('category','string',default=lis[0]['category'],requires=IS_IN_DB(db,'categories.id','categories.category')),
	    		Field('heading','string',default=lis[0]['heading']),
			Field('url','string',default=lis[0]['url'],requires=IS_URL()),
			Field('video','string',default=lis[0]['video'],requires=IS_IN_SET(["yes","no"]))
	   		)
    if form.process().accepted:
    	db(db.Item.id==temp).update(category=request.vars.category,heading=request.vars.heading,url=request.vars.url)
    return dict(form=form)
def delete_item():
    temp=request.args(0,cast=int)
    db(db.Item.id==temp).delete()
    db(db.comment_item.Item_id==temp).delete()
    db(db.likes.Item_id==temp).delete()
    redirect(URL('first'))
def list():
    lis=db((db.auth_user.id>0)&(db.auth_user.id!=1)).select(db.auth_user.ALL)
    return dict(lis=lis)
def delete_user():
    temp=request.args(0,cast=int)
    db(db.auth_user.id==temp).delete()
    db(db.Item.created_by==temp).delete()
    db(db.comment_item.commented_by==temp).delete()
    db(db.likes.liked_by==temp).delete()
    redirect(URL('list'))
def categories():
    form=SQLFORM(db.categories)
    if form.process().accepted:
    	response.flash="category added"
    lis=db(db.categories.id>0).select(db.categories.ALL)
    return dict(lis=lis,form=form)
def user_list():
    temp=request.args(0,cast=int)
    d=db(db.Item.created_by==temp).select(db.Item.ALL)
    nam=db(db.auth_user.id==temp).select(db.auth_user.username)
    return dict(temp=temp,d=d,nam=nam)
def delete_cat():
    temp=request.args(0,cast=int)
    db(db.categories.id==temp).delete()
    lis=db(db.Item.category==temp).select(db.Item.id)
    for i in lis:
	db(db.comment_item.Item_id==i['id']).delete()
	db(db.likes.Item_id==temp).delete()
    db(db.Item.category==temp).delete()
    redirect(URL('categories'))
    
