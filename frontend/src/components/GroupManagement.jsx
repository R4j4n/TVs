// components/GroupManagement.jsx

import { useState, useEffect } from 'react';
import { Plus, Trash2, Settings } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { EditGroupModal } from './EditGroupModal';
import { getGroups, createGroup, deleteGroup, isDeviceInAnyGroup } from '@/lib/groupUtils';

export function CreateGroupModal({ availablePis, onClose, onGroupCreated }) {
  const [groupName, setGroupName] = useState('');
  const [selectedPis, setSelectedPis] = useState([]);
  const [error, setError] = useState('');

  const handleCreateGroup = async () => {
    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }
    if (selectedPis.length === 0) {
      setError('Please select at least one device');
      return;
    }

    try {
      const groupId = await createGroup(groupName, selectedPis);
      onGroupCreated();
      onClose();
    } catch (err) {
      setError('Failed to create group: ' + err.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
        <h2 className="text-xl font-bold mb-4">Create New Group</h2>
        
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Group Name</label>
            <input
              type="text"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              className="w-full p-2 border rounded"
              placeholder="Enter group name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Select Devices</label>
            <div className="max-h-48 overflow-y-auto border rounded p-2">
              {availablePis.map((pi) => (
                <label key={pi.host} className="flex items-center space-x-2 p-1">
                  <input
                    type="checkbox"
                    checked={selectedPis.some(selected => selected.host === pi.host)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPis([...selectedPis, pi]);
                      } else {
                        setSelectedPis(selectedPis.filter(selected => selected.host !== pi.host));
                      }
                    }}
                  />
                  <span>{pi.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button onClick={handleCreateGroup}>Create Group</Button>
          </div>
        </div>
      </div>
    </div>
  );
}

export function GroupCard({ group, groupId, onDelete, onEdit, onSelect }) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-xl font-bold">{group.name}</CardTitle>
        <div className="flex space-x-2">
          <Button variant="ghost" size="icon" onClick={onEdit}>
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={onDelete}>
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <p className="text-sm text-gray-500">
            {group.devices.length} device{group.devices.length !== 1 ? 's' : ''}
          </p>
          <div className="flex flex-wrap gap-2">
            {group.devices.map((device) => (
              <span
                key={device.host}
                className="px-2 py-1 bg-gray-100 rounded-full text-xs"
              >
                {device.name}
              </span>
            ))}
          </div>
          <Button 
            className="w-full mt-4"
            variant="default"
            onClick={() => onSelect(group)}
          >
            Control Group
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function GroupsList({ availablePis, onSelectGroup }) {
  const [groups, setGroups] = useState({});
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingGroup, setEditingGroup] = useState(null);
  const [editingGroupId, setEditingGroupId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchGroups = async () => {
    try {
      setLoading(true);
      const fetchedGroups = await getGroups();
      setGroups(fetchedGroups);
      setError(null);
    } catch (err) {
      setError('Failed to load groups');
      console.error('Error loading groups:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGroups();
  }, []);

  const handleGroupCreated = () => {
    fetchGroups();
  };

  const handleDeleteGroup = async (groupId) => {
    if (window.confirm('Are you sure you want to delete this group?')) {
      try {
        await deleteGroup(groupId);
        await fetchGroups(); // Refresh the groups list
      } catch (error) {
        console.error('Error deleting group:', error);
        setError('Failed to delete group');
      }
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading groups...</div>;
  }

  if (error) {
    return (
      <Alert variant="destructive" className="mb-4">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Device Groups</h2>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Group
        </Button>
      </div>

      {Object.keys(groups).length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          No groups created yet. Click "Create Group" to get started.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(groups).map(([groupId, group]) => (
            <GroupCard
              key={groupId}
              group={group}
              groupId={groupId}
              onDelete={() => handleDeleteGroup(groupId)}
              onEdit={() => {
                setEditingGroup(group);
                setEditingGroupId(groupId);
                setShowEditModal(true);
              }}
              onSelect={() => onSelectGroup(group)}
            />
          ))}
        </div>
      )}

      {showEditModal && (
        <EditGroupModal
          group={editingGroup}
          groupId={editingGroupId}
          availablePis={availablePis.filter(pi => 
            !isDeviceInAnyGroup(pi.host) || 
            editingGroup.devices.some(d => d.host === pi.host)
          )}
          onClose={() => {
            setShowEditModal(false);
            setEditingGroup(null);
            setEditingGroupId(null);
          }}
          onGroupUpdated={handleGroupCreated}
        />
      )}

      {showCreateModal && (
        <CreateGroupModal
          availablePis={availablePis}
          onClose={() => setShowCreateModal(false)}
          onGroupCreated={handleGroupCreated}
        />
      )}
    </div>
  );
}