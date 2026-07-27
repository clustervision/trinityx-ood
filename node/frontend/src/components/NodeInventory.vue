<!--
  This code is part of the TrinityX software suite
  Copyright (C) 2026  ClusterVision Solutions b.v.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>

  @author      Yixin Zhang
  @copyright   Copyright 2026, Luna2 Project[OOD]
  @license     GPL
  @version     2.0
  @maintainer  Yixin Zhang
  @email       yixin.zhang@clustervision.com
  @status      Development
-->

<template>
  <div class="tx-shell tx-inventory-page">
    <div v-if="errorMsg" class="alert alert-danger" role="alert">{{ errorMsg }}</div>

    <div class="tx-header">
      <h2 class="tx-title">Nodes</h2>
      <div class="tx-header-actions">
        <button type="button" class="tx-btn tx-btn-blue" @click="$emit('open-add')">Add Node</button>
        <button class="tx-btn tx-btn-help" title="Help" type="button" @click="helpOpen = true">?</button>
        <div class="tx-inline-search">
          <label class="tx-inline-search-label" for="txNodeSearch">Search:</label>
          <input
            id="txNodeSearch"
            v-model="searchQuery"
            type="search"
            class="tx-inline-search-input"
            autocomplete="off"
          />
        </div>
      </div>
    </div>

    <div class="tx-inventory-table-wrap">
      <table class="tx-inventory-table">
        <thead>
          <tr>
            <th
              v-for="(col, cIdx) in regularColumns"
              :key="col.field"
              rowspan="2"
              class="tx-th-regular"
              :class="{
                'tx-th-sep-blue': cIdx > 0,
                'tx-th-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1,
              }"
              :title="col.label"
              @click="toggleSort(col.field)"
            >
              <span class="tx-th-label-clip">{{ col.label }}</span>
              <span class="tx-sort-dt" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th v-if="hasInterfaces" colspan="3" rowspan="1" class="tx-iface-header-main">Interfaces</th>
            <th
              v-if="hasTpm"
              rowspan="2"
              class="tx-th-regular tx-th-tpm"
              :class="{
                'tx-th-sep-orange-left': hasInterfaces,
                'tx-th-sep-blue': !hasInterfaces && regularColumns.length > 0,
              }"
              title="TPM PRESENT"
              @click="toggleSort('tpm_present')"
            >
              <span class="tx-th-label-clip">{{ FIELD_LABELS.tpm_present || 'TPM PRESENT' }}</span>
              <span class="tx-sort-dt" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th
              rowspan="2"
              class="tx-th-regular tx-th-actions"
              :class="{
                'tx-th-sep-orange-right': hasInterfaces && !hasTpm,
                'tx-th-sep-blue': hasTpm || (!hasInterfaces && !hasTpm),
              }"
            >Actions</th>
          </tr>
          <tr v-if="hasInterfaces">
            <th class="tx-iface-sub tx-iface-sub-name" @click.stop="toggleSort('iface_name')">
              <span class="tx-th-label-clip">Name</span>
              <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th class="tx-iface-sub tx-iface-sub-mac" @click.stop="toggleSort('iface_mac')">
              <span class="tx-th-label-clip">MAC address</span>
              <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
            <th class="tx-iface-sub tx-iface-sub-ip" @click.stop="toggleSort('iface_ip')">
              <span class="tx-th-label-clip">IP address</span>
              <span class="tx-sort-dt tx-sort-dt-orange" aria-hidden="true">
                <svg width="10" height="14" viewBox="0 0 10 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 0L9.33 5H0.67L5 0Z" fill="currentColor" opacity="0.35" />
                  <path d="M5 14L0.67 9H9.33L5 14Z" fill="currentColor" opacity="0.35" />
                </svg>
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="totalColspan" style="text-align:center;padding:2rem;">Loading...</td>
          </tr>
          <tr v-else-if="pagedRows.length === 0">
            <td :colspan="totalColspan" style="text-align:center;padding:2rem;color:#999;">No nodes found.</td>
          </tr>
          <tr v-for="(row, idx) in pagedRows" :key="(row.name || '') + '-' + idx">
            <td
              v-for="(col, cIdx) in regularColumns"
              :key="col.field"
              :class="{
                'tx-td-sep-blue': cIdx > 0,
                'tx-td-sep-before-iface': hasInterfaces && cIdx === regularColumns.length - 1,
              }"
            >
              <template v-if="col.field === 'name'">
                <button
                  type="button"
                  class="tx-name-link"
                  :title="displayNameTitle(row.name)"
                  @click="$emit('open-edit', canonicalName(row.name))"
                >
                  <span class="tx-cell-ellipsis tx-cell-truncate-js">{{ formatDisplayName(row.name) }}</span>
                </button>
              </template>
              <template v-else-if="col.field === 'osimage'">
                <span v-if="isInvalidOs(row)" class="tx-os-invalid">!!Invalid!!</span>
                <span v-else-if="isEmpty(row[col.field])" class="tx-na-box">NOT AVAILABLE</span>
                <span
                  v-else
                  class="tx-cell-ellipsis tx-cell-truncate-js"
                  :title="displayNameTitle(row[col.field])"
                >{{ formatDisplayName(row[col.field]) }}</span>
              </template>
              <template v-else-if="col.field === 'setupbmc'">
                <span :class="setupbmcClass(row[col.field])">{{ setupbmcLabel(row[col.field]) }}</span>
              </template>
              <template v-else-if="isEmpty(row[col.field])">
                <span class="tx-na-box">NOT AVAILABLE</span>
              </template>
              <template v-else>
                <span class="tx-cell-ellipsis" :title="cellText(row[col.field])">{{ cellText(row[col.field]) }}</span>
              </template>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-name tx-td-iface-edge">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'n-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="String(iface.interface || '')"
              >{{ iface.interface || '' }}</div>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-mac tx-td-iface-between">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'m-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="String(iface.macaddress || '')"
              >{{ iface.macaddress || '' }}</div>
            </td>
            <td v-if="hasInterfaces" class="tx-iface-cell tx-iface-ip tx-td-iface-edge-ip">
              <div
                v-for="(iface, iIdx) in (row.interfaces || [])"
                :key="'p-' + iIdx"
                class="tx-iface-entry tx-cell-ellipsis"
                :title="ifaceIp(iface)"
              >{{ ifaceIp(iface) }}</div>
            </td>
            <td
              v-if="hasTpm"
              class="tx-td-tpm"
              :class="{
                'tx-td-sep-orange-left': hasInterfaces,
                'tx-td-sep-blue': !hasInterfaces && regularColumns.length > 0,
              }"
            >
              <span :class="tpmClass(row.tpm_present)">{{ tpmLabel(row.tpm_present) }}</span>
            </td>
            <td
              class="tx-col-actions"
              :class="{
                'tx-td-sep-orange-right': hasInterfaces && !hasTpm,
                'tx-td-sep-blue': !hasTpm && !hasInterfaces,
              }"
            >
              <div class="tx-action-icons">
                <button
                  type="button"
                  class="tx-icon-act tx-icon-clone"
                  title="Clone"
                  @click="$emit('open-clone', canonicalName(row.name))"
                >
                  <img :src="actionIcons.clone" alt="Clone" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-osgrab"
                  title="Grab OS Image"
                  @click="$emit('open-osgrab', canonicalName(row.name))"
                >
                  <img :src="actionIcons.osgrab" alt="Grab OS Image" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-ospush"
                  title="OS Push"
                  @click="$emit('open-ospush', canonicalName(row.name))"
                >
                  <img :src="actionIcons.ospush" alt="OS Push" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
                </button>
                <button
                  type="button"
                  class="tx-icon-act tx-icon-danger"
                  title="Delete"
                  @click="$emit('open-delete', canonicalName(row.name))"
                >
                  <img :src="actionIcons.delete" alt="Delete" width="28" height="28"
                    onerror="this.style.display='none';this.nextElementSibling.style.display='inline'"
                  />
                  <svg style="display:none" viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="tx-table-footer">
      <div class="tx-page-length-box">
        <select v-model.number="pageSize">
          <option v-for="n in pageSizeOptions" :key="n" :value="n">{{ n }}</option>
        </select>
        <span class="tx-page-length-label">Entries per Page</span>
      </div>
      <div class="tx-paging">
        <button
          type="button"
          class="tx-paging-arrow"
          :disabled="currentPage <= 1"
          aria-label="Previous page"
          @click="currentPage--"
        >&lt;</button>
        <span class="tx-paging-current">{{ pageLabel }}</span>
        <button
          type="button"
          class="tx-paging-arrow"
          :disabled="currentPage >= totalPages"
          aria-label="Next page"
          @click="currentPage++"
        >&gt;</button>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="helpOpen" class="tx-modal-overlay" @mousedown.self="helpOpen = false">
        <div class="tx-help-dialog" role="dialog" aria-labelledby="help-title-node">
          <button type="button" class="tx-modal-x" aria-label="Close" @click="helpOpen = false">&times;</button>

          <h2 id="help-title-node" class="tx-help-title">Node management help</h2>

          <h3 class="tx-help-section-title">What this app does</h3>
          <ul class="tx-help-list">
            <li><strong>Purpose</strong>: This page manages Luna nodes. A node is a machine known to Luna, usually a compute node, login node, service node, or another system that can be provisioned, configured, cloned, or removed.</li>
            <li><strong>Scope</strong>: The GUI focuses on Luna <strong>node</strong> operations: list, add, edit, clone, delete, OS Grab, OS Push, and interface management.</li>
            <li><strong>Inheritance</strong>: Some values may come directly from the node, while others may be inherited from a group, OS image, or default Luna configuration. When the UI shows a label such as <strong>NODE</strong>, <strong>GROUP</strong>, <strong>OS IMAGE</strong>, or <strong>DEFAULT</strong>, it indicates where the displayed value currently comes from.</li>
            <li><strong>Saving</strong>: Changes are only applied after clicking <strong>Add Node</strong>, <strong>Save Changes</strong>, or <strong>Clone Node</strong>. Editing a field in the dialog alone does not change Luna until the form is submitted.</li>
          </ul>

          <h3 class="tx-help-section-title">Main page</h3>
          <ul class="tx-help-list">
            <li><strong>Add Node</strong>: Opens the dialog for creating a new Luna node.</li>
            <li><strong>Search</strong>: Filters the node table as you type. It searches the visible node data, including names and common node fields.</li>
            <li><strong>Sort</strong>: Click a column header to sort. Click the same header again to reverse the order.</li>
            <li><strong>Name</strong>: The Luna node name. The name is used as the node identifier in Luna commands and API calls.</li>
            <li><strong>Group</strong>: The node group. Groups are commonly used to share configuration such as OS image, provisioning settings, scripts, roles, interfaces, and defaults across multiple nodes.</li>
            <li><strong>OS Image</strong>: The OS image assigned to the node. This determines what image is used when the node is provisioned or synchronised.</li>
            <li><strong>BMC Setup</strong>: The BMC setup profile linked to the node. This profile normally contains BMC access and channel settings used during BMC configuration.</li>
            <li><strong>Setup BMC</strong>: Shows whether BMC setup is enabled, disabled, or inherited. This controls whether Luna should configure the node BMC when provisioning or applying configuration.</li>
            <li><strong>Status</strong>: The current node status when Luna provides one. If no status is available, the table may show <em>NOT AVAILABLE</em> or an empty value.</li>
            <li><strong>TPM</strong>: Shows TPM-related state when available. TPM fields are used only when the environment uses TPM-based node admission or identity checks.</li>
            <li><strong>Interfaces</strong>: Shows interface name, MAC address, IP address, and DHCP state where available. Interface columns can be sorted by interface name, MAC address, or IP address.</li>
            <li><strong>Actions</strong>: Opens node actions: clone, OS Grab, OS Push, or delete.</li>
            <li><strong>Entries per Page</strong>: Controls how many nodes are displayed on one page. Use the page controls to move through the node list.</li>
          </ul>

          <h3 class="tx-help-section-title">Add node</h3>
          <ul class="tx-help-list">
            <li><strong>Name</strong>: Unique Luna node name. Use a predictable name, for example <code>node001</code>. Avoid spaces. The name is the primary identifier used by Luna.</li>
            <li><strong>Group</strong>: Select the group the node should belong to. A group can provide inherited defaults such as OS image, scripts, provisioning method, and interfaces.</li>
            <li><strong>OS Image</strong>: Select the image assigned to this node. If set at node level, it overrides the inherited OS image from the group.</li>
            <li><strong>Net Boot</strong>: Controls whether the node should use network boot. <strong>YES</strong> enables Luna/PXE/iPXE-style booting. <strong>NO</strong> disables it for the node. <strong>INHERITED</strong> keeps the value from the parent configuration.</li>
            <li><strong>Setup BMC</strong>: Controls whether Luna should configure the node BMC. <strong>TRUE</strong> enables BMC setup, <strong>FALSE</strong> disables it, and <strong>DEFAULT</strong> keeps the inherited/default value.</li>
            <li><strong>BMC Setup</strong>: Selects the BMC setup profile. This is normally where BMC username, user ID, management channel, network channel, and related BMC defaults are defined.</li>
            <li><strong>Switch</strong>: Optional switch name associated with the node. Use this when Luna tracks physical switch placement.</li>
            <li><strong>Switch Port</strong>: Optional port on the selected switch where the node is connected.</li>
            <li><strong>Vendor</strong>: Optional vendor or hardware vendor label. This is useful for inventory and support context.</li>
            <li><strong>Scripts</strong>: Optional Luna script plugin list or script reference. Scripts are used during provisioning and configuration.</li>
            <li><strong>Roles</strong>: Optional Luna role plugin list or role reference. Roles are used to apply reusable configuration behaviour to a node.</li>
            <li><strong>+ Interfaces</strong>: Expands the interface section so that BOOTIF, BMC, bonded interfaces, VLANs, IP addresses, and MAC addresses can be configured.</li>
            <li><strong>Advanced</strong>: Expands less frequently changed fields such as kernel options, provisioning settings, scripts, TPM identity fields, service flag, and comments.</li>
          </ul>

          <h3 class="tx-help-section-title">Edit node</h3>
          <ul class="tx-help-list">
            <li><strong>Save Changes</strong>: Writes the changed node values back to Luna.</li>
            <li><strong>Rename</strong>: In edit mode, the node name can be changed using the rename control next to the name field. A rename changes the Luna node identifier, so confirm the new name carefully.</li>
            <li><strong>No changes to save</strong>: If nothing changed compared with the loaded form, the app will not submit an update.</li>
            <li><strong>Removing a value</strong>: Some fields must be submitted as an explicit empty value to clear them in Luna. Script fields such as pre, part, and post script are handled this way by the GUI.</li>
            <li><strong>Removing an interface</strong>: Removing an interface row in the form only changes the dialog until <strong>Save Changes</strong> is clicked. On save, the interface removal is sent to Luna.</li>
            <li><strong>Inherited values</strong>: If a value reappears after clearing it, it may be inherited from a group, OS image, or default configuration. Check the source label beside the field where available.</li>
          </ul>

          <h3 class="tx-help-section-title">Clone node</h3>
          <ul class="tx-help-list">
            <li><strong>Clone Name</strong>: Name for the new node. It must be unique and must not be the same as the source node.</li>
            <li><strong>Copied values</strong>: Clone starts with values from the source node, then lets you adjust the new node before creating it.</li>
            <li><strong>Interfaces</strong>: Existing interface definitions are copied, but the GUI can prefill the next available IP address so the clone does not reuse the source node IP.</li>
            <li><strong>MAC addresses</strong>: Review MAC address fields before cloning. Reusing a MAC address on two nodes can break provisioning, DHCP, or network identity.</li>
            <li><strong>IP addresses</strong>: Review IP fields before cloning. The new node should not use the same IP addresses as the source node.</li>
            <li><strong>Clone Node</strong>: Creates the new Luna node using the source node and the adjusted clone fields.</li>
          </ul>

          <h3 class="tx-help-section-title">Interfaces</h3>
          <ul class="tx-help-list">
            <li><strong>Interface</strong>: Luna interface name, for example <code>BOOTIF</code>, <code>BMC</code>, <code>eth0</code>, or another site-defined name. <code>BOOTIF</code> is commonly used for provisioning or boot networking. <code>BMC</code> is commonly used for management controller access.</li>
            <li><strong>Network</strong>: Luna network assigned to this interface, for example a cluster network, IPMI network, management network, or provisioning network.</li>
            <li><strong>IP Address</strong>: IPv4 address assigned to the interface. For clone, this should normally be a new free IP, not the source node IP.</li>
            <li><strong>NEXT IP</strong>: Finds and fills the next available IPv4 address for the selected network, based on the inventory data available to the GUI.</li>
            <li><strong>MAC Address</strong>: Hardware MAC address for the interface. For provisioning and DHCP workflows, this should match the real interface MAC address.</li>
            <li><strong>MTU</strong>: Maximum Transmission Unit. Valid range is 68 to 65535. Use the network-standard MTU unless jumbo frames or special network tuning is required.</li>
            <li><strong>DHCP</strong>: Enables or disables DHCP behaviour for this interface. When enabled, the interface may receive an address through DHCP rather than using a fixed address, depending on Luna/network configuration.</li>
            <li><strong>Bond Mode</strong>: Bonding mode used when multiple physical interfaces are combined into one logical interface. Only set this when the network design uses Linux bonding.</li>
            <li><strong>Bond Member</strong>: Physical member interfaces used by the bond, for example interfaces that belong to a bonded BOOTIF or data interface.</li>
            <li><strong>VLAN ID</strong>: VLAN tag ID for tagged networking. Use only when the interface should be placed on a VLAN.</li>
            <li><strong>VLAN Parent</strong>: Parent interface for a VLAN interface. For example, a VLAN interface may be based on a physical interface or bond.</li>
            <li><strong>Options</strong>: Extra interface options. Use this for advanced interface-specific configuration that does not fit the standard fields.</li>
            <li><strong>Remove Interface</strong>: Removes the row from the form. In edit mode, the removal is applied only after saving.</li>
            <li><strong>+ Add</strong>: Adds another interface row below the current one.</li>
          </ul>

          <h3 class="tx-help-section-title">Advanced fields</h3>
          <ul class="tx-help-list">
            <li><strong>Domain</strong>: DNS domain related to the node. In many Luna environments this is inherited from cluster or group configuration.</li>
            <li><strong>Unmanaged BMC Users</strong>: How Luna should treat unmanaged BMC users — leave empty (skip), <code>disable</code>, or <code>delete</code>.</li>
            <li><strong>Asset Tag</strong>: Optional inventory asset tag. Useful for mapping Luna nodes to hardware labels, CMDB records, or support contracts.</li>
            <li><strong>Cloud Name</strong>: Optional cloud or cloud profile association when Luna cloud-related configuration is used.</li>
            <li><strong>Kernel Options</strong>: Kernel command-line options used during boot or provisioning. Common examples include network naming or BIOS device naming options. The source label shows whether the current value comes from node, group, OS image, or default configuration.</li>
            <li><strong>Pre Script</strong>: Script content or script reference run early in the provisioning process, before the main image or partitioning steps, depending on Luna configuration.</li>
            <li><strong>Part Script</strong>: Partitioning script used during provisioning. This normally controls disk layout or partition creation. Be careful: wrong partitioning logic can destroy data.</li>
            <li><strong>Post Script</strong>: Script run after the image or core provisioning steps. Often used for final configuration, package changes, mounts, service setup, or site-specific tweaks.</li>
            <li><strong>Upload</strong>: Loads script or text content from a local text file into the field.</li>
            <li><strong>Expand editor</strong>: Opens a larger editor for long scripts, comments, kernel options, or interface options.</li>
            <li><strong>Provision Interface</strong>: Interface used for provisioning traffic. <code>BOOTIF</code> is a common value.</li>
            <li><strong>Provision Method</strong>: Method used by Luna to provision or transfer image data. The environment may use methods such as torrent or HTTP depending on cluster configuration.</li>
            <li><strong>Provision Fallback</strong>: Fallback method if the primary provisioning method is unavailable or unsuitable.</li>
            <li><strong>OS Image Tag</strong>: Optional OS image tag. Tags can be used to select a specific image variant or version when the OS image supports tags.</li>
            <li><strong>TPM UUID</strong>: TPM identity UUID when TPM-based node validation is used.</li>
            <li><strong>TPM Pubkey</strong>: TPM public key used for node identity or attestation workflows.</li>
            <li><strong>TPM SHA256</strong>: SHA256 fingerprint or digest associated with TPM validation.</li>
            <li><strong>Service</strong>: Marks the node as a service node when applicable. This is site-specific and should be used only when the node has a service role.</li>
            <li><strong>Comment</strong>: Free-text note for administrators. Use it for operational context, not for secrets or passwords.</li>
          </ul>

          <h3 class="tx-help-section-title">Source labels and inheritance</h3>
          <ul class="tx-help-list">
            <li><strong>NODE</strong>: The value is set directly on the node and overrides inherited configuration.</li>
            <li><strong>GROUP</strong>: The value is inherited from the node group.</li>
            <li><strong>OS IMAGE</strong>: The value is inherited from the selected OS image or image tag.</li>
            <li><strong>DEFAULT</strong>: The value comes from Luna defaults or another default configuration level.</li>
            <li><strong>Why this matters</strong>: Clearing a node-level value may reveal an inherited value after reload. That does not always mean the clear failed. It may mean Luna fell back to the next available configuration source.</li>
            <li><strong>Override behaviour</strong>: Setting a value directly on a node usually makes it a node-level override. Removing or clearing the node value may return the field to inherited behaviour.</li>
          </ul>

          <h3 class="tx-help-section-title">OS Grab</h3>
          <ul class="tx-help-list">
            <li><strong>Purpose</strong>: OS Grab captures the state of a running node into an OS image. Use it when a node has been prepared manually or updated and you want that state reflected in an image.</li>
            <li><strong>Node</strong>: Target node to grab from. This is the source of the captured state.</li>
            <li><strong>OS Image</strong>: Destination image name. The grabbed state is associated with this image.</li>
            <li><strong>Bare</strong>: Grabs a bare OS image and excludes packing behaviour where supported. Use this only when you specifically need the bare image workflow.</li>
            <li><strong>No Dry</strong>: Runs the real operation. When not selected, the workflow may run as a dry-run or validation-only action, depending on the backend behaviour.</li>
            <li><strong>When to use</strong>: Use OS Grab after validating a node configuration that should become reusable for other nodes.</li>
            <li><strong>Caution</strong>: Make sure the node state is clean before grabbing. Temporary files, local changes, credentials, or test data may become part of the captured image if not excluded.</li>
          </ul>

          <h3 class="tx-help-section-title">OS Push</h3>
          <ul class="tx-help-list">
            <li><strong>Purpose</strong>: OS Push deploys or synchronises an OS image to a node. It is used to push image changes from Luna to the selected node.</li>
            <li><strong>Node</strong>: Target node that will receive the image push.</li>
            <li><strong>OS Image</strong>: Image to push to the node. Confirm this carefully before running a live push.</li>
            <li><strong>No Dry</strong>: Runs the real push. If this is not selected, the operation may be a dry-run or validation-only action, depending on the backend behaviour.</li>
            <li><strong>When to use</strong>: Use OS Push when an image has changed and a node must be updated or synchronised from that image.</li>
            <li><strong>Caution</strong>: A live OS Push can modify the node. Make sure the selected node and image are correct before enabling <strong>No Dry</strong>.</li>
          </ul>

          <h3 class="tx-help-section-title">Delete node</h3>
          <ul class="tx-help-list">
            <li><strong>Delete</strong>: Removes the node from Luna configuration.</li>
            <li><strong>Permanent action</strong>: Deletion cannot be undone from this dialog. Recreating a deleted node requires adding it again or restoring configuration from elsewhere.</li>
            <li><strong>Before deleting</strong>: Confirm the node name, check whether it is still in use, and verify that removing it will not affect provisioning, monitoring, or operational workflows.</li>
          </ul>

          <h3 class="tx-help-section-title">Practical guidance</h3>
          <ul class="tx-help-list">
            <li><strong>Use inheritance where possible</strong>: Put common values on groups or OS images. Use node-level overrides only for node-specific differences.</li>
            <li><strong>Be careful with scripts</strong>: Pre, part, and post scripts can change the node filesystem and provisioning behaviour. Check them before saving.</li>
            <li><strong>Review clone network data</strong>: A cloned node should have unique IP addresses and MAC addresses.</li>
            <li><strong>Prefer dry-run first</strong>: For OS Grab and OS Push, leave <strong>No Dry</strong> unchecked first when you want to verify what would happen before running the real operation.</li>
            <li><strong>Do not store secrets in comments</strong>: Comments are for operational notes, not passwords, tokens, or private keys.</li>
          </ul>

          <p class="tx-help-note">Press <strong>Esc</strong> or click outside the help panel to close it.</p>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { fetchNodes } from '../api'
import { displayNameTitle, formatDisplayName } from '../constants/displayName'
import { actionIcons } from '../utils/assetImg'
import { parseIpv4String } from '../utils/nextFreeIpv4'
import type { NodeRow, NodeInventoryInterface, ColumnDef, InventoryIpv4Record } from '@/types'

defineEmits<{
  'open-add': []
  'open-edit': [name: string]
  'open-clone': [name: string]
  'open-ospush': [name: string]
  'open-osgrab': [name: string]
  'open-delete': [name: string]
}>()

const FIELD_LABELS: Record<string, string> = {
  name: 'NAME',
  group: 'GROUP',
  osimage: 'OS IMAGE',
  osimagetag: 'OS IM. TAG',
  setupbmc: 'SETUP BMC',
  bmcsetup: 'BMC SETUP',
  status: 'STATUS',
  tpm_present: 'TPM PRESENT',
}

const fields = ref<string[]>([])
const nodes = ref<NodeRow[]>([])
const loading = ref(true)
const errorMsg = ref('')
const searchQuery = ref('')
const sortField = ref('')
const sortAsc = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)
const pageSizeOptions = [10, 25, 50, 100]
const helpOpen = ref(false)

const hasInterfaces = computed(() => fields.value.includes('interfaces'))
const hasTpm = computed(() => fields.value.includes('tpm_present'))

const regularColumns = computed((): ColumnDef[] => {
  return fields.value
    .filter((f) => f !== 'interfaces' && f !== 'tpm_present')
    .map((f) => ({
      field: f,
      label: FIELD_LABELS[f] || f.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
    }))
})

const totalColspan = computed((): number => {
  let count = regularColumns.value.length + 1
  if (hasInterfaces.value) count += 3
  if (hasTpm.value) count += 1
  return count
})

const pageLabel = computed(() => String(currentPage.value))

function canonicalName(displayName: unknown): string {
  return String(displayName || '').replace(/\s+\*$/, '').trim()
}

function cellText(val: unknown): string {
  if (val == null) return ''
  if (typeof val === 'object') {
    try { return JSON.stringify(val) } catch { return String(val) }
  }
  return String(val)
}

function isEmpty(val: unknown): boolean {
  if (val == null) return true
  if (typeof val === 'string' && val.trim() === '') return true
  if (Array.isArray(val) && val.length === 0) return true
  return false
}

function ifaceIp(iface: NodeInventoryInterface | null): string {
  if (!iface || typeof iface !== 'object') return ''
  const parts: string[] = []
  if (iface.ipaddress) parts.push(String(iface.ipaddress))
  if (iface.ipaddress_ipv6) parts.push(String(iface.ipaddress_ipv6))
  if (iface.dhcp === true) parts.push('[DHCP]')
  return parts.join(' ') || ''
}

function isInvalidOs(row: NodeRow): boolean {
  const v = row.osimage
  if (v != null && typeof v === 'string' && /invalid/i.test(v)) return true
  return false
}

function setupbmcLabel(val: unknown): string {
  if (val === true || val === 'true' || val === 'True') return 'YES'
  if (val === false || val === 'false' || val === 'False') return 'NO'
  const s = val != null ? String(val).toLowerCase() : ''
  if (s.includes('inherit')) return 'INHERITED'
  return cellText(val) || '—'
}

function setupbmcClass(val: unknown): string {
  const s = val != null ? String(val).toLowerCase() : ''
  if (s.includes('inherit')) return 'tx-pill tx-pill-inherited'
  if (val === true || val === 'true' || val === 'True') return 'tx-pill tx-pill-yes'
  if (val === false || val === 'false' || val === 'False') return 'tx-pill tx-pill-no'
  return 'tx-pill tx-pill-no'
}

function tpmLabel(val: unknown): string {
  if (val === true || val === 'true' || val === 'True') return 'TRUE'
  if (val === false || val === 'false' || val === 'False') return 'FALSE'
  return cellText(val) || '—'
}

function tpmClass(val: unknown): string {
  if (val === true || val === 'true' || val === 'True') return 'tx-pill tx-pill-true'
  if (val === false || val === 'false' || val === 'False') return 'tx-pill tx-pill-false'
  return 'tx-pill tx-pill-false'
}

function ifaceSortKey(row: NodeRow, key: string): string {
  const list = row.interfaces || []
  if (key === 'ip') {
    return list
      .map((item) => ifaceIp(item).toLowerCase())
      .join('\u0001')
  }
  return list
    .map((item) => String((item && (item as Record<string, unknown>)[key]) || '').toLowerCase())
    .join('\u0001')
}

function rowMatchesSearch(row: NodeRow, q: string): boolean {
  let keys = fields.value.filter((f) => f !== 'interfaces')
  if (keys.length === 0) {
    keys = Object.keys(row).filter((k) => k !== 'interfaces')
  }
  return keys.some((key) => {
    const val = row[key]
    if (val == null) return false
    if (typeof val === 'string') return val.toLowerCase().includes(q)
    if (typeof val === 'boolean' || typeof val === 'number') {
      return String(val).toLowerCase().includes(q)
    }
    if (Array.isArray(val)) return false
    return String(val).toLowerCase().includes(q)
  })
}

const filteredRows = computed((): NodeRow[] => {
  let rows = nodes.value
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    rows = rows.filter((row) => rowMatchesSearch(row, q))
  }
  if (sortField.value) {
    const sf = sortField.value
    const asc = sortAsc.value
    rows = [...rows].sort((a, b) => {
      let va: string
      let vb: string
      if (sf === 'iface_name') {
        va = ifaceSortKey(a, 'interface')
        vb = ifaceSortKey(b, 'interface')
      } else if (sf === 'iface_mac') {
        va = ifaceSortKey(a, 'macaddress')
        vb = ifaceSortKey(b, 'macaddress')
      } else if (sf === 'iface_ip') {
        va = ifaceSortKey(a, 'ip')
        vb = ifaceSortKey(b, 'ip')
      } else {
        va = a[sf] != null ? String(a[sf]).toLowerCase() : ''
        vb = b[sf] != null ? String(b[sf]).toLowerCase() : ''
      }
      if (va < vb) return asc ? -1 : 1
      if (va > vb) return asc ? 1 : -1
      return 0
    })
  }
  return rows
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value)))

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

watch(searchQuery, () => { currentPage.value = 1 })
watch(pageSize, () => { currentPage.value = 1 })
watch([filteredRows, totalPages], () => {
  if (currentPage.value > totalPages.value) currentPage.value = Math.max(1, totalPages.value)
})

function toggleSort(field: string) {
  if (sortField.value === field) {
    sortAsc.value = !sortAsc.value
  } else {
    sortField.value = field
    sortAsc.value = true
  }
}

async function loadData() {
  loading.value = true
  errorMsg.value = ''
  try {
    const data = await fetchNodes()
    if (data.error) errorMsg.value = data.error
    fields.value = data.fields || []
    nodes.value = data.nodes || []
  } catch (err) {
    errorMsg.value = (err as Error).message || 'Network error while loading nodes.'
  } finally {
    loading.value = false
  }
}

function collectInventoryIpv4Records(): InventoryIpv4Record[] {
  const out: InventoryIpv4Record[] = []
  for (const row of nodes.value) {
    const name = canonicalName(row.name)
    for (const iface of row.interfaces || []) {
      const ipNum = parseIpv4String(iface.ipaddress)
      if (ipNum == null) continue
      out.push({
        nodeName: name,
        network: String(iface.network || ''),
        ipNum,
      })
    }
  }
  return out
}

function handleEscKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && helpOpen.value) {
    helpOpen.value = false
  }
}

defineExpose({ loadData, collectInventoryIpv4Records })

onMounted(() => {
  loadData()
  window.addEventListener('keydown', handleEscKey)
})
onUnmounted(() => {
  window.removeEventListener('keydown', handleEscKey)
})
</script>
