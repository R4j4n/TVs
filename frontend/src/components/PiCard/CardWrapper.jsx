// components/PiCard/CardWrapper.jsx
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import TVOnStatus from "./TVOnStatus";

export function CardWrapper({
  pi,
  title,
  status,
  error,
  tvStatus,
  onRefresh,
  isGroup = false,
  children,
}) {
  return (
    <Card
      className={`w-full drop-shadow-lg ${
        !status ? "bg-red-400/20" : ""
      } hover:drop-shadow-xl `}
    >
      <CardHeader className="space-y-1">
        <div className="flex items-center justify-between overflow-hidden">
          <CardTitle className="w-1/2 text-xl font-bold">
            {isGroup ? title : pi?.name}
          </CardTitle>
          {!isGroup && <TVOnStatus tvStatus={tvStatus} />}
          {status ? (
            <div className="w-1/4 text-center text-slate-200 justify-end h-100% px-4 py-1 rounded-full bg-emerald-600 transition-all ease-in duration-[1] ">
              Active
            </div>
          ) : (
            <div className="w-1/4 text-center text-slate-200 justify-end h-100% rounded-full px-4 py-1 bg-rose-600 transition-all ease-in duration-[1] ">
              Inactive
            </div>
          )}
          {onRefresh && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => onRefresh()}
              className="w-1/4"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </CardHeader>
      <CardContent className="space-y-4">{children}</CardContent>
    </Card>
  );
}