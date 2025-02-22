// lib/groupUtils.js
import { getBaseUrl } from './api';  // Import getBaseUrl from api.js

export async function getGroups() {
  try {
    const response = await fetch(`${getBaseUrl()}/groups`, {
      headers: {
        'skip_zrok_interstitial': '1'
      }
    });
    if (!response.ok) {
      throw new Error('Failed to fetch groups');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching groups:', error);
    return {};
  }
}

export async function createGroup(name, devices) {
  try {
    const response = await fetch(`${getBaseUrl()}/groups`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'skip_zrok_interstitial': '1'
      },
      body: JSON.stringify({ name, devices }),
    });

    if (!response.ok) {
      throw new Error('Failed to create group');
    }

    const result = await response.json();
    return result.id;
  } catch (error) {
    console.error('Error creating group:', error);
    throw error;
  }
}

export async function updateGroup(groupId, updates) {
  try {
    const response = await fetch(`${getBaseUrl()}/groups/${groupId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'skip_zrok_interstitial': '1'
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error('Failed to update group');
    }

    return true;
  } catch (error) {
    console.error('Error updating group:', error);
    return false;
  }
}

export async function deleteGroup(groupId) {
  try {
    const response = await fetch(`${getBaseUrl()}/groups/${groupId}`, {
      method: 'DELETE',
      headers: {
        'skip_zrok_interstitial': '1'
      }
    });

    if (!response.ok) {
      throw new Error('Failed to delete group');
    }

    return true;
  } catch (error) {
    console.error('Error deleting group:', error);
    return false;
  }
}

export async function isDeviceInAnyGroup(deviceHost) {
  try {
    const groups = await getGroups();
    return Object.values(groups).some(group => 
      group.devices.some(device => device.host === deviceHost)
    );
  } catch (error) {
    console.error('Error checking device group membership:', error);
    return false;
  }
}