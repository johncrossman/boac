import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'
import store from '@/store'
import Vue from 'vue'

export function getMyNoteTemplates() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_templates/my`)
    .then(response => response.data, () => null)
}

export function getNoteTemplate(templateId: number) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/note_template/${templateId}`)
    .then(response => response.data, () => null)
}

export function createNoteTemplate(
    title: string,
    subject: string,
    body: string,
    topics: string[],
    attachments: any[]
) {
  const data = {title, subject, body, topics}
  _.each(attachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_template/create', data).then(template => {
    store.dispatch('noteEditSession/onCreateTemplate', template)
    const uid = Vue.prototype.$currentUser.uid
    Vue.prototype.$ga.noteTemplateEvent(template.id, `Advisor ${uid} created a note template`, 'create')
    return template
  })
}

export function deleteNoteTemplate(templateId: number) {
  return axios
    .delete(`${utils.apiBaseUrl()}/api/note_template/delete/${templateId}`)
    .then(() => store.dispatch('noteEditSession/onDeleteTemplate', templateId))
}

export function renameNoteTemplate(noteTemplateId: number, title: string) {
  const data = {id: noteTemplateId, title: title}
  return axios.post(`${utils.apiBaseUrl()}/api/note_template/rename`, data).then(response => {
    const template = response.data
    store.dispatch('noteEditSession/onUpdateTemplate', template)
    const uid = Vue.prototype.$currentUser.uid
    Vue.prototype.$ga.noteTemplateEvent(noteTemplateId, `Advisor ${uid} renamed a note template`, 'update')
    return template
  })
}

export function updateNoteTemplate(
    noteTemplateId: number,
    subject: string,
    body: string,
    topics: string[],
    newAttachments: any[],
    deleteAttachmentIds: number[]
) {
  const data = {
    id: noteTemplateId,
    subject: subject,
    body: body,
    topics: topics,
    deleteAttachmentIds: deleteAttachmentIds || []
  }
  _.each(newAttachments || [], (attachment, index) => data[`attachment[${index}]`] = attachment)
  return utils.postMultipartFormData('/api/note_template/update', data).then(template => {
    store.dispatch('noteEditSession/onUpdateTemplate', template)
    const uid = Vue.prototype.$currentUser.uid
    Vue.prototype.$ga.noteTemplateEvent(noteTemplateId, `Advisor ${uid} updated a note template`, 'update')
    return template
  })
}
