// components/PiGrid.jsx
"use client";

import { useState, useEffect } from "react";
import { PiCard } from "./PiCard";
import { GroupsList } from "./GroupManagement";
import { GroupControl } from "./GroupControl";
import { fetchPis } from "@/lib/api";
import { isDeviceInAnyGroup, getGroups } from "@/lib/groupUtils";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";

export function PiGrid() {
  const [pis, setPis] = useState([]);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("individual");
  const [selectedGroup, setSelectedGroup] = useState(null);

  useEffect(() => {
    async function loadPis() {
      try {
        const result = await fetchPis(process.env.NEXT_PUBLIC_ACTIVE_SERVER_HOSTNAME);
        setPis(Array.isArray(result) ? result : Object.values(result));
      } catch (err) {
        console.error('Failed to fetch Pis:', err);
        setError('Failed to load Pis');
      }
    }

    loadPis();
    // Refresh every minute
    const interval = setInterval(loadPis, 60000);
    return () => clearInterval(interval);
  }, []);

  // Get ungrouped devices
  const ungroupedPis = pis.filter(pi => !isDeviceInAnyGroup(pi.host));

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="individual">Individual Devices</TabsTrigger>
          <TabsTrigger value="groups">Device Groups</TabsTrigger>
        </TabsList>

        <TabsContent value="individual" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {ungroupedPis.map((pi) => (
              <PiCard key={pi.host} pi={pi} />
            ))}
          </div>
          {ungroupedPis.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              No individual devices available. All devices are currently in groups.
            </div>
          )}
        </TabsContent>

        <TabsContent value="groups">
          {selectedGroup ? (
            <div className="space-y-4">
              <button
                onClick={() => setSelectedGroup(null)}
                className="text-blue-600 hover:underline mb-4"
              >
                ← Back to Groups
              </button>
              <GroupControl group={selectedGroup} />
            </div>
          ) : (
            <GroupsList
              availablePis={pis}
              onSelectGroup={(group) => {
                setSelectedGroup(group);
                console.log('Selected group:', group); // For debugging
              }}
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}