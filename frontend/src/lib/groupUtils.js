// lib/groupUtils.js

// Group structure in localStorage:
// {
//   groupId: {
//     name: string,
//     devices: Array<{name: string, host: string}>,
//     createdAt: number
//   }
// }

export function getGroups() {
    const groups = localStorage.getItem('piGroups');
    return groups ? JSON.parse(groups) : {};
  }
  
  export function saveGroups(groups) {
    localStorage.setItem('piGroups', JSON.stringify(groups));
  }
  
  export function createGroup(name, devices) {
    const groups = getGroups();
    const groupId = `group_${Date.now()}`;
    
    groups[groupId] = {
      name,
      devices,
      createdAt: Date.now()
    };
    
    saveGroups(groups);
    return groupId;
  }
  
  export function updateGroup(groupId, updates) {
    const groups = getGroups();
    
    if (groups[groupId]) {
      groups[groupId] = {
        ...groups[groupId],
        ...updates
      };
      saveGroups(groups);
      return true;
    }
    return false;
  }
  
  export function deleteGroup(groupId) {
    const groups = getGroups();
    
    if (groups[groupId]) {
      delete groups[groupId];
      saveGroups(groups);
      return true;
    }
    return false;
  }
  
  export function addDeviceToGroup(groupId, device) {
    const groups = getGroups();
    
    if (groups[groupId]) {
      const devices = groups[groupId].devices;
      if (!devices.some(d => d.host === device.host)) {
        devices.push(device);
        saveGroups(groups);
        return true;
      }
    }
    return false;
  }
  
  export function removeDeviceFromGroup(groupId, deviceHost) {
    const groups = getGroups();
    
    if (groups[groupId]) {
      groups[groupId].devices = groups[groupId].devices.filter(
        d => d.host !== deviceHost
      );
      saveGroups(groups);
      return true;
    }
    return false;
  }
  
  export function isDeviceInAnyGroup(deviceHost) {
    const groups = getGroups();
    return Object.values(groups).some(group => 
      group.devices.some(device => device.host === deviceHost)
    );
  }