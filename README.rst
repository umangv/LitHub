======
LitHub
======

.. contents::

Installing LitHub
=================

Before you begin
----------------

You should ensure you have the following installed:

 - Python2 (preferably version 2.6 or newer)
 - Django 1.3 (if you like `virtualenv`, feel free to use it when developing)
 - django-registration - I'm currently using a slightly modified version of registration's hg tip. I'll update this file once I'm using pristine upstream source.
 - a supported database driver. If you don't which to use:

   - if you are contributing, always use **pysqlite2** (DB-API 2.0, for sqlite3 databases). You may already have this installed. 
   - for production, most servers have **MySQL** readily available, making MySQL a good choice
   - while you are free to choose any database you like, please do not change ``settings.py`` in git if you are contributing to LitHub. 


Installing LitHub for development
------------------------------------------------------------

  1. Copy ``lithub_config-example.py`` to ``lithub_config.py``
  2. Edit the ``LITHUB_ROOT`` variable so that it points to the directory in which your project exists
  3. Run ``python manage.py syncdb``. Note, however, that if the version of python you hope to use is different from the default python, you should use that instead.
  4. Run the development server using ``python manage.py runserver``
  5. The default link to your server should be ``http//:127.0.0.1:8000/``

Installing LitHub in production
--------------------------------

  1. Copy ``lithub_config-example.py`` to ``lithub_config.py``
  2. Edit the ``LITHUB_ROOT`` variable so that it points to the directory in which your project exists
  3. Reading, understanding and editing ``settings.py`` would be good idea at this point. You may not want to use the default settings. Ensure ``DEBUG`` is set to False. It may be a good idea to use a MySQL database.
  4. Run ``python manage.py syncdb``. 
  5. Edit the ``STATIC_ROOT`` variable if you want to and run ``python manage.py collectstatic``.
  6. In ``urls.py`` remove the following from the last line::

          + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

  7. Make your server point requests for ``STATIC_URL`` (default: '/static/') to ``STATIC_ROOT``.
  8. Use your preferred method of Django Deployment (mod_wsgi is easy and safe).

Contributing to LitHub
======================

Forking LitHub (First time)
---------------------------

All of LitHub's code is stored in a git repository at GitHub_. Once you get a git account and `configure git to work on GitHub`_, you can fork the project.

.. _GitHub: https://github.com/umangv/LitHub
.. _configure git to work on GitHub: http://help.github.com/set-up-git-redirect

You are now ready to clone your fork of your project::

     git clone git@github.com:username/LitHub.git

(replace *username* with your username, obviously)

Now you add an "upstream" remote, so that you have access to the latest code::

    cd LitHub
    git remote add upstream git://github.com/umangv/LitHub

Making changes
--------------

Remember: **always** make your changes in topic branches.

Begin by pulling merging the upstream master into your local ``master``::

    git checkout master
    git fetch upstream
    git merge upstream/master

Now make a topic branch::

    git checkout -b my-cool-new-feature

Do all your work in this branch. `Commit your changes often`_. While working on a topic branch, use rebase instead of merge to keep your code up to date (``git rebase upstream/master``).

.. _Commit your changes often: http://help.github.com/fork-a-repo/

Before pushing your changes, rebase with upstream master::

    git fetch upstream
    git rebase upstream/master

`Resolve`_ any conflicts that come up. You are ready to push changes to your GitHub repo!

.. _Resolve: http://book.git-scm.com/3_basic_branching_and_merging.html

::

    git push origin my-new-feature-local-branch-name:my-new-feature-remote-branch-name

(replace branch names with the correct and meaningful names)

You are now ready to make a pull request! Once your changes have been pulled, you may delete your remote branch.

Reminder: don't make any changes to your master branch. You should merge your master with upstream master often. Feel free to ask for help if you run into any trouble.

Copyright
=========

Copyright 2010, 2011 © Kalamazoo College Computer Science Club <kzoo-cs-board@googlegroups.com>

This file is part of LitHub.

LitHub is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

LitHub is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with LitHub.  If not, see <http://www.gnu.org/licenses/>.
