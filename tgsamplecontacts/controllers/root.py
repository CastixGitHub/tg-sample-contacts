# -*- coding: utf-8 -*-
"""Main Controller"""

import tg
from tg import expose, flash, lurl, validate
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _
from tg.exceptions import HTTPFound
from tgsamplecontacts import model
from tgsamplecontacts.controllers.secure import SecureController
from tgsamplecontacts.model import DBSession, User, Contact, Number
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from tgsamplecontacts.lib.base import BaseController
from tgsamplecontacts.controllers.error import ErrorController
from formencode import validators

__all__ = ['RootController']


def get_user_id():
    try:
        return request.identity['user'].user_id
    except:
        return None


class RootController(BaseController):
    """
    The root controller for the tg-sample-contacts application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()
    admin = AdminController(model, DBSession, config_type=TGAdminConfig)

    error = ErrorController()

    def _before(self, *args, **kw):
        tmpl_context.project_name = "tgsamplecontacts"

    @expose('json')
    def form_error_handler(self, **kwarg):
        errors = [{e[0]: e[1].args[0]}
                  for e in tg.tmpl_context.form_errors.items()]
        values = tg.tmpl_context.form_values
        print("errors: " + str(errors))
        print("values: " + str(values))
        return dict({'errors': errors, 'values': values})

    @expose('tgsamplecontacts.templates.form_error')
    def form_error(self, **kwargs):
        errors = [{e[0]: e[1].args[0]}
                  for e in tg.tmpl_context.form_errors.items()]
        values = tg.tmpl_context.form_values

        return dict(errors=errors, values=values)

    @expose('tgsamplecontacts.templates.contacts')
    def index(self):
        """Handle the front-page."""
        user_id = get_user_id()
        contacts = DBSession.query(Contact).filter_by(user_id=user_id).all()
        return dict(page='contacts', contacts=contacts)

    @expose('tgsamplecontacts.templates.new_contact')
    def new_contact(self):
        """render the page with the form for adding a new user"""
        return dict(page='new_contact')

    @expose()
    @validate(validators={'first_name': validators.String(max=80,
                                                          not_empty=True),
                          'last_name': validators.String(max=80),
                          'number': validators.Regex(r'^\+?[-0-9 ]{10,}$',
                                                     not_empty=True)},
              error_handler=form_error)
    def add_contact(self, first_name, last_name, number):
        contact = Contact()
        contact.first_name = first_name
        contact.last_name = last_name
        user = DBSession.query(User).filter_by(user_id=get_user_id()).one()
        contact.user = user
        n = Number()
        n.number = number
        n.contact = contact

        DBSession.add(n)
        DBSession.add(contact)
        redirect('/')

    @expose()
    def delete_contact(self, contact_id):
        """Deletes a single contact"""
        contact = DBSession.query(Contact).filter_by(id=contact_id).one()
        if contact.user_id == get_user_id():
            DBSession.query(model.Number).filter_by(contact_id=contact.id).\
                    delete()
            DBSession.delete(contact)
        redirect('/')

    @expose('json')
    def export(self):
        contacts = DBSession.query(Contact).\
                filter_by(user_id=get_user_id()).all()
        return {'contacts': contacts, 'user_id': get_user_id()}

    @expose('tgsamplecontacts.templates.login')
    def login(self, came_from=lurl('/'), failure=None, login=''):
        """Start the user login."""
        if failure is not None:
            if failure == 'user-not-found':
                flash(_('User not found'), 'error')
            elif failure == 'invalid-password':
                flash(_('Invalid Password'), 'error')

        login_counter = request.environ.get('repoze.who.logins', 0)
        if failure is None and login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from, login=login)

    @expose()
    def post_login(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ.get('repoze.who.logins', 0) + 1
            redirect('/login',
                     params=dict(came_from=came_from, __logins=login_counter))
        flash(_('Welcome back, %s!') % request.identity['user'].user_name)

        # Do not use tg.redirect with tg.url as it will add the mountpoint
        # of the application twice.
        return HTTPFound(location=came_from)

    @expose()
    def post_logout(self, came_from=lurl('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        return HTTPFound(location=came_from)
