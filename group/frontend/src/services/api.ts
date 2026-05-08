import { apiClient } from './axios'

export async function fetchGroups() {
  const { data } = await apiClient.get('/api/v1/all_groups')
  return data
}

export async function fetchResources() {
  const { data } = await apiClient.get('/api/v1/get_resources')
  return data
}

export async function deleteGroup(name: string) {
  // const data = {content: {message: `Group ${name} is removed.`}, status: true, status_code: 204}
  const { data } = await apiClient.delete(`/api/v1/delete/${encodeURIComponent(name)}`)
   if (data.status === false) { throw new Error(data.content.message) }
  return data
}

export async function fetchEditData(name: string) {
  const { data } = await apiClient.get(`/edit/${encodeURIComponent(name)}?format=json`)
  return data
}

export async function fetchAddData() {
  const { data } = await apiClient.get('/add?format=json')
  return data
}

export async function fetchCloneData(name: string) {
  const { data } = await apiClient.get(`/clone/${encodeURIComponent(name)}?format=json`)
  return data
}

export async function fetchOspushData(name: string) {
  const { data } = await apiClient.get(`/ospush/${encodeURIComponent(name)}?format=json`)
  return data
}

export async function removeInterface(
  record: string,
  iface: string
) {
  const { data } = await apiClient.get(`/remove/${encodeURIComponent(record)}/${encodeURIComponent(iface)}`)

  if (data.status !== 'success') {
    throw new Error(data.message || 'Remove interface failed')
  }

  return data
}

export async function checkStatus(requestId: string) {
  const { data } = await apiClient.get(`/check_status/config/status/${encodeURIComponent(requestId)}`)
  return data
}

export async function submitForm(
  action: string,
  formData: FormData
) {
  const { data, status } = await apiClient.post(action, formData)
  return { ok: status >= 200 && status < 300, status, data }
}

export async function submitRename(
  record: string,
  newName: string
) {
  const fd = new FormData()
  fd.append('name', record)
  fd.append('newname', newName)

  return submitForm(`/rename/${encodeURIComponent(record)}`, fd)
}
