import { apiClient } from './axios'

export async function fetchGroups() {
  const { data } = await apiClient.get('/api/v1/all_groups')
  return data
}

export async function fetchResources() {
  const { data } = await apiClient.get('/api/v1/get_resources')
  return data
}

export async function fetchGroupResources(name: string) {
  const { data } = await apiClient.get(`/api/v1/get_resources/${encodeURIComponent(name)}`)
  return data
}

export async function deleteGroup(name: string) {
  const { data } = await apiClient.delete(`/api/v1/delete/${encodeURIComponent(name)}`)
  if (data.status === false) { throw new Error(data.content.message) }
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
  const { data } = await apiClient.get(`/api/v1/status/${encodeURIComponent(requestId)}`)
  return data
}

export async function submitForm(action: string, formData: FormData) {
  const { data } = await apiClient.post(action, formData)
  // console.log(data)
  if (data.status === false) { throw new Error(data.content.message) }
  return data
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
