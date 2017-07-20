# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, lurl
from tg import request, redirect, tmpl_context
from tg.i18n import ugettext as _
from tg.exceptions import HTTPFound
from tgsamplecontacts import model
from tgsamplecontacts.controllers.secure import SecureController
from tgsamplecontacts.model import DBSession
from tgext.admin.tgadminconfig import BootstrapTGAdminConfig as TGAdminConfig
from tgext.admin.controller import AdminController

from tgsamplecontacts.lib.base import BaseController
from tgsamplecontacts.controllers.error import ErrorController
from tgsamplecontacts.model.contact import Contact

__all__ = ['RootController']


def get_user_id():
    return request.identity['user'].user_id


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

    @expose('tgsamplecontacts.templates.contacts')
    def index(self):
        """Handle the front-page."""
        user_id = get_user_id()
        contacts = DBSession.query(Contact).filter_by(user_id=user_id).all()
        return dict(page='contacts', contacts=contacts)

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
        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)

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
