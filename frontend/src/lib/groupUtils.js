// lib/groupUtils.js

const API_BASE_URL = process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME;

// Helper function to get the base URL
function getBaseUrl() {
  // If it's a complete URL (like from zrok), use it as is
  if (API_BASE_URL.startsWith('http://') || API_BASE_URL.startsWith('https://')) {
    return API_BASE_URL;
  }
  // For local development, add the protocol and port
  return `http://${API_BASE_URL}:7777`;
}

export async function getGroups() {
  try {
    const response = await fetch(`${getBaseUrl()}/groups`);
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