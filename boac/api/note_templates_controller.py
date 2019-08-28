"""
Copyright ©2019. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import get_note_attachments_from_http_post, get_note_topics_from_http_post
from boac.lib.http import tolerant_jsonify
from boac.lib.util import process_input_from_rich_text_editor
from boac.models.note_template import NoteTemplate
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/note_template/create', methods=['POST'])
@login_required
def create_note_template():
    params = request.form
    title = params.get('title', None)
    subject = params.get('subject', None)
    body = params.get('body', None)
    topics = get_note_topics_from_http_post()
    if not title or not subject:
        raise BadRequestError('Note creation requires \'subject\' and \'title\'')
    if current_user.is_admin or not len(current_user.dept_codes):
        raise ForbiddenRequestError('Sorry, Admin users cannot create advising notes')

    attachments = get_note_attachments_from_http_post(tolerate_none=True)

    note_template = NoteTemplate.create(
        creator_id=current_user.get_id(),
        title=title,
        subject=subject,
        body=process_input_from_rich_text_editor(body),
        topics=topics,
        attachments=attachments,
    )
    return tolerant_jsonify(note_template.to_api_json())


@app.route('/api/note_template/<note_template_id>')
@login_required
def get_note_template(note_template_id):
    note_template = NoteTemplate.find_by_id(note_template_id=note_template_id)
    if not note_template:
        raise ResourceNotFoundError('Template not found')
    if note_template.creator_id != current_user.get_id():
        raise ForbiddenRequestError(f'Template not available')
    return tolerant_jsonify(note_template.to_api_json())


@app.route('/api/note_templates/my')
@login_required
def get_my_note_templates():
    note_templates = NoteTemplate.get_templates_created_by(creator_id=current_user.get_id())
    return tolerant_jsonify([t.to_api_json() for t in note_templates])


@app.route('/api/note_template/update', methods=['POST'])
@login_required
def update_note_template():
    params = request.form
    note_template_id = params.get('id', None)
    subject = params.get('subject', None)
    if not subject:
        raise BadRequestError('Requires \'subject\'')
    body = params.get('body', None)
    topics = get_note_topics_from_http_post()
    delete_ids_ = params.get('deleteAttachmentIds') or []
    delete_ids_ = delete_ids_ if isinstance(delete_ids_, list) else str(delete_ids_).split(',')
    delete_attachment_ids = [int(id_) for id_ in delete_ids_]
    note_template = NoteTemplate.find_by_id(note_template_id=note_template_id)
    if not note_template:
        raise ResourceNotFoundError('Template not found')
    if note_template.creator_id != current_user.get_id():
        raise ForbiddenRequestError('Template not available.')
    note_template = NoteTemplate.update(
        note_template_id=note_template_id,
        subject=subject,
        body=process_input_from_rich_text_editor(body),
        topics=topics,
        attachments=get_note_attachments_from_http_post(tolerate_none=True),
        delete_attachment_ids=delete_attachment_ids,
    )
    return tolerant_jsonify(note_template.to_api_json())


@app.route('/api/note_template/delete/<note_template_id>', methods=['DELETE'])
@login_required
def delete_note_template(note_template_id):
    note_template = NoteTemplate.find_by_id(note_template_id=note_template_id)
    if not note_template:
        raise ResourceNotFoundError('Template not found')
    if note_template.creator_id != current_user.get_id():
        raise ForbiddenRequestError(f'Template not available')
    NoteTemplate.delete(note_template_id=note_template_id)
    return tolerant_jsonify({'message': f'Note template {note_template_id} deleted'}), 200
