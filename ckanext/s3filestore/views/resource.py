# encoding: utf-8

import logging

import flask

from ckan.plugins.toolkit import config, asbool
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload

from . import resource_download, filesystem_resource_download

log = logging.getLogger(__name__)

Blueprint = flask.Blueprint


def _get_package_types():
    """Return configured package types, defaulting to ['dataset']."""
    raw = config.get('ckanext.s3filestore.package_types', 'dataset')
    types = [t.strip() for t in raw.split(',') if t.strip()]
    return types or ['dataset']


def _create_blueprint(package_type):
    """Create an S3 resource download blueprint for a single package type."""
    bp = Blueprint(
        u's3_resource_{}'.format(package_type),
        __name__,
        url_prefix=u'/{}/<id>/resource'.format(package_type),
        url_defaults={u'package_type': package_type}
    )

    if not hasattr(DefaultResourceUpload, 'download'):
        bp.add_url_rule(u'/<resource_id>/download',
                        view_func=resource_download)
        bp.add_url_rule(u'/<resource_id>/download/<filename>',
                        view_func=resource_download)

    bp.add_url_rule(u'/<resource_id>/fs_download/<filename>',
                    view_func=filesystem_resource_download)

    if not asbool(config.get('ckanext.s3filestore.use_filename', False)):
        bp.add_url_rule(
            u'/<resource_id>/orig_download/<filename>', view_func=resource_download
        )

    return bp


def get_blueprints():
    return [_create_blueprint(pt) for pt in _get_package_types()]
