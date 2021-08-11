# -*- coding: utf-8 -*-

class MigrationRouter(object):

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        All non-auth models end up in this pool.
        """
        
        return bool(app_label == 'fk') !=  bool(db == 'default') # xor
