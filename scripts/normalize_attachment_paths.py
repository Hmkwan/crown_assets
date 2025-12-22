"""Script to normalize chat attachment paths by resolving actual filesystem locations.

Usage:
    python scripts/normalize_attachment_paths.py --apply   # apply changes
    python scripts/normalize_attachment_paths.py --dry-run # just report
"""
import argparse
import logging
import os
from app import create_app, db
from app.chat_models import ChatAttachment

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def resolve_existing_path(path: str, app_root: str):
    if not path:
        return None
    # direct exists
    if os.path.exists(path):
        return path

    # relative path: try join with app_root
    try:
        candidate = os.path.join(app_root, path.lstrip(os.sep))
    except Exception:
        candidate = None
    if candidate and os.path.exists(candidate):
        return candidate

    # try common alternatives using basename and common subdirs (e.g., chat)
    basename = os.path.basename(path)
    for base in (os.path.join(app_root, 'uploads'), os.path.join(os.path.dirname(app_root), 'uploads')):
        # direct in base
        cand = os.path.join(base, basename)
        if os.path.exists(cand):
            return cand
        # common 'chat' subdir
        cand_chat = os.path.join(base, 'chat', basename)
        if os.path.exists(cand_chat):
            return cand_chat
        # try using the last folder name from the original path as a subdir
        orig_sub = os.path.basename(os.path.dirname(path))
        cand_sub = os.path.join(base, orig_sub, basename)
        if os.path.exists(cand_sub):
            return cand_sub

    # replace /app/app/uploads with /app/uploads and vice versa
    if path.startswith('/app/app/uploads'):
        alt = path.replace('/app/app/uploads', '/app/uploads')
        if os.path.exists(alt):
            return alt
    if path.startswith('/app/uploads'):
        alt = path.replace('/app/uploads', '/app/app/uploads')
        if os.path.exists(alt):
            return alt
    return None


def normalize_paths(app, apply_changes=False):
    changed = 0
    with app.app_context():
        app_root = app.root_path
        attachments = ChatAttachment.query.all()
        for att in attachments:
            updated = False
            # file_path
            resolved = resolve_existing_path(att.file_path, app_root)
            if resolved and resolved != att.file_path:
                logger.info(f"Would update file_path for attachment {att.id}: {att.file_path} -> {resolved}")
                if apply_changes:
                    att.file_path = resolved
                    updated = True
            # thumbnail_path
            resolved_thumb = resolve_existing_path(att.thumbnail_path, app_root)
            if resolved_thumb and resolved_thumb != att.thumbnail_path:
                logger.info(f"Would update thumbnail_path for attachment {att.id}: {att.thumbnail_path} -> {resolved_thumb}")
                if apply_changes:
                    att.thumbnail_path = resolved_thumb
                    updated = True
            if updated:
                if apply_changes:
                    db.session.add(att)
                # count potential change regardless of apply flag
                changed += 1
        if apply_changes and changed:
            db.session.commit()
            logger.info(f"Applied {changed} changes to attachments")
        else:
            logger.info(f"Dry run complete. Potential changes: {changed}")
    return changed


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Apply changes')
    args = parser.parse_args()

    app = create_app()
    if args.apply:
        logger.info('Applying normalization')
        normalize_paths(app, apply_changes=True)
    else:
        logger.info('Dry run (no changes will be applied)')
        normalize_paths(app, apply_changes=False)
