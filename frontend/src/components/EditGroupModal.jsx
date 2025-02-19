// components/EditGroupModal.jsx
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import * as GroupUtils from '@/lib/groupUtils';

export function EditGroupModal({ group, groupId, availablePis, onClose, onGroupUpdated }) {
  const [groupName, setGroupName] = useState(group.name);
  const [selectedPis, setSelectedPis] = useState(group.devices);
  const [error, setError] = useState('');

  const handleUpdateGroup = () => {
    if (!groupName.trim()) {
      setError('Please enter a group name');
      return;
    }
    if (selectedPis.length === 0) {
      setError('Please select at least one device');
      return;
    }

    GroupUtils.updateGroup(groupId, {
      name: groupName,
      devices: selectedPis
    });
    
    onGroupUpdated();
    onClose();
  };

  // Get all available devices including current group devices
  const allDevices = [...availablePis, ...group.devices].reduce((unique, device) => {
    const exists = unique.find(d => d.host === device.host);
    if (!exists) {
      unique.push(device);
    }
    return unique;
  }, []);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-96">
        <h2 className="text-xl font-bold mb-4">Edit Group</h2>
        
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
              {allDevices.map((device) => (
                <label key={device.host} className="flex items-center space-x-2 p-1">
                  <input
                    type="checkbox"
                    checked={selectedPis.some(selected => selected.host === device.host)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedPis([...selectedPis, device]);
                      } else {
                        setSelectedPis(selectedPis.filter(selected => 
                          selected.host !== device.host
                        ));
                      }
                    }}
                  />
                  <span>{device.name}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onClose}>Cancel</Button>
            <Button onClick={handleUpdateGroup}>Update Group</Button>
          </div>
        </div>
      </div>
    </div>
  );
}