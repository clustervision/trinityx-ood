/*
 * This code is part of the TrinityX software suite
 * Copyright (C) 2026  ClusterVision Solutions b.v.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * @author      Yixin Zhang
 * @copyright   Copyright 2026, Luna2 Project[OOD]
 * @license     GPL
 * @version     2.0
 * @maintainer  Yixin Zhang
 * @email       yixin.zhang@clustervision.com
 * @status      Development
 */

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

export async function removeInterface(record: string, iface: string) {
  const { data } = await apiClient.get(
    `/api/v1/remove-interface/${encodeURIComponent(record)}/${encodeURIComponent(iface)}`
  )

  if (data.status === false || data.status === 'false') {
    const message =
      typeof data.content === 'object' && data.content?.message
        ? data.content.message
        : 'Remove interface failed'
    throw new Error(message)
  }

  return data
}

export async function checkStatus(requestId: string) {
  const { data } = await apiClient.get(`/api/v1/status/${encodeURIComponent(requestId)}`)
  return data
}

export async function submitForm(action: string, formData: FormData | Record<string, any>) {
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
